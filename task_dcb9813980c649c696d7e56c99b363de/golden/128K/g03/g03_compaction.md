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
- The agent found earlier that `ColumnWithDirection` encodes `ASC` as `ASC(1)`, read through `getDirectionInt()`.
- The agent found earlier that `ColumnWithDirection` encodes `DESC` as `DESC(-1)`, read through `getDirectionInt()`.
- The agent found earlier that only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable` in the main code.
- The agent concluded that handling `Range` in `DefaultFramedOnHeapAggregatable` and in the value processors covers every `RowsAndColumns`.
- Decision: `WindowFrame.Range` will implement `WindowFrame` directly.
- The agent judged that `OffsetFrame` has `Integer` offsets.
- Decision: the planned `Range` constructor will not null-check `orderBy`.
- This replaces an earlier draft with a null check, because the agent judged that `EqualsVerifier` may reject one.
- The agent judged that `compareRows` returns -1 for a null left row, so null keys sort first under `ASC`.
- The agent judged that the sort multiplies `compareRows` by the direction, so null keys sort last under `DESC`.
- The agent judged that `compareRows(null, null)` returns 0, so the `NULL` rows form one peer group.
- Decision: a new class `RangeFrameResolver` in `org.apache.druid.query.operator.window` will compute the peer groups and the frame start and end of each group.
- The reason is that `DefaultFramedOnHeapAggregatable` and `WindowValueProcessorBase.computeFirstOrLastValueFramed` both need the peer groups and their frame intervals.
- Decision: the peer groups come from `computeBoundaries` on the `ORDER BY` column.
- The planned `RangeFrameResolver` constructor takes `RowsAndColumns rac` and `WindowFrame.Range frame`.
- The planned `RangeFrameResolver` keeps the peer group edges in `groupBoundaries`.
- The planned `RangeFrameResolver` keeps one frame start per group in `frameStarts`.
- The planned `RangeFrameResolver` keeps one frame end per group in `frameEnds`.
- Decision: both users of `RangeFrameResolver` will iterate the peer groups directly, without merging adjacent groups that have identical frames.
- The agent judged that such merging is possible but not worth doing.
- Decision: in `computeFirstOrLastValueFramed`, a `Range` peer group's `FIRST_VALUE` takes `getObject(frameStart)`.
- Decision: in `computeFirstOrLastValueFramed`, a `Range` peer group's `LAST_VALUE` takes `getObject(frameEnd - 1)`.
- Decision: a `Range` peer group gets a null value unless `frameStart < frameEnd`.
- Decision: `RangeFrameResolver` will throw a defensive `DruidException` when an offset is finite and the `ORDER BY` column is not numeric.
- Decision: `RangeFrameResolver` will throw `DruidException.defensive("Column[%s] does not exist", orderColumn)` when the `ORDER BY` column is missing.
- Decision: keys are compared as doubles through `accessor.getDouble(row)`.
- The reason is that `getDouble` treats `LONG`, `FLOAT` and `DOUBLE` keys the same way.
- The agent accepted a precision loss for key values beyond 2^53.
- Under `ASC`, the planned frame start is the first row whose value is at least the lower bound.
- Under `ASC`, the planned frame end is the first row whose value is greater than the upper bound, exclusive.
- Under `DESC`, the planned frame start is the first row whose value is at most the lower bound.
- Under `DESC`, the planned frame end is the first row whose value is less than the upper bound, exclusive.
- The planned search covers only the non-null rows, because the agent found earlier that `getDouble` on a null row gives 0.0.
- Decision: under `DESC`, when no non-null row is below the upper bound, the frame end is the start of the null run.
- This replaces the plain `DESC` end rule for that case, because the agent found it wrong when the upper bound is below every non-null value and null rows exist.
- Decision: `isEffectivelyUnbounded` treats a `Range` with both offsets null as unbounded.
- The agent judged that `isEffectivelyUnbounded` would fail on a `Range`, because it unwraps the frame as `OffsetFrame`.
- Decision: the `Range` branch in `isEffectivelyUnbounded` goes before the `OffsetFrame` unwrap.
- Decision: a new private static `buildRangeIteratorFor(rac, rangeFrame)` in `DefaultFramedOnHeapAggregatable` will yield one interval per peer group.
- Decision: `moveTo` stays unchanged, which replaces the planned full recompute for `Range` frames.
- The reason is that the agent judged `Range` frame bounds never decrease from one peer group to the next, so the existing `moveTo` stays correct.
- The agent found earlier that `DruidSqlValidator.validateWindow` rejects a `RANGE` frame unless both bounds pass `isUnboundedOrCurrent`.
- The agent concluded that Calcite 1.41 cannot parse `GROUPS` frames.
- The agent concluded that a false `isRows()` therefore means `RANGE`.
- The agent found earlier that quidem `!error` checks that the squashed stack trace contains the squashed expected text.
- The agent found earlier that the `qaWin` files expect only `QueryInterruptedException` before `!error`.
- The agent judged that any Druid validation or planning error therefore still matches the `qaWin` expectations.
- The agent found earlier that some `qaWin` `RANGE` windows have no `ORDER BY`.
- The visible part of the agent's balanced-paren scan of the `qaWin` `orderby_range_*.iq` files shows only `RANGE` clauses with several `ORDER BY` keys.
- The rest of that scan output was cut.
- The agent concluded from this scan that no `qaWin` `RANGE` case has exactly one `ORDER BY` key.
- Decision: unsupported `RANGE` forms will keep `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.` as the validator rejection message.
- The reason is that the multi-key `RANGE` cases in the `qaWin` quidem files then keep failing.
- Decision: the `qaWin` files are left as recorded.
- Decision: an offset `RANGE` frame with no `ORDER BY` is rejected.
- The reason is that `WindowFrame.range` needs an ordering column.
- Decision: the validator accepts an offset `RANGE` frame only with exactly one `ORDER BY` key.
- The planned validator check rejects an offset `RANGE` frame when `orderList` is null or its size is not 1.
- Decision: the validator accepts an offset bound literal only if it is numeric or a day-time `INTERVAL`.
- The agent planned to give a failing bound literal the old rejection message too.
- Decision: the key type check runs at planning time in `Windowing.getWindowFrame`.
- The reason is that the row signature `sig` is available there.
- Decision: planning-time rejections in `Windowing` will throw `QueryException` with `SQL_QUERY_UNSUPPORTED_ERROR_CODE`, like its existing direction check.
- The agent found earlier that `isLongType` counts `TIMESTAMP` as a long type, so the row signature reports timestamp keys as `LONG`.
- The agent found earlier that `Windowing.java` has no range branch.
- The agent judged that `RANGE` frames with only `UNBOUNDED` or `CURRENT ROW` bounds on `STRING` keys work today through the `groups(...)` frame.
- Decision: `Windowing.WindowGroup.getWindowFrame()` will keep the `groups(...)` path when no bound is a `PRECEDING` or `FOLLOWING` offset.
- Decision: `Windowing.WindowGroup.getWindowFrame()` will emit `WindowFrame.range(...)` only when at least one bound is a `PRECEDING` or `FOLLOWING` offset.
- The reason is that this keeps all existing behavior and tests.
- The agent found earlier that `RexWindowBound` exposes `getOffset()`.
- The agent judged earlier that frame offsets reach `Windowing` as `RexInputRef` entries into `window.constants`.
- The agent judged earlier that the constant is read as `window.constants.get(refIndex - sig.size()).getValue()`.
- Decision: the planned `RANGE` branch will read offsets through a new `getBoundAsDouble` reader that takes `doubleValue()` from the offset constant's `Number`, instead of `getBoundAsInteger`.
- The reason is that `Range` offsets are `Double` values.
- The planned `getBoundAsDouble` returns null for an unbounded bound.
- The planned `getBoundAsDouble` returns 0.0 for a `CURRENT ROW` bound.
- The planned `getBoundAsDouble` returns the negated value for a `PRECEDING` bound.
- The planned `getBoundAsDouble` returns the value as it is for a `FOLLOWING` bound.
- The agent found earlier that a day-time `INTERVAL` literal holds milliseconds, from `SqlParserUtil.intervalToMillis`.
- The agent found earlier that a year-month `INTERVAL` literal holds months, from `intervalToMonths`.
- Decision: year-month `INTERVAL` bounds are rejected.
- The agent judged that `RewriteFirstValueLastValueRule` does not interfere with offset `RANGE` frames.
- The agent found earlier that `testUnSupportedRangeBounds` runs `ROW_NUMBER() OVER (ORDER BY dim1 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING)`.
- The agent judged that this query will now pass, because `ROW_NUMBER` never calls `getWindowFrame()`.
- Decision: `testUnSupportedRangeBounds` will switch to a multi-key `ORDER BY dim1, dim2`.
- Decision: `testUnSupportedRangeBounds` will keep expecting the old rejection message.
- `WindowFrameTest` checks frame equality with `EqualsVerifier.forClass(...).usingGetClass().verify()`.

## Work State
### Completed
- No file in `/app` has been edited.
- The agent finished checking the `qaWin` `RANGE` cases for a single `ORDER BY` key.

### Active
- Todo 1, the `WindowFrame.Range` class with the `"range"` subtype and the `range()` factory, is in progress.
- No code for todo 1 is written yet.
- The agent was about to write the `Range` class.

### Blocked
- No item is blocked.

## Next Move
1. Add the `WindowFrame.Range` class to `WindowFrame.java`.
2. Register `Range` as `"range"` in `@JsonSubTypes`.
3. Add the `range(...)` factory.
4. Write the `RangeFrameResolver` class.
5. Make `DefaultFramedOnHeapAggregatable` resolve `Range` frames.
6. Add `Range` handling in `WindowValueProcessorBase`.
7. Relax `DruidSqlValidator.validateWindow` for offset `RANGE` frames.
8. Add a range branch to `Windowing.WindowGroup.getWindowFrame()` that builds `WindowFrame.range(...)`.
9. Update `testUnSupportedRangeBounds`.
10. Write native `Range` tests.
11. Write SQL planner tests for offset `RANGE` frames.
12. Compile the code.
13. Run the tests.
14. Run lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` holds the frame types.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` will resolve `Range` frames for aggregation.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` holds `computeFirstOrLastValueFramed`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` holds `validateWindow`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` holds `getWindowFrame()`.
- `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` holds `testUnSupportedRangeBounds`.
- `/app/quidem-ut/src/test/quidem/org.apache.druid.quidem.QTest/qaWin/` holds the recorded `RANGE` cases.
