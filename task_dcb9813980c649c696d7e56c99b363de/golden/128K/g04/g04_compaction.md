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
- In native resolution, an ordering type that cannot do value arithmetic with a finite offset must throw an unchecked `DruidException`.
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
- The agent found earlier that only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable` in the main code.
- The agent concluded that handling `Range` in `DefaultFramedOnHeapAggregatable` and in the value processors covers every `RowsAndColumns`.
- `WindowFrame.Range` implements `WindowFrame` directly, because the agent judged that `OffsetFrame` has `Integer` offsets.
- Decision: the `Range` constructor does not null-check `orderBy`.
- This replaces an earlier draft with a null check, because the agent judged that `EqualsVerifier` may reject one.
- The agent judged that `compareRows` returns -1 for a null left row, so null keys sort first under `ASC`.
- The agent judged that the sort multiplies `compareRows` by the direction, so null keys sort last under `DESC`.
- The agent judged that `compareRows(null, null)` returns 0, so the `NULL` rows form one peer group.
- `RangeFrameResolver` computes the peer groups.
- `RangeFrameResolver` computes the frame of each peer group.
- The reason is that `DefaultFramedOnHeapAggregatable` and `WindowValueProcessorBase.computeFirstOrLastValueFramed` both need them.
- The peer groups come from `computeBoundaries` on the `ORDER BY` column.
- `RangeFrameResolver` expects input already sorted by the ordering column within each partition.
- The native tests will feed the processors rows already sorted by the ordering column.
- Decision: both users of `RangeFrameResolver` iterate the peer groups directly, without merging adjacent groups that have identical frames, because the agent judged such merging possible but not worth doing.
- `RangeFrameResolver` throws `DruidException.defensive("Column [%s] specified in WindowFrame [%s] does not exist", ...)` when the `ORDER BY` column is missing.
- This message replaces the earlier planned `Column[%s] does not exist`.
- `RangeFrameResolver` also throws `DruidException.defensive("WindowFrame [%s] requires a numeric ordering column, found column [%s] of type [%s]", ...)` when an offset is finite and `accessor.getType().isNumeric()` is false.
- Keys are compared as doubles through `accessor.getDouble(row)`, because the agent judged that `getDouble` treats `LONG`, `FLOAT` and `DOUBLE` keys the same way.
- The agent accepted a precision loss for key values beyond 2^53.
- Under `ASC`, the leading `isNull` rows form the null run.
- Under `DESC`, the trailing `isNull` rows form the null run.
- A `NULL` key group's frame starts at 0 if the lower offset is null, else at the null run start.
- A `NULL` key group's frame ends at `numRows` if the upper offset is null, else at the null run end.
- Under `ASC`, the frame start is the first row whose value is at least the lower bound.
- Under `ASC`, the frame end is the first row whose value is greater than the upper bound, exclusive.
- Under `DESC`, the frame start is the first row whose value is at most the lower bound.
- Under `DESC`, the frame end is the first row whose value is less than the upper bound, exclusive.
- The binary search covers only the non-null rows, because the agent found earlier that `getDouble` on a null row gives 0.0.
- Decision: under `DESC`, when no non-null row is below the upper bound, the frame end is the start of the null run.
- This replaces the plain `DESC` end rule for that case, because the agent found it wrong when the upper bound is below every non-null value and null rows exist.
- Decision: the resolver raises each frame end to at least its frame start, so an empty frame is never an inverted interval.
- The reason is that the agent found that an inverted interval can make the incremental branches of `moveTo` add a wrong row.
- Decision: `moveTo` stays unchanged, which replaces the planned full recompute for `Range` frames.
- The reason is that the agent judged `Range` frame bounds never decrease from one peer group to the next, so the existing `moveTo` stays correct.
- `isEffectivelyUnbounded` treats a `Range` with both offsets null as unbounded.
- Its `Range` branch goes before the `OffsetFrame` unwrap, because the agent judged that the unwrap would fail on a `Range`.
- `buildIteratorFor` sends a `Range` to the new `buildRangeIteratorFor`, which yields one `AggInterval` of group rows and frame rows per peer group.
- In `computeFirstOrLastValueFramed`, a `Range` peer group's `FIRST_VALUE` takes `getObject(frameStart)`.
- In `computeFirstOrLastValueFramed`, a `Range` peer group's `LAST_VALUE` takes `getObject(frameEnd - 1)`.
- A `Range` peer group gets a null value unless `frameStart < frameEnd`.
- The agent concluded that Calcite 1.41 cannot parse `GROUPS` frames, so a false `isRows()` means `RANGE`.
- The agent found earlier that quidem `!error` checks that the squashed stack trace contains the squashed expected text.
- The agent found earlier that the `qaWin` files expect only `QueryInterruptedException` before `!error`.
- The agent judged that any Druid validation or planning error therefore still matches the `qaWin` expectations.
- The agent found earlier that some `qaWin` `RANGE` windows have no `ORDER BY`.
- The agent concluded earlier that no `qaWin` `RANGE` case has exactly one `ORDER BY` key.
- Decision: unsupported `RANGE` forms keep `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.` as the validator rejection message.
- The reason is that the multi-key `RANGE` cases in the `qaWin` quidem files then keep failing.
- Decision: the `qaWin` files are left as recorded.
- Decision: an offset `RANGE` frame with no `ORDER BY` is rejected, because `WindowFrame.range` needs an ordering column.
- `validateWindow` now accepts an offset `RANGE` frame only when `orderList` is not null and has size 1.
- Both bounds must also pass the new `isValidRangeBound`, which accepts a `SqlNumericLiteral` or a day-time `SqlIntervalLiteral` offset.
- Otherwise `validateWindow` still throws the old message through `buildCalciteContextException`.
- Decision: the key type check runs at planning time in `Windowing.getWindowFrame`, because the row signature `sig` is available there.
- `Calcites.isLongType` counts `TIMESTAMP` as a long type.
- The agent judged that timestamp keys therefore show as `LONG` in `sig`.
- The agent judged that `RANGE` frames with only `UNBOUNDED` or `CURRENT ROW` bounds on `STRING` keys work today through the `groups(...)` frame.
- `Windowing.WindowGroup.getWindowFrame()` keeps the `groups(...)` path when no bound is a `PRECEDING` or `FOLLOWING` offset.
- It emits `WindowFrame.range(...)` through the new `buildRangeFrame()` only when at least one bound is a `PRECEDING` or `FOLLOWING` offset.
- The reason is that this keeps all existing behavior and tests.
- `buildRangeFrame()` throws `QueryException` with `SQL_QUERY_UNSUPPORTED_ERROR_CODE` and `Order By with RANGE clause with offset-based bounds requires exactly one ordering key, found [%d]` unless the window has exactly one key.
- It throws the same `QueryException` code with `Order By with RANGE clause with offset-based bounds requires a numeric or timestamp ordering key, found column [%s] of type [%s]` for a non-numeric key.
- Decision: the `RANGE` branch reads offsets through the new `getBoundAsDouble` instead of `getBoundAsInteger`, because `Range` offsets are `Double` values.
- `getBoundAsDouble` returns null for an unbounded bound.
- `getBoundAsDouble` returns 0.0 for a `CURRENT ROW` bound.
- `getBoundAsDouble` returns the negated value for a `PRECEDING` bound.
- `getBoundAsDouble` returns the value as it is for a `FOLLOWING` bound.
- `getBoundAsDouble` reads the constant through the new `getConstantAsDouble`, which takes `doubleValue()` from `window.constants`.
- The reason is that `getConstant` takes `intValue()`, which the agent judged would overflow for interval milliseconds.
- The agent found earlier that a day-time `INTERVAL` literal holds milliseconds, from `SqlParserUtil.intervalToMillis`.
- The agent found earlier that a year-month `INTERVAL` literal holds months, from `intervalToMonths`.
- Decision: year-month `INTERVAL` bounds are rejected.
- The agent judged that `RewriteFirstValueLastValueRule` does not interfere with offset `RANGE` frames.
- `testUnSupportedRangeBounds` runs `ROW_NUMBER() OVER (ORDER BY dim1 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING)` and expects the old message at `(line [1], column [31])`.
- The agent judged that this query will now pass, because `ROW_NUMBER` never calls `getWindowFrame()`.
- Decision: `testUnSupportedRangeBounds` will switch to a multi-key `ORDER BY dim1, dim2`.
- Decision: `testUnSupportedRangeBounds` will keep expecting the old rejection message and column 31.
- The agent found earlier that `WindowFrameTest` checks frame equality with `EqualsVerifier.forClass(...).usingGetClass().verify()`.
- `QueryException` extends `RuntimeException`.
- No `CalciteQueryTest` test asserts `SQL_QUERY_UNSUPPORTED`.
- The agent planned to try `assertThrows(QueryException.class, ...)` for a `SUM` over a `STRING` key with an offset `RANGE` frame.
- A SQL `Range` test needs a `PRECEDING` or `FOLLOWING` offset bound.
- The agent judged that `m1` in `druid.foo` runs from 1.0 to 6.0 in `__time` order.
- The grep tool fails with `ripgrep execution failed`, so the agent uses `grep` in bash.

## Work State
### Completed
- `WindowFrame.Range` is written in `WindowFrame.java`.
- The `"range"` subtype is registered.
- The `range(...)` factory is written.
- `RangeFrameResolver.java` is written.
- `DefaultFramedOnHeapAggregatable` resolves `Range` frames.
- `WindowValueProcessorBase.computeFirstOrLastValueFramed` handles `Range` frames.
- `DruidSqlValidator.validateWindow` is relaxed for offset `RANGE` frames.
- `Windowing.WindowGroup.getWindowFrame()` builds `Range` frames.
- `mvn compile -pl processing,sql -am -Pskip-static-checks -Dweb.console.skip=true -T1C` ended with `BUILD SUCCESS`.

### Active
- The agent was about to write the native `Range` tests.

### Blocked
- No item is blocked.

## Next Move
1. Add a `Range` `EqualsVerifier` test to `WindowFrameTest`.
2. Write `Range` tests in `WindowFirstProcessorTest`.
3. Write `Range` tests in `WindowLastProcessorTest`.
4. Write `Range` tests in `WindowFramedAggregateProcessorTest`.
5. Change `testUnSupportedRangeBounds` to `ORDER BY dim1, dim2`.
6. Write SQL `RANGE` tests in `CalciteQueryTest`.
7. Run the tests.
8. Run lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` holds `Range`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/RangeFrameResolver.java` resolves `Range` frames.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` holds `buildRangeIteratorFor`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` holds `computeFirstOrLastValueFramed`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` holds `validateWindow`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` holds `buildRangeFrame()`.
- `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` holds `testUnSupportedRangeBounds`.
