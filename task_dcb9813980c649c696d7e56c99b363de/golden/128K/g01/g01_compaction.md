## Objective
- Add native value-based `RANGE` window framing to Druid in `/app`.
- The new type must be `WindowFrame.Range`.
- `WindowFrame.Range` must be a public nested class of `WindowFrame`.
- `WindowFrame.Range` must be registered as Jackson subtype `"range"`.
- Multi-key `RANGE` queries must still fail when the work is done.

## Important Details
- `WindowFrame.Range` must have a `@Nullable Double lowerOffset`.
- `WindowFrame.Range` must have a `@Nullable Double upperOffset`.
- `WindowFrame.Range` must have a non-null `ColumnWithDirection orderBy`.
- The required getter for the lower offset is `getLowerOffset()`.
- The required getter for the upper offset is `getUpperOffset()`.
- The required getter for the ordering column is `getOrderBy()`.
- A null offset must mean a positionally unbounded side.
- A non-null offset must be a signed distance in the ordering key's value space.
- The required static factory is `WindowFrame.range(@Nullable Double lowerOffset, @Nullable Double upperOffset, ColumnWithDirection orderBy)`.
- `Range` must not extend `OffsetFrame`.
- `Range` must override `equals` by value.
- `Range` must override `hashCode` by value.
- `Range` must support Jackson serialization.
- `Range` must support Jackson deserialization.
- `FramedOnHeapAggregatable#aggregateAll` must accept `Range`.
- `WindowFramedAggregateProcessor` must accept `Range`.
- `WindowFirstProcessor` must accept `Range`.
- `WindowLastProcessor` must accept `Range`.
- For a non-null ordering key value `v` and a finite offset `o`, a bound must be `v + o` under `ASC`.
- For a non-null ordering key value `v` and a finite offset `o`, a bound must be `v - o` under `DESC`.
- A `Range` frame must be the closed interval between its lower bound and its upper bound.
- Unbounded sides of a `Range` frame must reach the partition edges.
- Unbounded sides of a `Range` frame must include rows whose key is `NULL`.
- When the current row's key is `NULL`, finite bounds must resolve to the edges of the contiguous `NULL` run that holds the row.
- Peers with equal keys must get identical frame bounds.
- Peers with equal keys must get identical output.
- An empty frame must yield the aggregator's zero-row default.
- `FIRST_VALUE` must return `null` on an empty frame.
- `LAST_VALUE` must return `null` on an empty frame.
- A `Range` that covers the whole partition for every row must evaluate the same as `WindowFrame.unbounded()`.
- `LONG` ordering columns must work.
- `FLOAT` ordering columns must work.
- `DOUBLE` ordering columns must work.
- Range resolution must work for every `RowsAndColumns` implementation.
- Timestamp columns reach the native engine as `LONG`.
- An ordering type that cannot do value arithmetic with a finite offset must throw an unchecked `DruidException`.
- The SQL validator must accept offset `RANGE` frames.
- The SQL validator must accept one-sided offset `RANGE` frames.
- The SQL validator must accept offset `RANGE` frames with a `CURRENT ROW` bound.
- Calcite planning must turn offset `RANGE` frames into native frames.
- Offset `RANGE` support must apply only when the window has exactly one `ORDER BY` key.
- The single key must be numeric or a timestamp.
- The bound literal may be a number.
- The bound literal may be a day-time `INTERVAL`.
- A day-time `INTERVAL` must map to its millisecond magnitude as a floating-point offset with no integer truncation.
- An offset `RANGE` frame with finite bounds on a non-numeric and non-interval key must be rejected during validation or planning.
- `WindowFrame` maps the Jackson name `"rows"` to `WindowFrame.Rows`.
- `WindowFrame` maps the Jackson name `"groups"` to `WindowFrame.Groups`.
- `WindowFrame.unbounded()` returns `rows(null, null)`.
- `ColumnWithDirection` encodes `ASC` as `ASC(1)`, read through `getDirectionInt()`.
- `ColumnWithDirection` encodes `DESC` as `DESC(-1)`, read through `getDirectionInt()`.
- `Windowing.java` builds row frames as `WindowFrame.rows(getBoundAsInteger(group.lowerBound), getBoundAsInteger(group.upperBound))`.
- `Windowing.java` builds group frames as `WindowFrame.groups(getBoundAsInteger(group.lowerBound), getBoundAsInteger(group.upperBound), getOrderingColumNames())`.
- `Windowing.java` has no range branch yet.
- `RexWindowBound` exposes `getOffset()`.
- `RexWindowBound` exposes `isPreceding()`.
- `RexWindowBound` exposes `isFollowing()`.
- `RexWindowBound` exposes `isCurrentRow()`.
- The agent judged that frame offsets reach `Windowing` as `RexInputRef` entries into `window.constants`.
- The agent judged that the constant is read as `window.constants.get(refIndex - sig.size()).getValue()`.
- The agent judged that `DruidSqlValidator.validateWindow` currently rejects every offset `RANGE` frame.
- The agent judged that this rejection is raised as a `CalciteContextException`.
- The agent judged that `updateBoundsIfNeeded` turns the single bound `RANGE 0 FOLLOWING` into `RANGE BETWEEN CURRENT ROW AND 0 FOLLOWING`.
- The `qaWin` directory holds quidem `RANGE` cases named `orderby_range_0_following_first_last.01.all.iq` through `.15.all.iq`.
- The `qaWin` directory holds quidem `RANGE` cases named `orderby_range_0_following_sum_count.01.all.iq` through `.15.all.iq`.
- The `qaWin` directory holds quidem `RANGE` cases named `orderby_range_0_preceding_first_last.01.all.iq` through `.05.all.iq`.
- The `qaWin` `RANGE` cases the agent printed have several `ORDER BY` keys or none.
- It is unconfirmed whether every `qaWin` `RANGE` case has several `ORDER BY` keys or none.
- The `qaWin` `RANGE` cases the agent printed expect a `QueryInterruptedException` line followed by `!error`.
- Decision: the planned `RANGE` branch will read offsets through a new `getBoundAsDouble` reader that takes `doubleValue()` from the offset constant's `Number`, instead of `getBoundAsInteger`.
- The reason is that `Range` offsets are `Double` values.
- The agent judged that `getBoundAsInteger` keeps only `intValue()`.
- Decision: unsupported `RANGE` forms will keep `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.` as the validator rejection message.
- The reason is that the multi-key `RANGE` cases in the `qaWin` quidem files then keep failing.
- Decision: the `qaWin` files are left as recorded.
- Jars are unpacked under `/tmp/opencode` for `javap`.
- `WindowFrameTest` checks frame equality with `EqualsVerifier.forClass(...).usingGetClass().verify()`.

## Work State
### Completed
- The agent has read the main source and test files listed under Relevant Files.
- `git status` in `/app` reports a clean working tree.
- No file has been edited.

### Active
- Todo 1, the `WindowFrame.Range` class, is marked in progress.
- No code for todo 1 is written yet.
- The agent was reading the `Quidem$ErrorCommand` bytecode to learn how `!error` compares a changed validator rejection message with the `QueryInterruptedException` line in the `qaWin` `.iq` files.

### Blocked
- No item is blocked.

## Next Move
1. Add the `WindowFrame.Range` class to `WindowFrame.java`.
2. Register `Range` as `"range"` in `@JsonSubTypes`.
3. Add the `range(...)` factory.
4. Make `DefaultFramedOnHeapAggregatable` resolve `Range` frames.
5. Add `Range` handling in `WindowValueProcessorBase`.
6. Relax `DruidSqlValidator.validateWindow` for the supported `RANGE` forms.
7. Add a range branch to `Windowing.WindowGroup.getWindowFrame()` that builds `WindowFrame.range(...)`.
8. Write native `Range` tests.
9. Write SQL planner tests for offset `RANGE` frames.
10. Compile the code.
11. Run the tests.
12. Run lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` holds the frame types.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/FramedOnHeapAggregatable.java` defines `aggregateAll`.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` imports `WindowFrame.Rows`.
- `DefaultFramedOnHeapAggregatable.java` imports `WindowFrame.Groups`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFramedAggregateProcessor.java` keeps its frame in a `WindowFrame frame` field.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` is the base class of `WindowFirstProcessor`.
- `WindowValueProcessorBase` is also the base class of `WindowLastProcessor`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/ColumnWithDirection.java` defines `ColumnWithDirection`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` holds `validateWindow`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` turns Calcite bounds into native frames.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rule/RewriteFirstValueLastValueRule.java` rewrites some `FIRST_VALUE` cases to simpler plans.
- `RewriteFirstValueLastValueRule` also rewrites some `LAST_VALUE` cases to simpler plans.
- `WindowFrameTest.java` is a native window test under `/app/processing/src/test/java/org/apache/druid/query/operator/window/`.
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/WindowFramedAggregateProcessorTest.java` is a native window test.
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/RowsAndColumnsHelper.java` is a native test helper.
- `/app/processing/src/test/java/org/apache/druid/query/operator/window/value/WindowFirstProcessorTest.java` is a native window test.
- `/app/quidem-ut/src/test/quidem/org.apache.druid.quidem.QTest/qaWin/` holds the recorded `RANGE` cases.
- The agent inspected `/root/.m2/repository/org/apache/calcite/calcite-core/1.41.0/calcite-core-1.41.0.jar` with `javap`.
- The agent inspected `/root/.m2/repository/net/hydromatic/quidem/0.12/quidem-0.12.jar` with `javap`.
