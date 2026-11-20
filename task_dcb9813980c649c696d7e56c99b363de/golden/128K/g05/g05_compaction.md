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
- An empty frame must yield the aggregator's zero-row default, which Druid's existing empty-frame path emits as `null` for sum.
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
- The agent concluded that the `Range` handling covers every `RowsAndColumns`, because it found earlier that only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable` in the main code.
- `WindowFrame.Range` implements `WindowFrame` directly, because the agent judged that `OffsetFrame` has `Integer` offsets.
- Decision: the `Range` constructor does not null-check `orderBy`, because the agent judged that `EqualsVerifier` may reject a null check.
- `RangeFrameResolver` computes the peer groups through `computeBoundaries` on the `ORDER BY` column.
- `RangeFrameResolver` computes the frame of each peer group.
- The reason is that `DefaultFramedOnHeapAggregatable` needs the peer groups.
- `computeFirstOrLastValueFramed` needs them too.
- `RangeFrameResolver` expects input already sorted by the ordering column within each partition.
- The native tests feed the processors rows already sorted by the ordering column.
- Decision: both users of `RangeFrameResolver` iterate the peer groups directly, without merging adjacent groups that have identical frames, because the agent judged such merging possible but not worth doing.
- `RangeFrameResolver` throws `DruidException.defensive("Column [%s] specified in WindowFrame [%s] does not exist", ...)` when the `ORDER BY` column is missing.
- `RangeFrameResolver` also throws `DruidException.defensive("WindowFrame [%s] requires a numeric ordering column, found column [%s] of type [%s]", ...)` when an offset is finite and the key type is not numeric.
- Keys are compared as doubles through `accessor.getDouble(row)`, because the agent judged that `getDouble` treats `LONG`, `FLOAT` and `DOUBLE` keys the same way.
- The agent accepted a precision loss for key values beyond 2^53.
- Under `ASC`, the leading `isNull` rows form the null run.
- Under `DESC`, the trailing `isNull` rows form the null run.
- Under `ASC`, the frame start is the first row whose value is at least the lower bound.
- Under `ASC`, the frame end is the first row whose value is greater than the upper bound, exclusive.
- Under `DESC`, the frame start is the first row whose value is at most the lower bound.
- Under `DESC`, the frame end is the first row whose value is less than the upper bound, exclusive.
- The binary search covers only the non-null rows, because the agent found earlier that `getDouble` on a null row gives 0.0.
- Decision: under `DESC`, when no non-null row is below the upper bound, the frame end is the null run start, because the agent found the plain end rule wrong there when null rows exist.
- Decision: the resolver raises each frame end to at least its frame start, because the agent found that an inverted interval can make the incremental branches of `moveTo` add a wrong row.
- Decision: `moveTo` stays unchanged instead of the planned full recompute, because the agent judged that `Range` frame bounds never decrease from one peer group to the next.
- `isEffectivelyUnbounded` treats a `Range` with both offsets null as unbounded.
- Its `Range` branch goes before the `OffsetFrame` unwrap, because the agent judged that the unwrap would fail on a `Range`.
- `buildIteratorFor` sends a `Range` to the new `buildRangeIteratorFor`.
- `buildRangeIteratorFor` yields one `AggInterval` of group rows and frame rows per peer group.
- A `Range` peer group's `FIRST_VALUE` is `getObject(frameStart)`.
- A `Range` peer group's `LAST_VALUE` is `getObject(frameEnd - 1)`.
- A `Range` peer group gets a null value unless `frameStart < frameEnd`.
- Decision: an empty `Range` frame keeps `null` sum instead of 0, because `RangeDebugTest` empirically showed `ROWS-EMPTY row 0 sum=null` under `WindowFrame.rows(-1, -1)`.
- Although `LongSumAggregator.get()` initializes `sum` to 0, the agent kept `null` to match existing `WindowFrame.rows` empty-frame output.
- Decision: unsupported `RANGE` forms keep the validator message `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.`, because the multi-key `qaWin` `RANGE` cases then keep failing.
- Decision: the `qaWin` files are left as recorded, because the agent judged that any Druid validation or planning error still matches their `!error` expectations.
- The agent concluded earlier that no `qaWin` `RANGE` case has exactly one `ORDER BY` key.
- Decision: an offset `RANGE` frame with no `ORDER BY` is rejected, because `WindowFrame.range` needs an ordering column.
- `validateWindow` now accepts an offset `RANGE` frame only when `orderList` is not null and has size 1.
- Both bounds must also pass the new `isValidRangeBound`.
- `isValidRangeBound` accepts a `SqlNumericLiteral` or a day-time `SqlIntervalLiteral` offset.
- Decision: the key type check runs in `Windowing.getWindowFrame`, because the row signature `sig` is available there.
- The agent found earlier that `Calcites.isLongType` counts `TIMESTAMP` as a long type.
- `Windowing.WindowGroup.getWindowFrame()` keeps the `groups(...)` path when no bound is a `PRECEDING` or `FOLLOWING` offset, because this keeps all existing behavior and tests.
- It emits `WindowFrame.range(...)` through the new `buildRangeFrame()` only when at least one bound is a `PRECEDING` or `FOLLOWING` offset.
- `buildRangeFrame()` throws `QueryException` with `SQL_QUERY_UNSUPPORTED_ERROR_CODE` and `Order By with RANGE clause with offset-based bounds requires exactly one ordering key, found [%d]` unless the window has exactly one key.
- It throws the same `QueryException` code with `Order By with RANGE clause with offset-based bounds requires a numeric or timestamp ordering key, found column [%s] of type [%s]` for a non-numeric key.
- Decision: the `RANGE` branch reads offsets through the new `getBoundAsDouble` instead of `getBoundAsInteger`, because `Range` offsets are `Double` values.
- `getBoundAsDouble` returns null for an unbounded bound.
- `getBoundAsDouble` returns 0.0 for a `CURRENT ROW` bound.
- `getBoundAsDouble` returns the negated value for a `PRECEDING` bound.
- `getBoundAsDouble` returns the value as it is for a `FOLLOWING` bound.
- `getBoundAsDouble` reads the constant through the new `getConstantAsDouble`, because the agent judged that the `intValue()` of `getConstant` would overflow for interval milliseconds.
- `getConstantAsDouble` takes `doubleValue()`.
- The agent found earlier that a day-time `INTERVAL` literal holds milliseconds, from `SqlParserUtil.intervalToMillis`.
- Decision: year-month `INTERVAL` bounds are rejected, because the agent found earlier that such a literal holds months, from `intervalToMonths`.
- `testUnSupportedRangeBounds` now runs `ROW_NUMBER() OVER (ORDER BY dim1, dim2 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING)`.
- It still expects the old message at `(line [1], column [31])`.
- Decision: it uses two keys, because the agent judged that the one-key query could now pass, since `ROW_NUMBER` never calls `getWindowFrame()`.
- The new `testUnSupportedRangeBoundsOnStringKey` runs `SUM(m2) OVER (ORDER BY dim1 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING)` on `druid.foo`.
- It expects a `QueryException` with the code `QueryException.SQL_QUERY_UNSUPPORTED_ERROR_CODE`.
- The agent expects `buildRangeFrame()` to reject the `STRING` key of that query during planning.
- The agent judged that the `QueryException` reaches the test unwrapped, like `CannotBuildQueryException`, because `getWindowFrame()` runs at bind time.
- Decision: the positive SQL `RANGE` tests will check only `expectedResults`, not `expectedQuery`, which the agent called the simplest robust approach.
- The agent noted that the window tests call `msqIncompatible()`.
- The agent judged that the positive SQL tests need `assumeFeatureAvailable(EngineFeature.WINDOW_FUNCTIONS)`.
- The positive SQL tests will have no outer `ORDER BY`, because `testWindowingWithOrderBy` asserts window results without one.
- `testRangeFrameAsc` will expect (1.0, 3.0), (2.0, 6.0), (3.0, 9.0), (4.0, 12.0), (5.0, 15.0), (6.0, 11.0) from `SELECT m1, SUM(m2) OVER (ORDER BY m1 RANGE BETWEEN 1 PRECEDING AND 1 FOLLOWING) FROM foo`.
- `testRangeFrameDesc` will expect the same rows in reverse order from that query with `ORDER BY m1 DESC`.
- `testRangeFrameUnboundedPrecedingCurrentRow` will expect running sums 1, 3, 6, 10, 15, 21 from `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
- `testRangeFrameInterval` will expect (946684800000L, 2L), (946771200000L, 3L), (946857600000L, 2L), (978307200000L, 2L), (978393600000L, 3L), (978480000000L, 2L) from `SUM(cnt)` over `ORDER BY __time RANGE BETWEEN INTERVAL '1' DAY PRECEDING AND INTERVAL '1' DAY FOLLOWING`.
- The agent judged earlier that `RewriteFirstValueLastValueRule` does not interfere with offset `RANGE` frames.
- The agent found earlier that the grep tool fails with `ripgrep execution failed`, so it uses bash `grep`.

## Work State
### Completed
- All main code for `Range` is written.
- `mvn compile -pl processing,sql -am -Pskip-static-checks -Dweb.console.skip=true -T1C` ended with `BUILD SUCCESS`.
- `WindowFrameTest` has the new `testEqualsRange`.
- `WindowFirstProcessorTest` has nine new `Range` tests.
- `WindowLastProcessorTest` has five new `Range` tests.
- `WindowFramedAggregateProcessorTest` has five new `Range` tests.
- The agent corrected nine `Range` tests whose expected values had left boundary rows out of the closed frames.
- `testRangeFrameWithSumEmptyFrames` then failed, because it expected 0 for empty frames.
- The agent deleted `RangeDebugTest`.
- `mvn test -pl processing` with `-Dtest` set to `WindowFrameTest,WindowFirstProcessorTest,WindowLastProcessorTest,WindowFramedAggregateProcessorTest` then ended with 0 failures and `BUILD SUCCESS`.
- `testUnSupportedRangeBounds` is updated.
- `testUnSupportedRangeBoundsOnStringKey` is written.

### Active
- The agent is about to write the positive SQL `RANGE` tests in `CalciteQueryTest`.

### Blocked
- No item is blocked.

## Next Move
1. Read `RewriteFirstValueLastValueRule.java` before writing the `FIRST_VALUE` and `LAST_VALUE` test.
2. Confirm the `druid.foo` column types before writing the expected values.
3. Add `testRangeFrameAsc` to `CalciteQueryTest`.
4. Add `testRangeFrameDesc`.
5. Add `testRangeFrameUnboundedPrecedingCurrentRow`.
6. Add `testRangeFrameInterval`.
7. Add the `FIRST_VALUE` and `LAST_VALUE` `RANGE` test.
8. Run the changed `CalciteQueryTest` tests with `mvn test`, because `mvn surefire:test` reran stale test classes.
9. Run lint.

## Relevant Files
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` holds `Range`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/RangeFrameResolver.java` resolves `Range` frames.
- `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` holds `buildRangeIteratorFor`.
- `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` holds `computeFirstOrLastValueFramed`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` holds `validateWindow`.
- `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` holds `buildRangeFrame()`.
- `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` holds the SQL tests.
