# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the objective of implementing a native value-based `RANGE` window frame type `WindowFrame.Range` with Jackson subtype "range" in Apache Druid.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that the implementation extends `FramedOnHeapAggregatable#aggregateAll` and the value processors `WindowFramedAggregateProcessor`, `WindowFirstProcessor`, and `WindowLastProcessor`.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that SQL planning accepts offset-based `RANGE` frames only when the window has exactly one ORDER BY key.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that a full-partition `Range` frame must evaluate identically to `WindowFrame.unbounded()`.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States that an unsupported ordering column type results in an unchecked `DruidException`.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: major
Description:
States that an empty frame yields the aggregator zero-row default and that FIRST_VALUE and LAST_VALUE return `null` on an empty frame.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: major
Description:
States that a frame bound equals `v + o` under ASC ordering and `v - o` under DESC ordering within the closed interval `[lowerBound, upperBound]`.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: major
Description:
States that a null offset means a positionally UNBOUNDED bound and a non-null offset is a signed distance in ordering-key value space.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: major
Description:
States that RANGE forms with non-numeric and non-interval keys under finite bounds must fail validation or planning.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: minor
Description:
States that a NULL current-row key with finite offsets resolves to the boundaries of the contiguous NULL run.
````

## Criterion 11

````text
ID: criteria_10
Category: Goal fidelity
Weight: minor
Description:
States that peer rows receive identical frame boundaries and identical outputs.
````

## Criterion 12

````text
ID: criteria_11
Category: Goal fidelity
Weight: minor
Description:
States that ordering columns of type LONG, FLOAT, and DOUBLE must be supported across all `RowsAndColumns` implementations.
````

## Criterion 13

````text
ID: criteria_12
Category: Goal fidelity
Weight: minor
Description:
States that a day-time INTERVAL bound converts to a millisecond magnitude as a floating-point offset without integer truncation.
````

## Criterion 14

````text
ID: criteria_13
Category: Goal fidelity
Weight: minor
Description:
States that the ordering key for a planned RANGE frame must be numeric or a timestamp and the bound literal numeric or a day-time INTERVAL.
````

## Criterion 15

````text
ID: criteria_14
Category: Goal fidelity
Weight: minor
Description:
States that timestamps reach the native engine as LONG values.
````

## Criterion 16

````text
ID: criteria_15
Category: Decision rationale
Weight: minor
Description:
Explains that RANGE planning needs a double-based bound conversion because `getBoundAsInteger` truncates offsets through `Number.intValue()`.
````

## Criterion 17

````text
ID: criteria_16
Category: Decision rationale
Weight: minor
Description:
Explains that the multi-ORDER-BY-key RANGE queries in the `qaWin` `.iq` files must keep erroring because they expect `QueryInterruptedException` and `!error`.
````

## Criterion 18

````text
ID: criteria_17
Category: Temporal coherence
Weight: major
Description:
Records that no code changes have been written and that `git status` in `/app` reports branch master with a clean working tree.
````

## Criterion 19

````text
ID: criteria_18
Category: Temporal coherence
Weight: major
Description:
Records that the investigation of whether the recorded `QueryInterruptedException` expectation breaks when the validator error message changes is incomplete.
````

## Criterion 20

````text
ID: criteria_19
Category: Temporal coherence
Weight: major
Description:
Specifies implementing the `WindowFrame.Range` nested class in `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` as the next step.
````

## Criterion 21

````text
ID: criteria_20
Category: Temporal coherence
Weight: minor
Description:
Records that the key files `WindowFrame.java`, `DefaultFramedOnHeapAggregatable.java`, `DruidSqlValidator.java`, `Windowing.java`, and `RewriteFirstValueLastValueRule.java` have been read.
````

## Criterion 22

````text
ID: criteria_21
Category: Temporal coherence
Weight: minor
Description:
Lists the eight todo items running from the `WindowFrame.Range` class through aggregation, value processors, validator, planning, native tests, SQL and quidem tests, and compile, test, and lint.
````

## Criterion 23

````text
ID: criteria_22
Category: Temporal coherence
Weight: minor
Description:
Records that nothing is currently blocked.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` carries the fields `@Nullable Double lowerOffset`, `@Nullable Double upperOffset`, and a non-null `ColumnWithDirection orderBy`.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
Specifies the static factory `WindowFrame.range(@Nullable Double, @Nullable Double, ColumnWithDirection orderBy)` for constructing `Range` frames.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
Lists the `WindowFrame.Range` getters `getLowerOffset()`, `getUpperOffset()`, and `getOrderBy()`.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` implements value-based `equals` and `hashCode` and supports Jackson serde.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame` declares the Jackson subtypes "rows" and "groups" under `@JsonTypeInfo(use = Id.NAME, property = "type")`.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.unbounded()` returns `rows(null, null)`.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
States that `ColumnWithDirection.Direction` encodes ASC as 1 and DESC as -1 via `getDirectionInt()` with the factories `ascending(String)` and `descending(String)`.
````

## Criterion 31

````text
ID: criteria_30
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` is a standalone `WindowFrame` implementation that does not extend `OffsetFrame`.
````

## Criterion 32

````text
ID: criteria_31
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/FramedOnHeapAggregatable.java` as the semantic interface for framed aggregation.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` as the default frame resolution implementation.
````

## Criterion 34

````text
ID: criteria_33
Category: Artifact preservation
Weight: minor
Description:
States that Calcite 1.41.0 provides `RexWindowBound` with `isUnboundedPreceding`, `isPreceding`, `isCurrentRow`, and `getOffset`.
````

## Criterion 35

````text
ID: criteria_34
Category: Artifact preservation
Weight: minor
Description:
States that frame bound offsets appear as `RexInputRef` into `window.constants`.
````

## Criterion 36

````text
ID: criteria_35
Category: Artifact preservation
Weight: minor
Description:
States that `SqlWindow.updateBoundsIfNeeded` rewrites the single-bound form `RANGE 0 FOLLOWING` into `RANGE BETWEEN CURRENT ROW AND 0 FOLLOWING`.
````

## Criterion 37

````text
ID: criteria_36
Category: Artifact preservation
Weight: minor
Description:
Records the current validator error message `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.`
````

## Criterion 38

````text
ID: criteria_37
Category: Artifact preservation
Weight: minor
Description:
States that `rg` is not installed and that searching uses `grep` and `find`.
````

## Criterion 39

````text
ID: criteria_38
Category: Artifact preservation
Weight: minor
Description:
States that the tests to follow include `WindowFrameTest.java`, `WindowFramedAggregateProcessorTest.java`, and `WindowFirstProcessorTest.java`.
````

## Criterion 40

````text
ID: criteria_39
Category: Artifact preservation
Weight: minor
Description:
States that the test patterns use `EqualsVerifier.forClass(...).usingGetClass().verify()` with `MapOfColumnsRowsAndColumns`, `IntArrayColumn`, `DoubleArrayColumn`, `ObjectArrayColumn`, and `RowsAndColumnsHelper`.
````

## Criterion 41

````text
ID: criteria_40
Category: Artifact preservation
Weight: minor
Description:
States that `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` contains a ROW_NUMBER query using `RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING`.
````

## Criterion 42

````text
ID: criteria_41
Category: Compression efficiency
Weight: minor
Description:
Contains at most 10300 characters.
````

## Criterion 43

````text
ID: criteria_42
Category: Structural clarity
Weight: minor
Description:
Organizes related facts so that the outstanding work and next steps can be located without reading the entire text.
````

## Criterion 44

````text
ID: criteria_43
Category: Artifact preservation
Weight: negative
Description:
States that `WindowFrame.Range` stores its offsets as `int` values.
````

## Criterion 45

````text
ID: criteria_44
Category: Temporal coherence
Weight: negative
Description:
States that `getWindowFrame()` in `Windowing.java` already builds `WindowFrame.range` frames for RANGE queries.
````

## Criterion 46

````text
ID: criteria_45
Category: Goal fidelity
Weight: negative
Description:
States that FIRST_VALUE and LAST_VALUE return the aggregator zero-row default on an empty frame.
````

## Criterion 47

````text
ID: criteria_46
Category: Artifact preservation
Weight: negative
Description:
States that `WindowFrame.unbounded()` returns a `Groups` frame.
````
