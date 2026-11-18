**Handoff Summary**
- Implement Coulomb capstan friction for `CableSpan`, distributing tension from origin to termination by signed wrap and sliding direction.
- Work in `/app`, changing only `Simbody/include/simbody/internal/CableSpan.h` and `Simbody/src/CableSpan.cpp`.
- Do not add source files.
- Do not change build configuration.
- Friction changes must preserve the cable path.
- Friction changes must preserve contact status.
- Friction changes must preserve curve arc lengths.
- Each obstacle defaults to zero friction.
- `setObstacleFrictionCoefficient(CableSpanObstacleIndex ix, Real value)` throws on a negative value without changing the prior value.
- `getObstacleFrictionCoefficient(CableSpanObstacleIndex ix) const` returns the obstacle's coefficient.
- `calcCurveSegmentWrapAngle(const State& state, CableSpanObstacleIndex ix) const` requires `Stage::Position`.
- `calcCurveSegmentWrapAngle` returns the integral of signed surface normal curvature along the path tangent.
- Convex sphere or cylinder contact has a positive wrap angle.
- Concave contact such as the inner rim of a torus has a negative wrap angle.
- An obstacle without contact yields `NaN` for its wrap angle.
- Positive cable length rate multiplies contacted obstacle entry tension by `exp(mu * theta)`.
- Negative cable length rate multiplies contacted obstacle entry tension by `exp(-mu * theta)`.
- Zero length rate leaves tension unchanged.
- Only the length rate's sign controls the capstan multiplier, even for arbitrarily small nonzero rates.
- The wrap angle keeps its sign, so a negative wrap reverses the tension change direction.
- Obstacles without contact do not change tension.
- Via points are frictionless.
- Via points carry continuous local tension.
- Non-positive origin tension yields zero tension along the path.
- `calcTensionAtTermination(const State& state, Real originTension) const` returns propagated termination tension.
- `calcFrictionPowerDissipation(const State& state, Real originTension) const` returns mechanical power dissipated by friction.
- `calcTensionAtTermination` requires `Stage::Velocity`.
- `calcTensionAtTermination` returns zero for non-positive `originTension`.
- `calcFrictionPowerDissipation` requires `Stage::Velocity`.
- `calcFrictionPowerDissipation` returns zero for non-positive `originTension`.
- With no negative wrap, `calcFrictionPowerDissipation` equals cable length rate times termination tension minus origin tension.
- With no negative wrap, `calcFrictionPowerDissipation` is nonnegative.
- `applyBodyForcesWithFriction(const State& state, Real originTension, Vector_<SpatialVec>& bodyForcesInG) const` requires `Stage::Velocity`.
- `applyBodyForcesWithFriction` accumulates local-tension wrenches into `bodyForcesInG`.
- Obstacle Ground force must be `T_exit * t_exit - T_entry * t_entry`.
- Obstacle moment about the body origin must be `r_exit % (T_exit * t_exit) - r_entry % (T_entry * t_entry)`.
- Origin body tensile force is scaled by `originTension`.
- Termination body tensile force is scaled by termination tension.
- Each via-point force is scaled by its local continuous tension.
- At zero friction, every body's wrench must differ from `applyBodyForces` by a norm less than `1e-12`.
- Non-positive `originTension` applies no body forces.

**Current Progress**
- Header declarations for all six public methods were added in `Simbody/include/simbody/internal/CableSpan.h`.
- Public wrapper definitions for all six methods were added in `Simbody/src/CableSpan.cpp`.
- `CurveSegmentData::Instance` stores `wrapAngle`, initialized to `NaN`.
- `liftCurveFromSurface` resets `wrapAngle` to `NaN`.
- `CurveSegment::calcWrapAngle` returns `NaN` when not in contact.
- `CurveSegment::calcWrapAngle` returns stored `wrapAngle` when in contact.
- `CurveSegment` has `m_frictionCoefficient = 0.`.
- `setFrictionCoefficient` validates the coefficient with `SimTK_ERRCHK1_ALWAYS` before assignment.
- `setFrictionCoefficient` does not invoke topology invalidation.
- `setFrictionCoefficient` does not invoke geometry-cache invalidation.
- `shootNewGeodesic` integrates wrap angle trapezoidally over successive knot arc lengths.
- `integrateWrapAngle` queries curvature via `calcSurfaceCurvature` with `calcFrenetFrameFromGeodesicState` and `TangentAxis`.
- The analytic boundary-knot callback in `shootNewGeodesic` feeds `integrateWrapAngle`.
- The implicit geodesic-knot callback in `shootNewGeodesic` feeds `integrateWrapAngle`.
- `shootNewGeodesic` assigns the integral to `dataInst.wrapAngle`.
- `CableSpan::Impl::TensionProfile` stores `terminationTension`, `frictionPowerDissipation`, `obstacleEntryTension`, `obstacleExitTension`, and `viaPointTension`.
- `calcTensionProfile` reads `getDataVel(state).lengthDot`.
- `calcTensionProfile` computes `lengthRateSign` by strict positive and negative comparisons.
- The implemented multiplier is `std::exp(lengthRateSign * frictionCoefficient * wrapAngle)`.
- `calcTensionProfile` retains entry tension as exit tension for an obstacle without contact.
- `calcTensionAtTermination` calls `realizeVelocity` before its non-positive `originTension` early return.
- `calcFrictionPowerDissipation` calls `realizeVelocity` before its non-positive `originTension` early return.
- `applyBodyForcesWithFriction` calls `realizeVelocity` before returning on non-positive `originTension`.
- `applyBodyForcesWithFriction` forms obstacle moment arms by subtracting the body origin from `X_GP` and `X_GQ`.
- It applies obstacle forces via `applyBodyForce`.
- `calcUnitForceAtCableOrigin` supplies origin unit force, scaled by `originTension`.
- `calcUnitForceExertedByViaPoint` supplies via-point unit force, scaled by `profile.viaPointTension`.
- `calcUnitForceAtCableTermination` supplies termination unit force, scaled by `profile.terminationTension`.
- Compilation of the modified code failed.
- The new implementation has not been verified by tests.

**Key Decisions**
- Friction is stored on obstacle configuration outside the geometry solve so changing friction does not alter the path.
- `wrapAngle` is cached with the geodesic instance because analytic shooting does not retain the full knot sequence.
- The agent chose `calcSurfaceCurvature` for geodesic wrap integration.
- `calcSurfaceCurvature` negates `calcSurfaceCurvatureInDirection`.
- The agent's expectation that `calcSurfaceCurvature` yields a convex-positive wrap sign is untested.
- Analytic shooting uses the two boundary knots because the agent judged sphere and cylinder geodesics to have constant normal curvature.
- Implicit shooting integrates over its adaptive knot sequence.
- A shared `TensionProfile` avoids duplicating propagation logic between `applyBodyForcesWithFriction` and the scalar queries.
- `calcTensionProfile` visits each `CableSegment`'s `getObstacleIndexes()` before its final via point to preserve path ordering.
- `calcTensionProfile` accumulates per-contact friction power as `std::abs(lengthDot * (exitTension - entryTension))`.
- The agent chose per-contact absolute power to avoid cancellation across mixed-sign wraps.
- The agent reasoned that this sum reduces to the endpoint-difference formula when all wraps are nonnegative.
- No numerical validation of the friction-power calculation has run.

**Compile Blocker**
- The build directory is `out/build`, using Ninja.
- The corrected build command is `cmake --build out/build --target SimTKsimbody TestCableSpan TestCableSpan_Forces TestCableSpan_LengthDot -j2`.
- The earlier CMake target name `Simbody` was rejected as unknown.
- Use the `SimTKsimbody` CMake target instead.
- Compilation fails in `integrateWrapAngle` in `shootNewGeodesic` in `Simbody/src/CableSpan.cpp` because `geometry` is used before declaration.
- `const ContactGeometry& geometry = getContactGeometry();` still appears below `integrateWrapAngle`.
- The agent attempted to move that declaration above `integrateWrapAngle` and remove the duplicate below.
- That declaration-move edit did not execute.
- The subsequent build repeated the undeclared-`geometry` failure.

**Tooling Issue**
- Earlier `apply_patch` calls updated the header and source files.
- The attempted declaration move failed with `apply_patch: command not found`.
- The coding instructions require editing via `apply_patch`.
- `command -v apply_patch` found no binary.
- The filesystem search for `apply_patch` found no binary.
- `type -a apply_patch` reported it missing.
- The Codex vendor `codex-path` directory contained only `rg`.
- The agent was investigating how to recover `apply_patch` when execution stopped.

**Remaining Work**
1. Recover a usable `apply_patch` invocation.
2. In `Simbody/src/CableSpan.cpp`, move `const ContactGeometry& geometry = getContactGeometry();` above `integrateWrapAngle` in `shootNewGeodesic`, leaving one declaration.
3. Rebuild with the corrected CMake build command above.
4. Run `out/build/TestCableSpan` after rebuilding.
5. Run `out/build/TestCableSpan_Forces` after rebuilding.
6. Run `out/build/TestCableSpan_LengthDot` after rebuilding.
7. The agent planned to run these existing test binaries rather than adding test source files.
8. Check zero-friction wrench equivalence between `applyBodyForcesWithFriction` and `applyBodyForces` within a `1e-12` per-body norm.
9. The agent anticipated possible floating-point differences from scaling obstacle entry and exit forces separately.
10. Zero-friction wrench equivalence has not yet been measured.
11. Review the implemented per-contact friction-power calculation against the requested signed-wrap behavior.
12. The agent left the signed-wrap friction-power interpretation open for further examination.
