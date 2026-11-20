## Objective
- Implement a native value-based `RANGE` window frame type (`WindowFrame.Range`, Jackson subtype `"range"`) in Apache Druid, extending framed aggregation (`FramedOnHeapAggregatable#aggregateAll`) and value processors (`WindowFramedAggregateProcessor`, `WindowFirstProcessor`, `WindowLastProcessor`), plus SQL validator and Calcite window planning to plan offset-based `RANGE` frames with exactly one ORDER BY key.

## Important Details
- `WindowFrame.Range`: public nested class in `WindowFrame`, registered via `@JsonSubTypes` as `"range"`; fields `@Nullable Double lowerOffset`, `@Nullable Double upperOffset`, non-null `ColumnWithDirection orderBy`; getters `getLowerOffset()`/`getUpperOffset()`/`getOrderBy()`; static factory `WindowFrame.range(@Nullable Double, @Nullable Double, ColumnWithDirection orderBy)`; standalone `WindowFrame` implementation (NOT extending `OffsetFrame`); `equals`/`hashCode` by value; Jackson serde supported; null offset = positionally UNBOUNDED, non-null = signed distance in ordering-key value space.
- Frame resolution semantics: bound value = `v + o` when ASC, `v - o` when DESC, closed interval `[lowerBound, upperBound]`; UNBOUNDED bounds stay positional (partition boundaries, include NULL-key rows); NULL current-row key with finite offsets resolves to boundaries of the contiguous NULL run (peer group); peers get identical boundaries/outputs; empty frame → aggregator zero-row default, or `null` for FIRST_VALUE/LAST_VALUE; full-partition `Range` must evaluate identically to `WindowFrame.unbounded()`; must support LONG/FLOAT/DOUBLE ordering columns (timestamps reach native engine as LONG) across all `RowsAndColumns` implementations; unsupported ordering column types → unchecked `DruidException`.
- SQL planning: accept `RANGE BETWEEN <offset> PRECEDING AND <offset> FOLLOWING` (incl. one-sided and CURRENT ROW) only with exactly one ORDER BY key; ordering key numeric or timestamp; bound literal numeric or day-time INTERVAL; day-time INTERVAL → millisecond magnitude as floating-point offset without integer truncation; unsupported forms (multiple ORDER BY keys, non-numeric/non-interval keys with finite bounds) must fail validation or planning.
- Current validator error message: "Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead." — quidem `qaWin` `.iq` files (all multi-ORDER-BY-key RANGE queries) expect `QueryInterruptedException` + `!error`, so those queries must keep erroring (message compatibility under investigation).
- Calcite 1.41.0 (`/root/.m2/repository/org/apache/calcite/calcite-core/1.41.0/calcite-core-1.41.0.jar`): `RexWindowBound` (`isUnboundedPreceding/Following`, `isPreceding/Following`, `isCurrentRow`, `getOffset`); frame bound offsets appear as `RexInputRef` into `window.constants`; current `Windowing.getWindowFrame()` uses `getBoundAsInteger` (`Number.intValue()`) — RANGE needs a double-based variant.
- `SqlWindow.updateBoundsIfNeeded`: single-bound `RANGE 0 FOLLOWING` becomes `RANGE BETWEEN CURRENT ROW AND 0 FOLLOWING`.
- Tooling notes: `rg` is NOT installed (use `grep`/`find`); `/tmp/opencode` used for `javap` inspection of calcite-core and quidem-0.12 jars; repo `/app` is on master, working tree clean.

## Work State
### Completed
- Located all key files: `WindowFrame.java`, `FramedOnHeapAggregatable.java`, `DefaultFramedOnHeapAggregatable.java`, `WindowFramedAggregateProcessor.java`, `WindowFirstProcessor.java`, `WindowLastProcessor.java`, `WindowValueProcessorBase.java`, `ShiftedColumnAccessorBase.java`, `ColumnWithDirection.java`, `DruidSqlValidator.java`, `Windowing.java`, `RewriteFirstValueLastValueRule.java`.
- Confirmed `WindowFrame` structure: `@JsonTypeInfo(use = Id.NAME, property = "type")`, subtypes `"rows"`→`Rows`, `"groups"`→`Groups`; `WindowFrame.unbounded()` returns `rows(null, null)`; `OffsetFrame` has `getLowerOffsetClamped(int)`/`getUpperOffsetClamped(int)`; `ColumnWithDirection.Direction` is ASC(1)/DESC(-1) with `getDirectionInt()`, factories `ascending(String)`/`descending(String)`.
- Confirmed `Windowing.java` lines ~449–457 `getWindowFrame()`: `unbounded()` / `WindowFrame.rows(getBoundAsInteger(lower), getBoundAsInteger(upper))` / `WindowFrame.groups(..., getOrderingColumNames())`.
- Confirmed test patterns: `WindowFrameTest` uses `EqualsVerifier.forClass(...).usingGetClass().verify()`; `WindowFramedAggregateProcessorTest` and `WindowFirstProcessorTest` use `MapOfColumnsRowsAndColumns` + `IntArrayColumn`/`DoubleArrayColumn`/`ObjectArrayColumn` and `RowsAndColumnsHelper`.
- Confirmed quidem `qaWin` RANGE tests (`orderby_range_0_following_*`, `orderby_range_0_preceding_*`) all use multiple ORDER BY keys and expect `!error` (should remain errors after change); `CalciteQueryTest.java:15625` has ROW_NUMBER with RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING.
- Created 8-item todo list (Range class → aggregation → value processors → validator → planning → native tests → SQL/quidem tests → run compile/tests/lint).

### Active
- Investigating quidem `!error` matching semantics (`Quidem$ErrorCommand.checkResultSet` via `javap` on quidem-0.12.jar) to verify whether the recorded "QueryInterruptedException" expectation breaks if the validator error message changes for still-unsupported multi-key RANGE forms — investigation incomplete.
- No code changes written yet (working tree clean).

### Blocked
- (none)

## Next Move
1. Implement `WindowFrame.Range` nested class in `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` — Jackson subtype `"range"`, `@Nullable Double lowerOffset`/`upperOffset`, `ColumnWithDirection orderBy`, getters, static factory `WindowFrame.range(...)`, value-based `equals`/`hashCode` (todo item 1, in progress).
2. Then extend `DefaultFramedOnHeapAggregatable#aggregateAll` and `WindowFramedAggregateProcessor`/`WindowFirstProcessor`/`WindowLastProcessor` (via `WindowValueProcessorBase`) for Range resolution per the semantics above, then `DruidSqlValidator` + `Windowing` planning, then unit/SQL tests, then compile/test/lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` — add `Range` nested class + `"range"` subtype + factory
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/FramedOnHeapAggregatable.java` — semantic interface for framed aggregation (`aggregateAll`)
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` — default frame resolution (imports `WindowFrame.Groups`/`OffsetFrame`/`Rows`)
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFramedAggregateProcessor.java` — framed aggregate processor to extend
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowFirstProcessor.java` — FIRST_VALUE processor (null on empty frame)
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowLastProcessor.java` — LAST_VALUE processor (null on empty frame)
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` — shared base for value processors
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/ShiftedColumnAccessorBase.java` — shifted accessor base (positional bounds pattern)
- `/app/processing/src/main/java/org/apache/druid/query/operator/ColumnWithDirection.java` — orderBy column + ASC(1)/DESC(-1) direction
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` — `validateWindow` RANGE restriction to relax for single-key
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` — `WindowGroup.getWindowFrame()`/`getBoundAsInteger` (lines ~449–457) needs a RANGE branch producing `WindowFrame.range`
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rule/RewriteFirstValueLastValueRule.java` — existing RANGE handling/rewrites
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/WindowFrameTest.java`, `WindowFramedAggregateProcessorTest.java`, `value/WindowFirstProcessorTest.java`, `RowsAndColumnsHelper.java` — test patterns to follow
- `/app/quidem-ut/src/test/quidem/org.apache.druid.quidem.QTest/qaWin/` — recorded `.iq` files expecting errors for multi-key RANGE
- `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java:15625` — existing RANGE query test expecting failure
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/` (incl. `concrete/`, `column/`, `semantic/`) — RowsAndColumns implementations that must support Range resolution
