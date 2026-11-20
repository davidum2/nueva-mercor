## Objective
- Add native value-based `RANGE` window framing to Druid in `/app`: a new `WindowFrame.Range` type, frame resolution in the native window engine, and SQL validator/Calcite planning support, so single-key numeric/timestamp offset `RANGE` frames work end-to-end while unsupported forms (multi-key, non-numeric keys) keep failing.

## Important Details
- `WindowFrame.Range` must be a public nested class of `WindowFrame`, registered as Jackson subtype `"range"`, with `@Nullable Double lowerOffset`, `@Nullable Double upperOffset`, non-null `ColumnWithDirection orderBy`; getters `getLowerOffset()`, `getUpperOffset()`, `getOrderBy()`; static factory `WindowFrame.range(@Nullable Double, @Nullable Double, ColumnWithDirection)`; must not extend `OffsetFrame`; equals/hashCode by value, `toString`, Jackson ser/de.
- `WindowFrame` already maps `"rows"`→`Rows`, `"groups"`→`Groups`; `WindowFrame.unbounded()` = `rows(null, null)`.
- `FramedOnHeapAggregatable#aggregateAll`, `WindowFramedAggregateProcessor`, `WindowFirstProcessor`, `WindowLastProcessor` must accept `Range`.
- Offset semantics (final): signed distances — PRECEDING negative, FOLLOWING positive, `CURRENT ROW` = 0.0, null = UNBOUNDED (positional, partition edge, includes NULL rows).
- Bound value: `v + o` when ASC, `v - o` when DESC; frame is the closed interval between lower and upper bound.
- Resolution algorithm (final): ASC → frameStart = first row with value >= lowerBound, frameEnd (exclusive) = first row with value > upperBound; DESC → frameStart = first row with value <= lowerBound, frameEnd = first row with value < upperBound; search restricted to non-null region (nulls sort first ASC / last DESC since `compareRows` returns -1 for null lhs, multiplied by direction for DESC).
- NULL current row: finite bounds resolve to the boundaries of the contiguous NULL run (its peer group); unbounded bounds stay positional (0 / numRows).
- Peers (equal keys) get identical bounds/output — compute per peer group via `ClusteredGroupPartitioner.fromRAC(rac).computeBoundaries([orderByColumn])` (nulls form one peer group since `compareRows(null,null)==0`).
- Empty frames: aggregation path already handles empty `Interval` via `AggIntervalCursor.moveTo` → fresh aggregators → zero-row default (verified existing empty-rows-frame behavior); `FIRST_VALUE`/`LAST_VALUE` return null when frameStart >= frameEnd.
- Value comparisons in double space via `accessor.getDouble(row)`; accepted precision caveat beyond 2^53 (offsets are Doubles anyway).
- `isEffectivelyUnbounded` for Range: both offsets null → same as `WindowFrame.unbounded()`.
- Ordering type support: LONG/FLOAT/DOUBLE; timestamps reach native engine as LONG; non-numeric ordering type + finite offset must throw unchecked `DruidException`.
- `ColumnWithDirection` encodes `ASC(1)`/`DESC(-1)` read via `getDirectionInt()`.
- Plan a shared resolver (e.g. `RangeFrameResolver`) in `org.apache.druid.query.operator.window`, exposing peer-group boundaries + per-group frameStart/frameEnd; used by both `DefaultFramedOnHeapAggregatable` (output rows = peer group, input rows = frame interval, natural order; moveTo may full-recompute, correctness first) and `WindowValueProcessorBase.computeFirstOrLastValueFramed`.
- Only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable`; concrete RACs (e.g. `QueryableIndexRowsAndColumns` via `AS_MAP`) don't override `as()` for it, so handling it + value processors covers all `RowsAndColumns`.
- SQL layer facts (verified via `javap` of `calcite-core-1.41.0.jar`): Calcite 1.41 frame grammar only produces ROWS (`createBoolean(true)`) / RANGE (`createBoolean(false)`) — GROUPS is not parseable → `!SqlWindow.isRows()` ⟺ RANGE; `Window.Group` at Rel level has only boolean `isRows`.
- Validator plan: keep old rejection message `"Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead."` for unsupported cases; allow offset RANGE only when window `orderList.size() == 1` (covers both multi-key and missing ORDER BY) and each bound literal is numeric or day-time INTERVAL (`isValidEndpoint` already requires `SqlUtil.isLiteral`); year-month INTERVAL rejected.
- Planning plan (`Windowing.WindowGroup.getWindowFrame()`, current lines 446–461): keep `groups(...)` path when both bounds are UNBOUNDED/CURRENT ROW (preserves string-key behavior); emit `WindowFrame.range(...)` only when ≥1 bound is PRECEDING/FOLLOWING offset; key type check via `sig.getColumnType(fieldIndex)` ∈ {LONG, FLOAT, DOUBLE} (`Calcites.getColumnTypeForRelDataType`/`isLongType` maps TIMESTAMP → ColumnType.LONG).
- `getBoundAsDouble` (new): unbounded → null, currentRow → 0.0, preceding → `-value`, following → `+value`, value = `((Number) window.constants.get(((RexInputRef) bound.getOffset()).getIndex() - sig.size()).getValue()).doubleValue()`; day-time interval RexLiteral value is BigDecimal of **millis** (`SqlParserUtil.intervalToMillis`); year-month → months → reject.
- Quidem `!error` matches `squash(stackTrace).contains(squash(expectedText))`; qaWin files expect only `QueryInterruptedException` (class name in stack trace) before `!error` — any Druid-wrapped validation/planning error matches; files stay as recorded.
- qaWin RANGE queries observed are either no-ORDER-BY (`OVER (PARTITION BY client_ip RANGE 0 FOLLOWING)`, `OVER (RANGE BETWEEN 0 FOLLOWING AND ...)`) or multi-key (`ORDER BY server_ip ASC, timezone, time_floor(__time, 'PT12H') RANGE 0 FOLLOWING`) — both must keep failing via the one-ORDER-BY-key check.
- `testUnSupportedRangeBounds` (CalciteQueryTest.java ~15619): `ROW_NUMBER() OVER (ORDER BY dim1 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING)` — single STRING key; ROW_NUMBER ignores frames and `getWindowFrame()` is never called for it, so it would now succeed → test must be updated.
- `RexWindowBound` exposes `getOffset()`, `isPreceding()`, `isFollowing()`, `isCurrentRow()`; `getBoundAsInteger` keeps only `intValue()`.
- `RewriteFirstValueLastValueRule` only rewrites CURRENT ROW bounds — no interference.
- `updateBoundsIfNeeded` turns single-bound `RANGE 0 FOLLOWING` into `RANGE BETWEEN CURRENT ROW AND 0 FOLLOWING`.
- Jars unpacked under `/tmp/opencode` for `javap` (calcite-core-1.41.0.jar, quidem-0.12.jar).

## Work State
### Completed
- Read all main source/test files listed under Relevant Files; `git status` in `/app` clean; no file edited yet.
- Full design finalized: Range class shape, resolution algorithm (ASC/DESC bounds, NULL run handling, empty frames), shared resolver placement, aggregation and value-processor integration, validator/planner split.
- Verified: quidem `!error` matching semantics; expected text `QueryInterruptedException`; Calcite parser has no GROUPS frame; `Window.Group` only has `isRows` boolean; day-time interval literal → millis BigDecimal; `Calcites` maps TIMESTAMP → `ColumnType.LONG`; `LongColumnAccessorBase` nulls-first-ASC/last-DESC; `DefaultClusteredGroupPartitioner` groups nulls as one peer group; only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable`; `AggIntervalCursor.moveTo` handles empty intervals correctly (zero-row defaults).

### Active
- Todo 1 (`WindowFrame.Range` class) marked in progress; no code written yet.
- Last action: multiline-unaware grep of all qaWin `orderby_range_*.iq` files (`grep -oE "ORDER BY [^)]*RANGE[^)]*\)"`) returned no matches because OVER clauses span lines — full confirmation that every qaWin RANGE query is multi-key or no-ORDER-BY is still pending (earlier greps showed both patterns, no single-key form seen so far).

### Blocked
- None.

## Next Move
1. Re-verify with a multiline-aware scan (e.g. `grep -A5 "RANGE"` / python) that no qaWin RANGE query has exactly one numeric ORDER BY key (would now succeed and break recorded outputs).
2. Write `WindowFrame.Range` + register `"range"` in `@JsonSubTypes` + `range(...)` factory; add EqualsVerifier test in `WindowFrameTest`.
3. Write the shared Range frame resolver class in `org.apache.druid.query.operator.window` (peer groups via `ClusteredGroupPartitioner`, binary search on `getDouble`, NULL-run handling, DruidException for non-numeric types with finite offsets).
4. Wire `DefaultFramedOnHeapAggregatable` (`buildIteratorFor` Range branch, `aggregateAll`, `isEffectivelyUnbounded`) and `WindowValueProcessorBase.computeFirstOrLastValueFramed`.
5. Relax `DruidSqlValidator.validateWindow`: offset RANGE allowed only with exactly one ORDER BY key and numeric/day-time-interval bound literals; keep old message otherwise.
6. Add `Windowing.getWindowFrame` range branch + `getBoundAsDouble` (+ key type check via `sig`, year-month interval rejection).
7. Update `testUnSupportedRangeBounds`; add native Range tests (WindowFramedAggregateProcessorTest, WindowFirstProcessorTest) and SQL planner tests for offset RANGE.
8. `mvn compile`, run affected tests (processing + sql + quidem qaWin), run lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` — frame types; add `Range`, subtype `"range"`, factory; `unbounded()` = `rows(null, null)`.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/FramedOnHeapAggregatable.java` — `aggregateAll` must accept Range.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` — only impl; `buildIteratorFor`, `AggInterval`/`AggIntervalCursor.moveTo`, `GroupIteratorForWindowFrame`, `invertedOrderForLastK`; add Range branch.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/ClusteredGroupPartitioner.java` and `DefaultClusteredGroupPartitioner.java` — peer-group boundaries (`computeBoundaries`).
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFramedAggregateProcessor.java` — keeps frame in `WindowFrame frame` field.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` — `computeFirstOrLastValueFramed`; base of `WindowFirstProcessor`/`WindowLastProcessor`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/ColumnWithDirection.java` — `ASC(1)`/`DESC(-1)`, `getDirectionInt()`.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/column/ColumnAccessor.java` — `getDouble`, `isNull`, `numRows`.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/column/BinarySearchableAccessor.java` — exists but assumes sorted; resolver does its own binary search.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/column/accessor/LongColumnAccessorBase.java` — null sort order reference.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/concrete/QueryableIndexRowsAndColumns.java` — `as()` via `AS_MAP`, no `FramedOnHeapAggregatable`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` — `validateWindow` (lines 114–162), `isValidEndpoint` (705), `isUnboundedOrCurrent` (722), `updateBoundsIfNeeded` (733).
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` — `KNOWN_WINDOW_FNS`, `WindowGroup.getOrdering()`, `getWindowFrame()` (lines 446–461), `getBoundAsInteger`, `computeWindowOperations`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/Calcites.java` — `getColumnTypeForRelDataType`, `isLongType` (TIMESTAMP → LONG).
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rule/RewriteFirstValueLastValueRule.java` — no interference (only CURRENT ROW rewrites).
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/WindowFrameTest.java` — EqualsVerifier tests; add Range.
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/WindowFramedAggregateProcessorTest.java`, `/app/processing/src/test/java/org/apache/druid/query/operator/window/RowsAndColumnsHelper.java`, `/app/processing/src/test/java/org/apache/druid/query/operator/window/value/WindowFirstProcessorTest.java` — native test harness.
- `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` — `testUnSupportedRangeBounds` (~15619), `testUnSupportedWindowBoundExpressions` (~15630).
- `/app/quidem-ut/src/test/quidem/org.apache.druid.quidem.QTest/qaWin/` — recorded RANGE cases (`orderby_range_*_{first_last,sum_count}.NN.all.iq`), must keep failing.
- `/root/.m2/repository/org/apache/calcite/calcite-core/1.41.0/calcite-core-1.41.0.jar` and `/root/.m2/repository/net/hydromatic/quidem/0.12/quidem-0.12.jar` — inspected via `javap` (unpacked under `/tmp/opencode`).
