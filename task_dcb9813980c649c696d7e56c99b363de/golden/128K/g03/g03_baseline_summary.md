## Objective
- Add native value-based `RANGE` window framing to Druid in `/app`: a `WindowFrame.Range` type plus resolver, native wiring through aggregation and value processors, SQL validator relaxation for single-key numeric/timestamp offset `RANGE` frames, Calcite planning, and tests. Multi-key `RANGE` queries must still fail when the work is done.

## Important Details
- `WindowFrame.Range` must be a public nested class of `WindowFrame`, registered as Jackson subtype `"range"`, with `@Nullable Double lowerOffset`, `@Nullable Double upperOffset`, non-null `ColumnWithDirection orderBy`; getters `getLowerOffset()`/`getUpperOffset()`/`getOrderBy()`; static factory `WindowFrame.range(@Nullable Double, @Nullable Double, ColumnWithDirection)`; must not extend `OffsetFrame`; equals/hashCode by value; Jackson ser/deser; whole-partition `Range` evaluates same as `WindowFrame.unbounded()`.
- Frame semantics: bound = `v + o` under `ASC`, `v - o` under `DESC`; frame = closed interval between bounds; unbounded sides reach partition edges including `NULL` rows; null-key row with finite bounds resolves to the null-run edges; peers get identical bounds/output; empty frame → aggregator zero-row default; `FIRST_VALUE`/`LAST_VALUE` return null on empty frame.
- `LONG`/`FLOAT`/`DOUBLE` keys must work (compare as doubles via `accessor.getDouble(row)`; precision loss beyond 2^53 accepted); timestamps reach native as `LONG`; non-numeric key type with a finite offset must throw an unchecked `DruidException`; resolution must work for every `RowsAndColumns` implementation (only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable` in main code; handling `Range` there + in the value processors covers everything).
- `FramedOnHeapAggregatable#aggregateAll`, `WindowFramedAggregateProcessor`, `WindowFirstProcessor`, `WindowLastProcessor` must accept `Range`.
- SQL layer: validator accepts offset `RANGE` frames (one-sided and `CURRENT ROW` bounds); planning turns them native only with exactly one `ORDER BY` key that is numeric or timestamp; bound literal may be a number or day-time `INTERVAL` (millisecond magnitude as floating-point offset, no truncation); year-month `INTERVAL` rejected (months vs millis via `SqlParserUtil.intervalToMillis`/`intervalToMonths`); non-numeric non-interval keys rejected at validation or planning.
- Decision: new class `RangeFrameResolver` in `org.apache.druid.query.operator.window`; constructor `(RowsAndColumns rac, WindowFrame.Range frame)`; keeps `groupBoundaries`/`frameStarts`/`frameEnds`; exposes `getNumGroups/getGroupStart/getGroupEnd/getFrameStart/getFrameEnd` primitives (peer groups from `ClusteredGroupPartitioner.computeBoundaries` on the `ORDER BY` column; no merging of adjacent identical-frame groups). `AggInterval`/`Interval` are package-private inside `DefaultFramedOnHeapAggregatable`, so the resolver only exposes primitives.
- Resolution algorithm (keys via `getDouble`, searches over non-null rows only since `getDouble(null)` = 0.0):
  - Null run from sort order: `ASC` → nulls are a prefix `[0, nullRunEnd)`; `DESC` → nulls are a suffix `[nullRunStart, numRows)`; detected via `accessor.isNull` scan, not `compareRows` null semantics.
  - Universal null-key rule: lower finite → `nullRunStart`; upper finite → `nullRunEnd`; lower unbounded → 0; upper unbounded → `numRows` (so any-finite-bounds null row frame = null run; DuckDB-like).
  - Non-null `v` `ASC`: frameStart = lower unbounded ? 0 : first idx in `[nullRunEnd, numRows)` with val ≥ `v+lower`; frameEnd = upper unbounded ? `numRows` : first idx in `[nullRunEnd, numRows)` with val > `v+upper` (exclusive). `DESC`: frameStart = lower unbounded ? 0 : first idx in `[0, nullRunStart)` with val ≤ `v-lower`; frameEnd = upper unbounded ? `numRows` : first idx in `[0, nullRunStart)` with val < `v-upper` (exclusive). Binary helpers `lowerBoundAsc/upperBoundAsc/lowerBoundDesc/upperBoundDesc`.
  - Negative offsets well-defined (`-1 PRECEDING` → bound `v+1`); `frameStart > frameEnd` → empty frame, handled by existing zero-row default.
  - frameStart/frameEnd are monotone non-decreasing across groups in both directions → `AggIntervalCursor.moveTo` incremental branches stay correct (aggregators commutative); `moveTo` else-branch recomputes whole interval when both ends move.
- `isEffectivelyUnbounded` must handle `Range` before the `OffsetFrame` unwrap (NPE risk): both offsets null → unbounded → `buildUnboundedIteratorFor`.
- `DefaultFramedOnHeapAggregatable` gets a private static `buildRangeIteratorFor(rac, rangeFrame)` returning `Iterable<AggInterval>` with `AggInterval(Interval.of(groupStart, groupEnd), Interval.of(frameStart, frameEnd))`.
- `WindowValueProcessorBase.computeFirstOrLastValueFramed` `Range` branch: if `frameStart < frameEnd`, value = `first ? accessor.getObject(frameStart) : accessor.getObject(frameEnd - 1)`, filled over `[groupStart, groupEnd)`; empty frame leaves results null.
- Validator (`DruidSqlValidator.validateWindow`, checks run before `super`, raised via `buildCalciteContextException(windowOrId)` → `CalciteContextException`): keep old message `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.`; reject when `orderList` null or size != 1 or bound literal invalid; `isValidRangeBound`: true if `isUnboundedOrCurrent`; `PRECING`/`FOLLOWING` operand `instanceof SqlNumericLiteral` → true; `SqlIntervalLiteral` with `!((SqlIntervalLiteral.IntervalValue) literal.getValue()).getIntervalQualifier().isYearMonth()` → true; else false. No-ORDER-BY offset `RANGE` rejected.
- `Windowing.getWindowFrame`: keep `groups(...)` path when no bound is a `PRECEDING`/`FOLLOWING` offset; new `isOffsetBound(bound) = bound.isPreceding() || bound.isFollowing()` (true only for finite bounds since `UNBOUNDED_PRECEDING`/`UNBOUNDED_FOLLOWING` are separate `SqlKind`s); `buildRangeFrame` does defensive exactly-one-key check (`group.orderKeys.getFieldCollations().size() != 1` → `QueryException(SQL_QUERY_UNSUPPORTED...)`), direction switch, `sig.getColumnName/getColumnType(fieldIndex)`, non-numeric → same `QueryException` pattern; new `getBoundAsDouble` (unbounded → null, `CURRENT ROW` → 0.0, `PRECEDING` → negated, `FOLLOWING` → as-is) reading `((Number) window.constants.get(refIndex - sig.size()).getValue()).doubleValue()`. `getBoundAsInteger` keeps only `intValue()` so it can't be reused.
- Key type check at planning time because `sig` is available there; `Calcites.isLongType` counts `TIMESTAMP` so sig reports timestamp keys as `LONG` (so `ORDER BY time_floor(__time, ...)` works).
- Resolver defensive checks: missing order column → `DruidException.defensive`; non-numeric column type when any offset finite → `DruidException.defensive` (uses `ColumnType.isNumeric()` — existence still unverified).
- `Range` constructor mirrors `Groups` style (no null checks) for `EqualsVerifier` friendliness; `WindowFrameTest` uses `EqualsVerifier.forClass(...).usingGetClass().verify()`.
- `testUnSupportedRangeBounds` update: change SQL to `ORDER BY dim1, dim2 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING` → same old message and same expected column 31 (prefix `SELECT dim1,ROW_NUMBER() OVER (` unchanged; 31 = the `(` after `OVER`).
- Accepted inconsistency: `ROW_NUMBER` with string key + offset `RANGE` passes the validator and succeeds silently (`ROW_NUMBER` never calls `getWindowFrame()`).
- Nulls direction: validator rejects `ASC NULLS LAST` / `DESC NULLS FIRST`, so allowed combos match native sort (null-first `ASC` via `compareRows` null lhs = -1 × direction; null-last `DESC`; `compareRows(null, null)` = 0 → one null peer group).
- Calcite facts: 1.41 cannot parse `GROUPS`; `Window.Group` has only boolean `isRows`; `updateBoundsIfNeeded` turns `RANGE 0 FOLLOWING` into `RANGE BETWEEN CURRENT ROW AND 0 FOLLOWING`; `WindowFrame` maps `"rows"`→`Rows`, `"groups"`→`Groups`, `unbounded()` = `rows(null, null)`; `RewriteFirstValueLastValueRule` rewrites only `CURRENT ROW` bounds → no interference.
- Native users can construct `WindowFrame.range` directly via window operator query JSON (`WindowFramedAggregateProcessor` holds the `WindowFrame` field; `ColumnWithDirection` serde works).
- Quidem: `!error` checks squashed stack trace contains squashed expected text; qaWin `RANGE` cases expect only `QueryInterruptedException`; any Druid validation/planning error still matches → qaWin files left as recorded.

## Work State
### Completed
- Verified every qaWin `RANGE` case (python extraction over `orderby_range_*.iq`): all have no `ORDER BY` or 3-4 keys, none single-key → the "exactly one key" validator rule keeps every recorded `QueryInterruptedException` intact; no `.iq` edits needed. Examples: `OVER (PARTITION BY client_ip ORDER BY server_ip, time_floor(__time, 'PT12H') ASC, timezone RANGE 0 FOLLOWING)` (3 keys), `... ORDER BY server_ip, length(server_ip) DESC, timezone, time_floor(__time, 'PT12H') RANGE ...` (4 keys), `OVER (PARTITION BY client_ip RANGE 0 FOLLOWING)` (none). Full output at `/logs/agent/opencode/xdg-data/opencode/tool-output/tool_1f268efbf001S0z110HYFn9FDH`.
- Re-read key files in fresh context: `WindowFrame.java`, `WindowValueProcessorBase.java`, `DefaultFramedOnHeapAggregatable.java`, `FramedOnHeapAggregatable.java`, `ColumnWithDirection.java`, `ClusteredGroupPartitioner.java`, `ColumnAccessor.java`, `WindowFrameTest.java`, `Windowing.java`, `DruidSqlValidator.java` (lines 1-200, 660-790), `WindowFirstProcessor.java`, `WindowFramedAggregateProcessor.java`, `DefaultClusteredGroupPartitioner.java` (several reads truncated).
- Full implementation design worked out: `Range` class shape, resolver algorithm incl. null-run rules and binary searches, monotonicity/`moveTo` safety, validator checks, `Windowing` branch, test updates.
- 8-item todo list created (todo 1 in progress, rest pending).

### Active
- Todo 1: add `WindowFrame.Range` class + `"range"` `@JsonSubTypes` entry + `range()` factory — marked in progress, no code written yet.
- No file in `/app` has been edited.

### Blocked
- (none)
- Still-to-verify items (not blocking): `ColumnType.isNumeric()` exists; `compareRows(null, null)` == 0 verified only for `LongColumnAccessorBase` (others unverified, but null-run detection uses `isNull` scan); `WindowFirstProcessor` results array initialization; full bodies of `Windowing.java`, `DefaultFramedOnHeapAggregatable.java`, `WindowFirstProcessor.java` (reads truncated); `Calcites` `DATE` type mapping.

## Next Move
1. Write `WindowFrame.Range` in `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java`: class (`Double lowerOffset/upperOffset`, `ColumnWithDirection orderBy`, `@JsonCreator`, equals/hashCode/toString), `@JsonSubTypes.Type(name = "range", ...)`, `range(...)` factory.
2. Write new `RangeFrameResolver` in `org.apache.druid.query.operator.window` (peer groups via `computeBoundaries`, null-run via `isNull` scan, `getDouble` binary searches per the ASC/DESC and null-key rules above, defensive `DruidException` checks).
3. Wire `DefaultFramedOnHeapAggregatable`: `buildRangeIteratorFor`, `Range` branch in `isEffectivelyUnbounded` before the `OffsetFrame` unwrap.
4. Add `Range` branch in `WindowValueProcessorBase.computeFirstOrLastValueFramed`.
5. Relax `DruidSqlValidator.validateWindow`: single-key + `isValidRangeBound` check, old message kept.
6. Add `isOffsetBound`, `getBoundAsDouble`, `buildRangeFrame` to `Windowing.getWindowFrame`.
7. Update `testUnSupportedRangeBounds` to `ORDER BY dim1, dim2 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING`; add `EqualsVerifier` test for `Range` in `WindowFrameTest`; add native tests (aggregation + FIRST/LAST_VALUE with `Range`, incl. nulls, `DESC`, empty frames, unbounded variants) and SQL planner tests.
8. Compile, run tests, lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` — add `Range` class, `"range"` subtype, `range()` factory.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` — only main `FramedOnHeapAggregatable` impl; `buildRangeIteratorFor`, `isEffectivelyUnbounded`; holds package-private `AggInterval`/`Interval`.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/FramedOnHeapAggregatable.java` — `aggregateAll` must accept `Range`.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/ClusteredGroupPartitioner.java` and `DefaultClusteredGroupPartitioner.java` — `computeBoundaries` conventions.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/column/ColumnAccessor.java` — `isNull`/`getDouble`/`getObject`/`numRows`/`getType`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/ColumnWithDirection.java` — `ASC(1)`/`DESC(-1)` via `getDirectionInt()`, Jackson serde.
- New `/app/processing/src/main/java/org/apache/druid/query/operator/window/RangeFrameResolver.java` — the resolver.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` — `computeFirstOrLastValueFramed` `Range` branch.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowFirstProcessor.java` and `WindowLastProcessor.java` — must accept `Range`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFramedAggregateProcessor.java` — holds `WindowFrame` field; accepts `Range`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` — `validateWindow` relaxation, `isValidRangeBound`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` — `getWindowFrame` range branch, `getBoundAsDouble`, `buildRangeFrame`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/Calcites.java` — `isLongType`.
- `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` — `testUnSupportedRangeBounds` update + new SQL tests.
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/WindowFrameTest.java` — `EqualsVerifier` frame tests.
- `/app/quidem-ut/src/test/quidem/org.apache.druid.quidem.QTest/qaWin/` — recorded `RANGE` cases (left as recorded).
- `/logs/agent/opencode/xdg-data/opencode/tool-output/tool_1f268efbf001S0z110HYFn9FDH` — full qaWin `RANGE` OVER-clause extraction output.
