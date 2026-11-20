# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States that the objective is to add native value-based `RANGE` window framing to Druid in `/app`, covering a `WindowFrame.Range` type, native frame resolution for the aggregation and value processors, SQL validator and planner wiring, and tests.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that multi-key `RANGE` queries must still fail.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
Records the verbatim validator message `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.`
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: minor
Description:
States that a null offset leaves a frame side positionally unbounded while a non-null offset is a signed distance in the key's value space.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: minor
Description:
States that a finite bound is `v + o` under `ASC` and `v - o` under `DESC`, with the frame as the closed interval between bounds.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
States that when the current key is `NULL`, finite bounds resolve to the edges of the contiguous `NULL` run.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: minor
Description:
States that an empty frame yields a zero-row default and `null` for `FIRST_VALUE` and `LAST_VALUE`.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: minor
Description:
States that a non-numeric order-by key with a finite offset must throw an unchecked `DruidException`.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: minor
Description:
States that `LONG`, `FLOAT`, and `DOUBLE` keys work and that timestamps arrive as `LONG`.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: negative
Description:
States that the task requires supporting `RANGE` frames over non-numeric order-by keys.
````

## Criterion 11

````text
ID: criteria_10
Category: Artifact preservation
Weight: minor
Description:
Identifies `WindowFrame.Range` as a public nested class of `WindowFrame` registered as the Jackson subtype `"range"`.
````

## Criterion 12

````text
ID: criteria_11
Category: Artifact preservation
Weight: minor
Description:
Specifies the `Range` fields `@Nullable Double lowerOffset` and `@Nullable Double upperOffset` with non-null `ColumnWithDirection orderBy` and the factory `WindowFrame.range(@Nullable Double lowerOffset, @Nullable Double upperOffset, ColumnWithDirection orderBy)`.
````

## Criterion 13

````text
ID: criteria_12
Category: Artifact preservation
Weight: minor
Description:
Records the `Range` getters `getLowerOffset()`, `getUpperOffset()`, and `getOrderBy()`.
````

## Criterion 14

````text
ID: criteria_13
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/operator/window/RangeFrameResolver.java` as the created resolver class with the constructor `(RowsAndColumns rac, WindowFrame.Range frame)`.
````

## Criterion 15

````text
ID: criteria_14
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` as edited to add the `Range` branch in `buildIteratorFor` and the new `buildRangeIteratorFor`.
````

## Criterion 16

````text
ID: criteria_15
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` as edited to add the `Range` branch in `computeFirstOrLastValueFramed`.
````

## Criterion 17

````text
ID: criteria_16
Category: Artifact preservation
Weight: minor
Description:
Names `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` as edited to add `buildRangeFrame`, `getBoundAsDouble`, `getConstantAsDouble`, and the `ColumnType` import.
````

## Criterion 18

````text
ID: criteria_17
Category: Artifact preservation
Weight: minor
Description:
Names `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` as edited to relax `validateWindow` and add `isValidRangeBound`.
````

## Criterion 19

````text
ID: criteria_18
Category: Artifact preservation
Weight: minor
Description:
Lists `WindowFrameTest.java`, `WindowFirstProcessorTest.java`, `WindowLastProcessorTest.java`, and `WindowFramedAggregateProcessorTest.java` as edited with new range tests.
````

## Criterion 20

````text
ID: criteria_19
Category: Artifact preservation
Weight: minor
Description:
Records that `WindowFramedAggregateProcessor.process` falls back to `DefaultFramedOnHeapAggregatable` when `as(FramedOnHeapAggregatable.class)` returns null.
````

## Criterion 21

````text
ID: criteria_20
Category: Artifact preservation
Weight: minor
Description:
Records that `rg` is not installed so `bash` with `grep` is used for searching.
````

## Criterion 22

````text
ID: criteria_21
Category: Artifact preservation
Weight: minor
Description:
Describes the foo test data in `TestDataBuilder.RAW_ROWS1` as six rows with `m1` FLOAT and `m2` DOUBLE running 1.0 through 6.0 and `cnt` of 1 per row.
````

## Criterion 23

````text
ID: criteria_22
Category: Artifact preservation
Weight: negative
Description:
States that `WindowFrame.Range` extends `OffsetFrame`.
````

## Criterion 24

````text
ID: criteria_23
Category: Decision rationale
Weight: major
Description:
Explains that `WindowFrame.Range` implements `WindowFrame` directly rather than extending `OffsetFrame` because `OffsetFrame` uses `Integer` offsets.
````

## Criterion 25

````text
ID: criteria_24
Category: Decision rationale
Weight: major
Description:
Explains that `isEffectivelyUnbounded` checks the `Range` case before the `OffsetFrame` unwrap because the unwrap would otherwise NPE or misbehave.
````

## Criterion 26

````text
ID: criteria_25
Category: Decision rationale
Weight: major
Description:
Explains that `getConstantAsDouble` reads window constants as doubles because `getBoundAsInteger` would overflow day-time interval millis through `intValue()`.
````

## Criterion 27

````text
ID: criteria_26
Category: Decision rationale
Weight: major
Description:
Explains that frame ends are normalized as `frameEnds = Math.max(frameStarts, frameEnds)` because `AggIntervalCursor.moveTo` breaks on inverted intervals.
````

## Criterion 28

````text
ID: criteria_27
Category: Decision rationale
Weight: major
Description:
Explains that key-type rejection happens at planning time rather than validation so a single-key STRING offset RANGE passes validation and throws `QueryException` during planning.
````

## Criterion 29

````text
ID: criteria_28
Category: Decision rationale
Weight: major
Description:
Explains that `testUnSupportedRangeBounds` must switch to `ORDER BY dim1, dim2` because `ROW_NUMBER()` never calls `getWindowFrame()`.
````

## Criterion 30

````text
ID: criteria_29
Category: Decision rationale
Weight: minor
Description:
Explains that `getWindowFrame` keeps `groups(...)` for UNBOUNDED and CURRENT-ROW-only bounds because STRING keys with those bounds work today via `groups`.
````

## Criterion 31

````text
ID: criteria_30
Category: Decision rationale
Weight: minor
Description:
Explains that the validator message is kept verbatim so the `qaWin` multi-key cases keep failing and the `qaWin` files stay as recorded.
````

## Criterion 32

````text
ID: criteria_31
Category: Decision rationale
Weight: minor
Description:
Explains that `Range` must work for every `RowsAndColumns` because only `DefaultFramedOnHeapAggregatable` implements `FramedOnHeapAggregatable`.
````

## Criterion 33

````text
ID: criteria_32
Category: Decision rationale
Weight: minor
Description:
Explains that the binary searches in `RangeFrameResolver` run over the non-null region only because `getDouble` on a null row gives 0.0.
````

## Criterion 34

````text
ID: criteria_33
Category: Decision rationale
Weight: minor
Description:
Explains that `moveTo` stays unchanged because Range bounds are monotone non-decreasing across groups.
````

## Criterion 35

````text
ID: criteria_34
Category: Temporal coherence
Weight: major
Description:
Records that the main sources compile with BUILD SUCCESS under `mvn compile -pl processing,sql -am -Pskip-static-checks -Dweb.console.skip=true -T1C`.
````

## Criterion 36

````text
ID: criteria_35
Category: Temporal coherence
Weight: major
Description:
Records that the test-source edits have not yet been compiled or run, so the first test run will be their first compile.
````

## Criterion 37

````text
ID: criteria_36
Category: Temporal coherence
Weight: major
Description:
Records that the SQL tests for `CalciteQueryTest` are designed but not yet written.
````

## Criterion 38

````text
ID: criteria_37
Category: Temporal coherence
Weight: major
Description:
Records the open question of how the planning-time `QueryException` surfaces through `testBuilder().run()`, to be settled empirically before the negative SQL test is written.
````

## Criterion 39

````text
ID: criteria_38
Category: Temporal coherence
Weight: major
Description:
Specifies the next steps of editing `CalciteQueryTest.java`, running the window and Calcite query tests, and running lint checks.
````

## Criterion 40

````text
ID: criteria_39
Category: Temporal coherence
Weight: minor
Description:
Specifies the planned `testUnSupportedRangeBounds` update to `SELECT dim1,ROW_NUMBER() OVER (ORDER BY dim1, dim2 RANGE BETWEEN 3 PRECEDING AND 2 FOLLOWING) from druid.foo` keeping the `(line [1], column [31])` error position.
````

## Criterion 41

````text
ID: criteria_40
Category: Temporal coherence
Weight: minor
Description:
Records the expected results `(1,3),(2,6),(3,9),(4,12),(5,15),(6,11)` for the planned `SUM(m2) OVER (ORDER BY m1 RANGE BETWEEN 1 PRECEDING AND 1 FOLLOWING)` test.
````

## Criterion 42

````text
ID: criteria_41
Category: Temporal coherence
Weight: minor
Description:
Records the expected cumulative sum 1, 3, 6, 10, 15, 21 for the `UNBOUNDED PRECEDING AND CURRENT ROW` variant.
````

## Criterion 43

````text
ID: criteria_42
Category: Temporal coherence
Weight: negative
Description:
States that the added range tests have been run and pass.
````

## Criterion 44

````text
ID: criteria_43
Category: Compression efficiency
Weight: minor
Description:
Contains at most 16300 characters.
````

## Criterion 45

````text
ID: criteria_44
Category: Structural clarity
Weight: minor
Description:
Separates the completed edits from the remaining SQL test work so the outstanding work can be found without reading the whole summary.
````
