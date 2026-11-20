# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States that the user requested a public instance method `selectMaxWeight` on the existing `Layer` class taking a single `ToDoubleFunction<Annotation>` and returning a new anonymous `Layer` of the same section holding the maximum-weight subset of non-overlapping annotations.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that the user requested a `best-disjoint` operator in the `nav` library.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that two annotations overlap when each starts before the other ends, so touching spans do not overlap.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: minor
Description:
States that a zero-length annotation overlaps only annotations extending on both sides of its position.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States that `Double.NaN` weights normalize to 0.0 while every other value, including positive and negative infinity, contributes unclamped.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
States that the empty subset at total 0.0 is always a candidate.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: major
Description:
States that a subset whose total is NaN is never selected, so an annotation weighted negative infinity never appears in the selection.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: major
Description:
States that equal totals, compared as plain doubles, break to the lexicographically least member indices in the layer's canonical order, with a strict prefix comparing as less.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: major
Description:
States that the operator takes the four forms `best-disjoint:LAYER`, `best-disjoint:LAYER(WEIGHT)`, `best-disjoint(LAYER_EXPR)`, and `best-disjoint(LAYER_EXPR, WEIGHT)`, each working bare and `nav:`-qualified.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: major
Description:
States that evaluation returns an empty annotation set, without evaluating `WEIGHT`, when the context element cannot be downcast to a section or the layer is absent.
````

## Criterion 11

````text
ID: criteria_10
Category: Goal fidelity
Weight: minor
Description:
States that `WEIGHT` is evaluated exactly once per annotation with that annotation as context element, coerced to double whatever its type, and that the selection is returned in canonical order.
````

## Criterion 12

````text
ID: criteria_11
Category: Goal fidelity
Weight: minor
Description:
States that an omitted `WEIGHT` means an equal positive weight per annotation, so the largest non-overlapping set wins.
````

## Criterion 13

````text
ID: criteria_12
Category: Goal fidelity
Weight: minor
Description:
States that `LAYER_EXPR` is evaluated as a string against the context element on every evaluation.
````

## Criterion 14

````text
ID: criteria_13
Category: Goal fidelity
Weight: minor
Description:
States that `toString()` serializes the operator without the `nav:` prefix and round-trips through parsing.
````

## Criterion 15

````text
ID: criteria_14
Category: Artifact preservation
Weight: minor
Description:
States that `alvisnlp-core/src/main/java/fr/inra/maiage/bibliome/alvisnlp/core/corpus/Layer.java` adds `public Layer selectMaxWeight(ToDoubleFunction<Annotation> weightFunction)` and that an empty layer returns `new Layer(section)`.
````

## Criterion 16

````text
ID: criteria_15
Category: Artifact preservation
Weight: minor
Description:
States that `Layer.java` carries a private `selectMaxWeight(double[] weights)` dynamic program over the non-zero-length annotations sorted by end, with a predecessor binary search on `end <= start`.
````

## Criterion 17

````text
ID: criteria_16
Category: Artifact preservation
Weight: minor
Description:
Lists the private helpers and types `countEndingAtMost`, `best`, `compareIndices`, `dropIndices`, `compareEqualLengthIndices`, `WeightedInterval`, `SelectionIndices`, and `SelectionState` added to `Layer.java`.
````

## Criterion 18

````text
ID: criteria_17
Category: Artifact preservation
Weight: minor
Description:
States that `alvisnlp-bibliome/src/main/java/fr/inra/maiage/bibliome/alvisnlp/bibliomefactory/library/standard/NavigationLibrary.java` carries four `bestDisjoint` overloads placed after `overlapping`.
````

## Criterion 19

````text
ID: criteria_18
Category: Artifact preservation
Weight: minor
Description:
States that the `bestDisjoint` overloads `(String layerName)` and `(String layerName, Evaluator weight)` are annotated `@Function(firstFtor="best-disjoint", ftors=1, nameTypes={NameType.LAYER})`.
````

## Criterion 20

````text
ID: criteria_19
Category: Artifact preservation
Weight: minor
Description:
States that the `bestDisjoint` overloads `(Evaluator layerName)` and `(Evaluator layerName, Evaluator weight)` carry `@Function`.
````

## Criterion 21

````text
ID: criteria_20
Category: Artifact preservation
Weight: minor
Description:
States that each `bestDisjoint` overload returns `new BestDisjointEvaluator(...)` with a null or given weight evaluator.
````

## Criterion 22

````text
ID: criteria_21
Category: Artifact preservation
Weight: minor
Description:
States that `alvisnlp-bibliome/src/main/java/fr/inra/maiage/bibliome/alvisnlp/bibliomefactory/library/standard/BestDisjointEvaluator.java` is a new file extending `AbstractListEvaluator`.
````

## Criterion 23

````text
ID: criteria_22
Category: Artifact preservation
Weight: minor
Description:
States that `evaluateList` returns `Collections.emptyList()` when `DownCastElement.toSection(elt)` is null or `section.hasLayer(name)` is false, leaving the weight untouched.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
States that the weight function passed to `layer.selectMaxWeight` returns `DEFAULT_WEIGHT = 1.0` when the weight is null and `weight.evaluateDouble(ctx, annotation)` otherwise.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
States that `getTypes()` returns `EvaluationType.ANNOTATIONS`.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
States that `collectUsedNames` adds `NameType.LAYER` for a literal layer name and recurses into `layerNameEvaluator` and `weight`.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
Specifies the four `function-doc` entries in `alvisnlp-bibliome/src/main/resources/fr/inra/maiage/bibliome/alvisnlp/bibliomefactory/library/standard/NavigationLibraryDoc.xml` as carrying nothing but `first-ftor="best-disjoint"` and the synopses `nav:best-disjoint:layerName()`, `nav:best-disjoint(layerName)`, `nav:best-disjoint:layerName(weight)`, and `nav:best-disjoint(layerName, weight)`.
````

## Criterion 28

````text
ID: criteria_27
Category: Decision rationale
Weight: minor
Description:
Records the decision to run `apply_patch` as the single dedicated command because running it inside a compound shell command failed with `apply_patch: command not found`.
````

## Criterion 29

````text
ID: criteria_28
Category: Decision rationale
Weight: major
Description:
Explains that the corrected `LegacyFunctors.java` patch must add `case "best-disjoint":` only once because the failed patch's two hunks, one in the `arity == 0` fall-through group with `layer` and one for the `n == 0 && (arity == 1 || arity == 2)` handling, would have placed duplicate labels in the same `switch`.
````

## Criterion 30

````text
ID: criteria_29
Category: Decision rationale
Weight: major
Description:
Explains that `alvisnlp-core/src/main/java/fr/inra/maiage/bibliome/alvisnlp/core/corpus/expressions/Expression.java` needs the `best-disjoint` case in the `libEllipsisToString` group of `navToString` because serialization otherwise falls through to `defaultToString` and prints the `nav:` prefix.
````

## Criterion 31

````text
ID: criteria_30
Category: Decision rationale
Weight: minor
Description:
Explains that the `NavigationLibraryDoc.xml` entries are needed because the annotation processor warns for undocumented functions.
````

## Criterion 32

````text
ID: criteria_31
Category: Decision rationale
Weight: minor
Description:
States that zero-length annotations are handled in a post-pass over the canonical order because the dynamic program runs over the non-zero-length annotations.
````

## Criterion 33

````text
ID: criteria_32
Category: Temporal coherence
Weight: major
Description:
Records that the patch adding `case "best-disjoint":` to `getFunctors` in `alvisnlp-bibliome/src/main/java/fr/inra/maiage/bibliome/alvisnlp/bibliomefactory/converters/expression/parser/LegacyFunctors.java` failed with `Failed to find expected lines` and left the file unchanged.
````

## Criterion 34

````text
ID: criteria_33
Category: Temporal coherence
Weight: major
Description:
States that the `nav:`-qualified forms resolve without the `LegacyFunctors.java` change while the bare forms do not map to `NavigationLibrary.NAME` and do not parse.
````

## Criterion 35

````text
ID: criteria_34
Category: Temporal coherence
Weight: major
Description:
Records that nothing has been compiled or run.
````

## Criterion 36

````text
ID: criteria_35
Category: Temporal coherence
Weight: major
Description:
Lists the outstanding work as the `LegacyFunctors.java` patch, the `Expression.java` case, the `NavigationLibraryDoc.xml` entries, and the verification, in that order.
````

## Criterion 37

````text
ID: criteria_36
Category: Temporal coherence
Weight: minor
Description:
States the planned verification with `git diff --stat`, `git status --short`, and `rg -n 'selectMaxWeight|bestDisjoint|best-disjoint'` over `Layer.java`, `NavigationLibrary.java`, `BestDisjointEvaluator.java`, `LegacyFunctors.java`, and `Expression.java`, followed by compiling the `alvisnlp-core` and `alvisnlp-bibliome` modules.
````

## Criterion 38

````text
ID: criteria_37
Category: Compression efficiency
Weight: minor
Description:
Contains at most 7200 characters.
````

## Criterion 39

````text
ID: criteria_38
Category: Structural clarity
Weight: minor
Description:
Organizes the summary so that the outstanding work can be found without reading the whole summary.
````

## Criterion 40

````text
ID: criteria_39
Category: Temporal coherence
Weight: negative
Description:
States that bare `best-disjoint` forms parse through `getFunctors` in `LegacyFunctors.java`.
````

## Criterion 41

````text
ID: criteria_40
Category: Goal fidelity
Weight: negative
Description:
States that two annotations overlap when one starts before the other ends.
````

## Criterion 42

````text
ID: criteria_41
Category: Artifact preservation
Weight: negative
Description:
States that `selectMaxWeight` returns `null` when the layer is empty.
````
