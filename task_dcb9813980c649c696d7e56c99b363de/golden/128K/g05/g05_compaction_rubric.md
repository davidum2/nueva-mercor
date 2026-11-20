# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the objective of adding native value-based `RANGE` window framing to Druid as `WindowFrame.Range` with Jackson subtype `"range"`, together with SQL validator and planner support and native and SQL test coverage.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that success requires the native `Range` tests and the SQL `RANGE` tests in `CalciteQueryTest` to pass.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that multi-key `RANGE` queries must still fail with the existing validator message `Order By with RANGE clause currently supports only UNBOUNDED or CURRENT ROW. Use ROWS clause instead.`
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that success requires lint and static checks to pass on the touched modules.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: minor
Description:
States that a null offset on a bound of `WindowFrame.Range` means that side of the frame is positionally unbounded.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
States that `Range` bounds compute as `v + o` under `ASC` and `v - o` under `DESC` with the frame as the closed interval `[lowerBound, upperBound]`.
````

## Criterion 7

````text
ID: criteria_6
Category: Decision rationale
Weight: major
Description:
States that `WindowFrame.Range` implements `WindowFrame` directly rather than extending `OffsetFrame` because `OffsetFrame` carries `Integer` offsets.
````

## Criterion 8

````text
ID: criteria_7
Category: Decision rationale
Weight: major
Description:
States that empty `Range` frames yield `null` rather than 0 because `SUM` of zero rows is `NULL` per SQL semantics.
````

## Criterion 9

````text
ID: criteria_8
Category: Decision rationale
Weight: major
Description:
States that `getConstantAsDouble` reads offsets via `doubleValue()` because `intValue()` would overflow interval milliseconds.
````

## Criterion 10

````text
ID: criteria_9
Category: Decision rationale
Weight: major
Description:
States that the `qaWin` quidem files are left as recorded because no `qaWin` `RANGE` case has exactly one `ORDER BY` key.
````

## Criterion 11

````text
ID: criteria_10
Category: Decision rationale
Weight: minor
Description:
States that `RewriteFirstValueLastValueRule` only rewrites default frames so explicit `RANGE` bounds flow to the processors unchanged.
````

## Criterion 12

````text
ID: criteria_11
Category: Decision rationale
Weight: minor
Description:
States that the constructor of `WindowFrame.Range` does not null-check `orderBy` for `EqualsVerifier` considerations.
````

## Criterion 13

````text
ID: criteria_12
Category: Temporal coherence
Weight: major
Description:
States that all native `Range` tests pass in `WindowFrameTest`, `WindowFirstProcessorTest`, `WindowLastProcessorTest`, and `WindowFramedAggregateProcessorTest`.
````

## Criterion 14

````text
ID: criteria_13
Category: Temporal coherence
Weight: major
Description:
States that `testUnSupportedRangeBoundsOnStringKey` currently fails because Calcite validation rejects the STRING ordering key query with `DruidException` from `DruidPlanner.parseValidationMessage` rather than the expected `QueryException`.
````

## Criterion 15

````text
ID: criteria_14
Category: Temporal coherence
Weight: major
Description:
States the pending fix of changing the assertion in `testUnSupportedRangeBoundsOnStringKey` to `assertThrows(DruidException.class, ...)` with `assertDruidException(e, invalidSqlIs("Data type of ORDER BY prohibits use of RANGE clause (line [1], column [55])"))`, matching the pattern of `testUnSupportedNullsFirst`.
````

## Criterion 16

````text
ID: criteria_15
Category: Temporal coherence
Weight: major
Description:
States that the positive `testRangeFrame*` tests and `testUnSupportedRangeBounds` pass in the SQL test run.
````

## Criterion 17

````text
ID: criteria_16
Category: Temporal coherence
Weight: major
Description:
Lists the next steps as applying the `testUnSupportedRangeBoundsOnStringKey` fix, re-running the SQL tests, running lint and static checks on the `processing` and `sql` modules, and a final full verification run of all touched test classes.
````

## Criterion 18

````text
ID: criteria_17
Category: Temporal coherence
Weight: major
Description:
States that `testUnSupportedRangeBounds` uses `ORDER BY dim1, dim2` and passes with the same validator message.
````

## Criterion 19

````text
ID: criteria_18
Category: Temporal coherence
Weight: minor
Description:
States that the failing native test expectations came from miscomputed frame bounds while the `RangeFrameResolver` implementation was verified correct via a debug frame dump.
````

## Criterion 20

````text
ID: criteria_19
Category: Temporal coherence
Weight: negative
Description:
States that the temporary `RangeDebugTest` debug test is still present in the processing test sources.
````

## Criterion 21

````text
ID: criteria_20
Category: Temporal coherence
Weight: negative
Description:
States that `RewriteFirstValueLastValueRule` was edited to pass explicit `RANGE` bounds through to the processors.
````

## Criterion 22

````text
ID: criteria_21
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/operator/window/WindowFrame.java` as holding `Range`, the `"range"` subtype registration, and the `range(...)` factory.
````

## Criterion 23

````text
ID: criteria_22
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/operator/window/RangeFrameResolver.java` as computing `Range` peer groups and per-group frames.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/rowsandcols/semantic/DefaultFramedOnHeapAggregatable.java` as holding `buildRangeIteratorFor` and `isEffectivelyUnbounded`.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
Names `/app/processing/src/main/java/org/apache/druid/query/operator/window/value/WindowValueProcessorBase.java` as holding `computeFirstOrLastValueFramed`.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
Names `/app/sql/src/main/java/org/apache/druid/sql/calcite/planner/DruidSqlValidator.java` as holding `validateWindow` and `isValidRangeBound`.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
Names `/app/sql/src/main/java/org/apache/druid/sql/calcite/rel/Windowing.java` as holding `buildRangeFrame()`.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
Names `/app/sql/src/test/java/org/apache/druid/sql/calcite/CalciteQueryTest.java` as holding the new `RANGE` SQL tests.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFrame.Range` carries `@Nullable Double lowerOffset`, `@Nullable Double upperOffset`, and non-null `ColumnWithDirection orderBy` with static factory `WindowFrame.range(@Nullable Double, @Nullable Double, ColumnWithDirection)` and value-based equals and hashCode.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
States that `RangeFrameResolver` computes peer groups via `ClusteredGroupPartitioner.fromRAC(rac).computeBoundaries(ImmutableList.of(orderColumn))` and expects pre-sorted input with nulls clustering first under `ASC` and last under `DESC`.
````

## Criterion 31

````text
ID: criteria_30
Category: Artifact preservation
Weight: minor
Description:
States that a missing ordering column raises `DruidException.defensive("Column [%s] specified in WindowFrame [%s] does not exist", ...)`.
````

## Criterion 32

````text
ID: criteria_31
Category: Artifact preservation
Weight: minor
Description:
States that a finite offset on a non-numeric ordering column raises `DruidException.defensive("WindowFrame [%s] requires a numeric ordering column, found column [%s] of type [%s]", ...)`.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: minor
Description:
States that `QueryException` extends `RuntimeException` with constant `SQL_QUERY_UNSUPPORTED_ERROR_CODE` set to `"SQL query is unsupported"`.
````

## Criterion 34

````text
ID: criteria_33
Category: Artifact preservation
Weight: minor
Description:
States that `Windowing.buildRangeFrame()` throws `QueryException` for a multi-key or non-numeric ordering key.
````

## Criterion 35

````text
ID: criteria_34
Category: Artifact preservation
Weight: minor
Description:
States that `DruidSqlValidator.validateWindow` accepts offset `RANGE` only with exactly one `ORDER BY` key whose bounds pass `isValidRangeBound` as a `SqlNumericLiteral` or a day-time `SqlIntervalLiteral`, and rejects year-month intervals.
````

## Criterion 36

````text
ID: criteria_35
Category: Artifact preservation
Weight: minor
Description:
States that `Windowing.getWindowFrame()` builds `WindowFrame.range(...)` via `buildRangeFrame()` only when a bound is `PRECEDING` or `FOLLOWING`, otherwise keeping the `groups(...)` path.
````

## Criterion 37

````text
ID: criteria_36
Category: Artifact preservation
Weight: minor
Description:
States that `WindowFirstProcessorTest`, `WindowLastProcessorTest`, and `WindowFramedAggregateProcessorTest` gained new `Range` tests including `testFirstWithRangeFrame`, `testLastWithRangeFrame`, and `testRangeFrameWithSum`.
````

## Criterion 38

````text
ID: criteria_37
Category: Artifact preservation
Weight: minor
Description:
States the six new positive SQL test names `testRangeFrameAsc`, `testRangeFrameDesc`, `testRangeFrameUnboundedPrecedingAndCurrentRow`, `testRangeFrameCurrentRowAndUnboundedFollowing`, `testRangeFrameInterval`, and `testRangeFrameFirstLastValue`.
````

## Criterion 39

````text
ID: criteria_38
Category: Artifact preservation
Weight: minor
Description:
States that the `druid.foo` test data types are `m1` as FLOAT, `m2` as DOUBLE, and `cnt` as LONG per `TestDataBuilder.INDEX_SCHEMA`, with SQL tests boxing expected values as `1.0f`, `3.0D`, and `2L` to match.
````

## Criterion 40

````text
ID: criteria_39
Category: Artifact preservation
Weight: minor
Description:
States that window SQL tests need `assumeFeatureAvailable(EngineFeature.WINDOW_FUNCTIONS)` and `msqIncompatible()`.
````

## Criterion 41

````text
ID: criteria_40
Category: Artifact preservation
Weight: minor
Description:
States that the grep tool fails with `ripgrep execution failed` so `grep` runs via bash.
````

## Criterion 42

````text
ID: criteria_41
Category: Artifact preservation
Weight: minor
Description:
States that `mvn surefire:test` does not recompile test classes so `mvn test` is used after test edits.
````

## Criterion 43

````text
ID: criteria_42
Category: Artifact preservation
Weight: minor
Description:
States that `mvn test-compile -pl sql` needs `-am` so sql builds against fresh processing classes.
````

## Criterion 44

````text
ID: criteria_43
Category: Artifact preservation
Weight: minor
Description:
States the test command pattern `mvn test -pl processing -Dtest="..." -Dsurefire.failIfNoSpecifiedTests=false -Pskip-static-checks -Dweb.console.skip=true -T1C`.
````

## Criterion 45

````text
ID: criteria_44
Category: Compression efficiency
Weight: minor
Description:
Contains at most 15100 characters.
````

## Criterion 46

````text
ID: criteria_45
Category: Structural clarity
Weight: minor
Description:
Organizes completed changes, the currently failing test, and the next steps as separate groups of related facts.
````

## Criterion 47

````text
ID: criteria_46
Category: Decision rationale
Weight: negative
Description:
States that `WindowFrame.Range` extends `OffsetFrame` with `Integer` offsets.
````
