# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the goal of extending CableSpan with Coulomb capstan friction over wrapped obstacle surfaces so that tension is distributed by contact wrap and sliding direction according to the Euler-Eytelwein relation.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that changing friction parameters must not change the cable path, contact status, or curve arc lengths.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: minor
Description:
States that the change belongs only in `Simbody/include/simbody/internal/CableSpan.h` and `Simbody/src/CableSpan.cpp`.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: minor
Description:
States that no source files may be added and the build configuration may not be touched.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States the success criterion that with zero friction `applyBodyForces` and `applyBodyForcesWithFriction` must produce a per-body spatial-vector difference norm `< 1e-12`.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
States that a sphere wrap angle and the Euler-Eytelwein tension relation must be validated manually without adding tests or source files.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: negative
Description:
States that the task requires adding a new source file for the friction feature.
````

## Criterion 8

````text
ID: criteria_7
Category: Artifact preservation
Weight: minor
Description:
States that no applicable `AGENTS.md` was found.
````

## Criterion 9

````text
ID: criteria_8
Category: Artifact preservation
Weight: minor
Description:
Lists the added public API methods `setObstacleFrictionCoefficient`, `getObstacleFrictionCoefficient`, `calcCurveSegmentWrapAngle`, `calcTensionAtTermination`, `calcFrictionPowerDissipation`, and `applyBodyForcesWithFriction`.
````

## Criterion 10

````text
ID: criteria_9
Category: Artifact preservation
Weight: minor
Description:
States that `CurveSegmentData::Instance::wrapAngle` is initialized to `NaN` and set to `NaN` when lifted from a surface.
````

## Criterion 11

````text
ID: criteria_10
Category: Artifact preservation
Weight: minor
Description:
States that `CurveSegment::m_frictionCoefficient` defaults to zero and is validated to be nonnegative.
````

## Criterion 12

````text
ID: criteria_11
Category: Artifact preservation
Weight: minor
Description:
States that `CurveSegment::calcWrapAngle` returns `NaN` when not in contact.
````

## Criterion 13

````text
ID: criteria_12
Category: Artifact preservation
Weight: minor
Description:
States that `shootNewGeodesic` integrates the signed surface normal curvature along the geodesic knot points using trapezoidal integration.
````

## Criterion 14

````text
ID: criteria_13
Category: Artifact preservation
Weight: minor
Description:
States that `CableSpan::Impl::TensionProfile` holds obstacle entry and exit tensions and via-point local tensions.
````

## Criterion 15

````text
ID: criteria_14
Category: Artifact preservation
Weight: minor
Description:
States that tension propagation uses `exp(lengthRateSign * mu * theta)` with the sign following the cable length rate.
````

## Criterion 16

````text
ID: criteria_15
Category: Artifact preservation
Weight: minor
Description:
States that the public wrapper definitions were added in `CableSpan.cpp`.
````

## Criterion 17

````text
ID: criteria_16
Category: Artifact preservation
Weight: minor
Description:
Names the build command `cmake --build out/build --target SimTKsimbody TestCableSpan TestCableSpan_Forces TestCableSpan_LengthDot -j2`.
````

## Criterion 18

````text
ID: criteria_17
Category: Artifact preservation
Weight: negative
Description:
States that the `geometry` scope error is located in `Simbody/include/simbody/internal/CableSpan.h`.
````

## Criterion 19

````text
ID: criteria_18
Category: Decision rationale
Weight: minor
Description:
Explains that the wrap-angle sign uses `calcSurfaceCurvature` because it flips Simbody's raw curvature sign so convex wrapping is positive.
````

## Criterion 20

````text
ID: criteria_19
Category: Decision rationale
Weight: minor
Description:
Explains that analytic surfaces use the two analytic boundary knots because sphere and cylinder normal curvature is constant along their geodesics, which makes the integration exact for them.
````

## Criterion 21

````text
ID: criteria_20
Category: Decision rationale
Weight: minor
Description:
States that friction power is accumulated per contact as `std::abs(lengthDot * (exitTension - entryTension))` and stays nonnegative for mixed-sign wrap angles.
````

## Criterion 22

````text
ID: criteria_21
Category: Decision rationale
Weight: minor
Description:
Explains that via points are frictionless so each carries one continuous local tension.
````

## Criterion 23

````text
ID: criteria_22
Category: Decision rationale
Weight: minor
Description:
Explains that `applyBodyForcesWithFriction` follows path order by iterating `CableSegment`s, their obstacles, then each segment's final via point.
````

## Criterion 24

````text
ID: criteria_23
Category: Decision rationale
Weight: minor
Description:
Explains that friction setters do not invalidate topology or cache so they cannot alter the path, contact status, or arc lengths.
````

## Criterion 25

````text
ID: criteria_24
Category: Decision rationale
Weight: minor
Description:
States that obstacles out of contact contribute no force and no tension change.
````

## Criterion 26

````text
ID: criteria_25
Category: Decision rationale
Weight: negative
Description:
States that the two-knot wrap-angle integration is exact for every obstacle surface type.
````

## Criterion 27

````text
ID: criteria_26
Category: Temporal coherence
Weight: major
Description:
Identifies the current build failure as the `integrateWrapAngle` lambda referencing `geometry` before the `const ContactGeometry& geometry = getContactGeometry();` declaration in `Simbody/src/CableSpan.cpp`.
````

## Criterion 28

````text
ID: criteria_27
Category: Temporal coherence
Weight: major
Description:
States the next step of moving the `geometry` declaration above the `integrateWrapAngle` lambda in `shootNewGeodesic` and removing the later duplicate declaration.
````

## Criterion 29

````text
ID: criteria_28
Category: Temporal coherence
Weight: major
Description:
Records that `apply_patch` now fails with `command not found` and that `command -v apply_patch` finds nothing.
````

## Criterion 30

````text
ID: criteria_29
Category: Temporal coherence
Weight: major
Description:
States that `apply_patch` must be retried before falling back to another editing method and that any fallback must be noted explicitly.
````

## Criterion 31

````text
ID: criteria_30
Category: Temporal coherence
Weight: major
Description:
States that the steps after the compile fix are to rebuild and to run `out/build/TestCableSpan`, `out/build/TestCableSpan_Forces`, and `out/build/TestCableSpan_LengthDot`.
````

## Criterion 32

````text
ID: criteria_31
Category: Temporal coherence
Weight: minor
Description:
States that `LD_LIBRARY_PATH=$PWD/out/build` must be set if dynamic loading of the test executables fails.
````

## Criterion 33

````text
ID: criteria_32
Category: Temporal coherence
Weight: major
Description:
States that reviewing the diff for accidental unrelated changes and confirming that only `Simbody/include/simbody/internal/CableSpan.h` and `Simbody/src/CableSpan.cpp` are modified remains to be done.
````

## Criterion 34

````text
ID: criteria_33
Category: Temporal coherence
Weight: major
Description:
States that verifying that friction changes leave the cable path, contact status, and arc lengths unchanged remains to be done.
````

## Criterion 35

````text
ID: criteria_34
Category: Temporal coherence
Weight: negative
Description:
States that the build of the `SimTKsimbody` and `TestCableSpan` targets currently succeeds.
````

## Criterion 36

````text
ID: criteria_35
Category: Compression efficiency
Weight: minor
Description:
Contains at most 5000 characters.
````

## Criterion 37

````text
ID: criteria_36
Category: Structural clarity
Weight: minor
Description:
Organizes the remaining work into separate items so that each step can be found without reading the whole summary.
````
