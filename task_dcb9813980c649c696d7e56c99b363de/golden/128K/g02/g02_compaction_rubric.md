# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the goal of adding native value-based `RANGE` window framing to Druid in `/app` through a new `WindowFrame.Range` type, frame resolution in the native window engine, and SQL validator and Calcite planning support.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that single-key numeric and timestamp offset `RANGE` frames must work end-to-end while unsupported forms such as multi-key and non-numeric keys keep failing.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that the recorded qaWin `orderby_range_*` quidem cases must keep failing after the change.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that `testUnSupportedRangeBounds` in `CalciteQueryTest.java` must be updated because its single STRING key `ROW_NUMBER()` query would succeed once offset `RANGE` is planned.
````

## Criterion 5

````text
ID: criteria_4
Category: Decision rationale
Weight: major
Description:
Records the decision that offset `RANGE` passes validation only when the window `orderList.size() == 1` and each bound literal is numeric or a day-time INTERVAL, with year-month INTERVAL rejected.
````

## Criterion 6

````text
ID: criteria_5
Category: Decision rationale
Weight: major
Description:
Records the decision that offsets are signed distances with PRECEDING negative, FOLLOWING positive, `CURRENT ROW` as 0.0, and null meaning UNBOUNDED.
````

## Criterion 7

````text
ID: criteria_6
Category: Decision rationale
Weight: major
Description:
Specifies the resolution algorithm where ASC sets frameStart to the first row with value >= lowerBound and frameEnd exclusive to the first row with value > upperBound, and DESC sets frameStart to the first row with value <= lowerBound and frameEnd to the first row with value < upperBound.
````

## Criterion 8

````text
ID: criteria_7
Category: Decision rationale
Weight: major
Description:
Records the planner split where the `groups(...)` path is kept when both bounds are UNBOUNDED or CURRENT ROW and `WindowFrame.range(...)` is emitted only when at least one bound is a PRECEDING or FOLLOWING offset.
````

## Criterion 9

````text
ID: criteria_8
Category: Decision rationale
Weight: major
Description:
Records that an ordering type that cannot do value arithmetic with a finite offset must throw an unchecked `DruidException`.
````

## Criterion 10

````text
ID: criteria_9
Category: Decision rationale
Weight: minor
Description:
Records the decision to keep the existing rejection message `"Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead."` for unsupported cases.
````

## Criterion 11

````text
ID: criteria_10
Category: Decision rationale
Weight: minor
Description:
Records that `getBoundAsInteger` was rejected because it keeps only `intValue()` while `Range` offsets are `Double` values.
````

## Criterion 12

````text
ID: criteria_11
Category: Decision rationale
Weight: minor
Description:
Records that the Calcite 1.41 frame grammar only produces ROWS and RANGE so GROUPS is not parseable and `!SqlWindow.isRows()` means RANGE.
````

## Criterion 13

````text
ID: criteria_12
Category: Decision rationale
Weight: minor
Description:
Records that `Quidem` `!error` matching uses `squash(stackTrace).contains(squash(expectedText))` so any Druid-wrapped validation or planning error matches the expected `QueryInterruptedException`.
````

## Criterion 14

````text
ID: criteria_13
Category: Decision rationale
Weight: minor
Description:
Records that the resolver performs its own binary search because `BinarySearchableAccessor` assumes a sorted column.
````

## Criterion 15

````text
ID: criteria_14
Category: Decision rationale
Weight: minor
Description:
Records that `RewriteFirstValueLastValueRule` only rewrites CURRENT ROW bounds so it does not interfere with offset `RANGE`.
````

## Criterion 16

````text
ID: criteria_15
Category: Decision rationale
Weight: minor
Description:
Records that bound values are computed as `v + o` when ASC and `v - o` when DESC with the frame as the closed interval between its lower and upper bound.
````

## Criterion 17

````text
ID: criteria_16
Category: Decision rationale
Weight: minor
Description:
Records that a NULL current row with finite bounds resolves to the boundaries of the contiguous NULL run while unbounded bounds stay positional at 0 or numRows.
````

## Criterion 18

````text
ID: criteria_17
Category: Decision rationale
Weight: minor
Description:
Records that peers with equal keys get identical bounds and output.
````

## Criterion 19

````text
ID: criteria_18
Category: Decision rationale
Weight: minor
Description:
Records that the resolution search is restricted to the non-null region where nulls sort first under ASC and last under DESC.
````

## Criterion 20

````text
ID: criteria_19
Category: Temporal coherence
Weight: major
Description:
Records that no file has been edited and `git status` in `/app` reported a clean working tree.
````

## Criterion 21

````text
ID: criteria_20
Category: Temporal coherence
Weight: major
Description:
Records that the full design is finalized while no code for `WindowFrame.Range` has been written yet.
````

## Criterion 22

````text
ID: criteria_21
Category: Temporal coherence
Weight: major
Description:
Lists the next steps of writing `WindowFrame.Range` in `WindowFrame.java`, writing the shared Range frame resolver in `org.apache.druid.query.operator.window`, wiring `DefaultFramedOnHeapAggregatable` and `WindowValueProcessorBase.computeFirstOrLastValueFramed`, relaxing `DruidSqlValidator.validateWindow`, adding the `Windowing.getWindowFrame` range branch with `getBoundAsDouble`, and updating `testUnSupportedRangeBounds`.
````

## Criterion 23

````text
ID: criteria_22
Category: Temporal coherence
Weight: minor
Description:
Includes running `mvn compile`, the affected processing, sql, and quidem qaWin tests, and lint as the final next step.
````

## Criterion 24

````text
ID: criteria_23
Category: Temporal coherence
Weight: minor
Description:
Records that a python3 balanced-paren scan of the qaWin `orderby_range_*.iq` files found every RANGE query is either no-ORDER-BY or multi-key with none having a single ORDER BY key.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` must be a public nested class of `WindowFrame` registered as the Jackson subtype `"range"`.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` carries `@Nullable Double lowerOffset` and `@Nullable Double upperOffset` with a non-null `ColumnWithDirection orderBy`.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` exposes `getLowerOffset()`, `getUpperOffset()`, and `getOrderBy()` alongside the static factory `WindowFrame.range(@Nullable Double, @Nullable Double, ColumnWithDirection)`.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` supports equals and hashCode by value, `toString`, and Jackson ser/de.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
States that `FramedOnHeapAggregatable#aggregateAll`, `WindowFramedAggregateProcessor`, `WindowFirstProcessor`, and `WindowLastProcessor` must accept `Range`.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
States that the shared resolver lives in `org.apache.druid.query.operator.window` and exposes peer-group boundaries plus per-group frameStart and frameEnd.
````

## Criterion 31

````text
ID: criteria_30
Category: Artifact preservation
Weight: minor
Description:
States that peer-group boundaries are computed via `ClusteredGroupPartitioner.fromRAC(rac).computeBoundaries([orderByColumn])` with nulls forming one peer group because `compareRows(null, null) == 0`.
````

## Criterion 32

````text
ID: criteria_31
Category: Artifact preservation
Weight: minor
Description:
States that value comparisons run in double space via `accessor.getDouble(row)`.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: minor
Description:
States that `getBoundAsDouble` maps unbounded to null, currentRow to 0.0, preceding to `-value`, and following to `+value`.
````

## Criterion 34

````text
ID: criteria_33
Category: Artifact preservation
Weight: minor
Description:
States that a day-time interval `RexLiteral` value is a BigDecimal of millis via `SqlParserUtil.intervalToMillis`.
````

## Criterion 35

````text
ID: criteria_34
Category: Artifact preservation
Weight: minor
Description:
States that the planning key type check uses `sig.getColumnType(fieldIndex)` restricted to LONG, FLOAT, and DOUBLE, with TIMESTAMP mapping to LONG.
````

## Criterion 36

````text
ID: criteria_35
Category: Artifact preservation
Weight: minor
Description:
States that `ColumnWithDirection` encodes `ASC(1)` and `DESC(-1)` read via `getDirectionInt()`.
````

## Criterion 37

````text
ID: criteria_36
Category: Artifact preservation
Weight: minor
Description:
States that `updateBoundsIfNeeded` turns the single bound `RANGE 0 FOLLOWING` into `RANGE BETWEEN CURRENT ROW AND 0 FOLLOWING`.
````

## Criterion 38

````text
ID: criteria_37
Category: Artifact preservation
Weight: minor
Description:
States that only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable` and concrete RACs such as `QueryableIndexRowsAndColumns` do not override `as()` for it.
````

## Criterion 39

````text
ID: criteria_38
Category: Artifact preservation
Weight: minor
Description:
States that `isEffectivelyUnbounded` for `Range` treats both offsets null as equivalent to `WindowFrame.unbounded()`.
````

## Criterion 40

````text
ID: criteria_39
Category: Artifact preservation
Weight: minor
Description:
States that the aggregation path already handles an empty `Interval` through `AggIntervalCursor.moveTo`, which makes fresh aggregators and returns the zero-row default.
````

## Criterion 41

````text
ID: criteria_40
Category: Artifact preservation
Weight: minor
Description:
States that `FIRST_VALUE` and `LAST_VALUE` return null when frameStart >= frameEnd.
````

## Criterion 42

````text
ID: criteria_41
Category: Artifact preservation
Weight: minor
Description:
Includes adding an EqualsVerifier test for `WindowFrame.Range` in `WindowFrameTest`.
````

## Criterion 43

````text
ID: criteria_42
Category: Artifact preservation
Weight: minor
Description:
Includes adding native `Range` tests in `WindowFramedAggregateProcessorTest` and `WindowFirstProcessorTest` and SQL planner tests for offset `RANGE`.
````

## Criterion 44

````text
ID: criteria_43
Category: Compression efficiency
Weight: minor
Description:
Contains at most 13400 characters.
````

## Criterion 45

````text
ID: criteria_44
Category: Structural clarity
Weight: minor
Description:
Organizes related facts together so that the outstanding work can be found without reading the whole text.
````

## Criterion 46

````text
ID: criteria_45
Category: Artifact preservation
Weight: negative
Description:
States that `WindowFrame.Range` extends `OffsetFrame`.
````

## Criterion 47

````text
ID: criteria_46
Category: Decision rationale
Weight: negative
Description:
States that `getBoundAsDouble` maps an unbounded `RexWindowBound` to 0.0.
````

## Criterion 48

````text
ID: criteria_47
Category: Temporal coherence
Weight: negative
Description:
States that the `WindowFrame.Range` class and its EqualsVerifier test are already written and passing.
````
