## Objective
- Add durable external-event approvals to Seata Saga so suspended workflows resume through signals or timeouts across engine restarts.

## Important Details
- Domain additions belong in `org.apache.seata.saga.statelang.domain`.
- Add `StateType.WAIT` with value `"Wait"`.
- State-type lookup must remain case-insensitive.
- Add `ExecutionStatus.WA` with value `"Waiting"`.
- `WaitState` must be an interface extending `State`.
- `String getEvent()` exposes a required, non-blank Event.
- `Map<String, Object> getOutput()` exposes optional Output mappings.
- `java.time.Duration getTimeout()` exposes the optional Timeout.
- `String getTimeoutNext()` exposes the optional TimeoutNext.
- Reject a definition containing only one of Timeout and TimeoutNext.
- A supplied Timeout duration must be strictly positive.
- A supplied Timeout must use ISO-8601 duration syntax.
- Supplied Timeout durations must support fractional seconds.
- A Wait's possible subsequent destinations must be its configured Next plus its TimeoutNext when present.
- Entering Wait must persist a WAIT state instance in WA.
- Persist the suspended machine with execution status WA.
- Persist the suspended machine with `isRunning=false`.
- Wait entry must return without executing Next.
- Wait entry must leave the machine completion time unset.
- Wait entry must skip completion reporting to the transaction coordinator.
- A fresh engine using the same database must reload a suspended workflow.
- A fresh engine must resume the reloaded workflow.
- Add `StateMachineInstance signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String, Object> payload)` to `StateMachineEngine`.
  - Atomically claim the exact activation identified by `waitStateInstanceId` on a matching event.
  - Persist a winning signal's activation status as SU.
  - Persist the signal payload as the activation's output parameters.
  - Record a null payload as an empty map.
  - Continue synchronously until another suspension or a terminal state.
  - Evaluate each Output expression using the recorded payload as its root.
  - Merge mapped signal outputs into machine context.
  - Preserve completed predecessors' outputs when merging mapped signal outputs.
  - Replaying the same event on a satisfied activation returns the reloaded machine without running its continuation again.
  - A delayed duplicate for an older loop activation must not consume a newer activation of the same Wait state.
  - Null or blank required arguments raise `EngineExecutionException` carrying `ParameterRequired` or `InvalidParameter`.
  - A nonexistent machine ID must report `ObjectNotExists`.
  - An event mismatch must report `OperationDenied`.
  - An activation already lost to timeout or compensation must report `OperationDenied`.
- Add `int fireDueTimeouts(java.time.Instant now)` to `StateMachineEngine`.
  - Claim persisted waits whose configured deadline is less than or equal to `now`.
  - Persist each timeout winner as SK.
  - Resume a timeout winner along TimeoutNext.
  - Return the number of claims won.
  - Leave indefinite waits suspended after a timeout sweep.
  - Leave waits whose deadline is later than `now` suspended after a timeout sweep.
  - After reconstruction, the engine must discover persisted waits with due deadlines.
  - After reconstruction, the engine must resume execution when a timeout claim wins.
  - A null `now` raises `EngineExecutionException` carrying `InvalidParameter`.
- Concurrent duplicate matching signals must yield a single winning claim for the same Wait activation.
- A matching signal and a due timeout racing for the same Wait activation must have a single winner.
- A matching signal and compensation racing for the same Wait activation must have a single winner.
- A due timeout and compensation racing for the same Wait activation must have a single winner.
- A waiting child must suspend its enclosing SubStateMachine state in WA.
- A waiting child must suspend its parent machine in WA.
- Completing or timing out a child must synchronously resume its parents through multiple nesting levels.
- Apply each nesting level's output mappings during resumption.
- Ancestor compensation must cancel active descendant waits, including waits in grandchildren.
- Cancellation of active descendant waits must precede compensation of any completed predecessor.
- Add the matching WAIT constant to the deprecated `io.seata.saga.statelang.domain.StateType` wrapper.
- Add the matching WA constant to the deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper.
- Preserve wrap/unwrap round trips for every value of the deprecated `io.seata.saga.statelang.domain.StateType` wrapper.
- Preserve wrap/unwrap round trips for every value of the deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper.
- `ExecutionStatus.java` defines `RU`, `SU`, `FA`, `UN`, and `SK`.
- `ExecutionStatus.java` exposes `getStatusString()`.
- `SucceedEndStateHandler` implements `StateHandler`.
- `SucceedEndStateHandler` has a no-op `process(ProcessContext context)` body.
- `StateInstruction` implements `Instruction`.
- `StateInstruction` declares visible fields `stateName`, `stateMachineName`, `tenantId`, and `end`.
- `ParameterUtils` declares `ResourceLock INPUT_LOCK` in its opening excerpt.
- `ParameterUtils.createOutputParams` lies past the clipped `ParameterUtils.java` excerpt.
- `StateInstanceImpl` implements `StateInstance`.
- `StateInstanceImpl` declares visible `java.util.Date` fields `gmtStarted`, `gmtUpdated`, and `gmtEnd`.
- `StateMachineInstanceImpl` implements `StateMachineInstance`.
- `StateMachineInstanceImpl` declares visible fields `id`, `machineId`, `tenantId`, `parentId`, and `gmtStarted`.
- `StateMachineEngine.java` shows `start(String stateMachineName, String tenantId, Map<String, Object> startParams)` in its opening excerpt.
- `StateMachineProcessHandler.java` imports `SubStateMachineHandler`.
- `StateMachineProcessHandler.java` imports `SucceedEndStateHandler`.
- The solver planned new Wait support after searching `saga` and `compatible` matched only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- The solver planned `WaitStateImpl` to extend `BaseState`.
- The solver planned `WaitStateImpl` to implement `WaitState`.
- The solver proposed registering `WaitStateHandler` through `StateMachineProcessHandler`.
- The solver had not chosen between a dedicated `WaitStateRouter` and reuse of `TaskStateRouter`.
- The solver decided to derive the deadline from the persisted `gmtStarted` plus the configured `Timeout` to avoid a new column.
- The solver planned a `StateLogStore` query by WA status so a reconstructed engine can discover waiting machine instances.
- The solver proposed filtering `seata_state_machine_instance` by status in `DbAndReportTcStateLogStore`.
- The proposed store query name `queryStateMachineInstanceByStatus(ExecutionStatus)` was provisional.
- The solver had yet to verify the status column in `StateLogStoreSqls.java`.
- The solver planned to parse ISO-8601 `Timeout` values with `java.time.Duration.parse` in `WaitStateParser`.
- The solver planned to update `StateMachineUtils.getAllPossibleSubsequentStates` so graph traversal includes `Next` and the optional `TimeoutNext` for a Wait state.
- The solver reasoned that `SubStateMachineHandler` calls `engine.start` synchronously under `DefaultStateMachineConfig` via `ProcessCtrlEventPublisher`.
- The solver reasoned that `decideStatus` must propagate child WA status to the enclosing `SubStateMachine` state.
- The solver reasoned that `ServiceTaskHandlerInterceptor.postProcess` receives a WA state instance from a suspended child.
- The solver reasoned that `decideExecutionStatus` should propagate the WA status to the parent machine.

## Work State
### Completed
- Located `/workspace/repo`.
- Read `ExecutionStatus.java` in full.
- Read `SucceedEndStateHandler.java` in full.
- Read `StateType.java` up to `LOOP_START`.
- Read the opening excerpt of `StateInstruction.java`.
- Read the opening excerpt of `ParameterUtils.java`.
- Read the opening excerpt of `StateMachineEngine.java`.
- Read the opening excerpt of `StateInstanceImpl.java`.
- Read the opening excerpt of `StateMachineInstanceImpl.java`.
- Read the clipped opening excerpt of `ProcessCtrlStateMachineEngine.java`.
- Read the clipped opening excerpt of `StateMachineProcessHandler.java`.
- Read the clipped opening excerpt of `TaskStateRouter.java`.
- Read the clipped opening excerpt of `EngineUtils.java`.
- Read the clipped opening excerpt of `ServiceTaskHandlerInterceptor.java`.
- Read the clipped opening excerpt of `SubStateMachineHandler.java`.
- Read the clipped opening excerpt of `DbAndReportTcStateLogStore.java`.

### Active
- The exploration todo remains `in_progress`.
- Zero source edits have been made.
- Implementation items remain pending.
- Planned unit tests remain pending execution.
- Planned Maven builds remain pending execution.
- Planned lint checks remain pending execution.
- No execution results were recorded for these checks.

### Blocked
- No blocker is established.

## Next Move
1. Finish reading `StateType.java` past `LOOP_START`.
2. Add StateType.WAIT with value "Wait" while preserving case-insensitive state-type lookup.
3. Add ExecutionStatus.WA with value "Waiting".
4. Add the WaitState interface extending State and implement the planned WaitStateImpl.
5. Read the deprecated `io.seata.saga.statelang.domain.StateType` wrapper implementation.
6. Read the deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper implementation.
7. Mirror WAIT and WA in the deprecated io.seata enum wrappers and preserve wrap/unwrap round trips.
8. Register WaitStateParser for Wait in StateParserFactory.java.
9. Validate a non-blank Event, paired Timeout and TimeoutNext, and a strictly positive ISO-8601 duration with fractional-second support.
10. Update `StateMachineUtils.getAllPossibleSubsequentStates` to handle `Next` and optional `TimeoutNext` for Wait graph traversal.
11. Finish reading `DbAndReportTcStateLogStore.java`.
12. Check whether `seata_state_machine_instance` exposes `status` in `StateLogStoreSqls.java`.
13. Read `DbStateMachineConfig.java`.
14. Finish reading `ProcessCtrlStateMachineEngine.java`.
15. Finish reading `SubStateMachineHandler.java`.
16. Inspect `ParameterUtils.createOutputParams` in `ParameterUtils.java`.
17. Finish reading `StateInstanceImpl.java`.
18. Finish reading `StateMachineInstanceImpl.java`.
19. Read `StateMachineImpl`.
20. Read `CompensationHolder`.
21. Read the `StateMachineEngine` wrappers under `compatible`.
22. Inspect tests under `saga/seata-saga-engine/src/test`.
23. Inspect tests under `saga/seata-saga-spring/src/test`.
24. Implement `WaitStateHandler` execution.
25. Implement Wait state routing.
26. Implement durable Wait suspension.
27. Implement database reload for suspended workflows.
28. Implement `signal` on `StateMachineEngine`.
29. Implement `fireDueTimeouts` on `StateMachineEngine` using `gmtStarted` plus the configured `Timeout` as the deadline.
30. Implement nested `SubStateMachine` WA status propagation.
31. Implement descendant wait cancellation before predecessor compensation.
32. Add unit tests for durable Wait behavior.
33. Run Maven builds.
34. Run lint checks.

## Relevant Files
- Paths are relative to `/workspace/repo`.
- The state language source root is `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/`.
- The state language source root contains `domain/StateType.java`.
- The state language source root contains `domain/ExecutionStatus.java`.
- The state language source root contains `domain/State.java`.
- The state language source root contains `domain/impl/BaseState.java`.
- The state language source root contains `domain/impl/AbstractTaskState.java`.
- The state language source root contains `domain/impl/ScriptTaskStateImpl.java`.
- The state language source root contains `domain/impl/StateInstanceImpl.java`.
- The state language source root contains `domain/impl/StateMachineInstanceImpl.java`.
- The state language source root contains `parser/StateParserFactory.java`.
- The state language source root contains `parser/impl/ScriptTaskStateParser.java`.
- The engine source root is `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/`.
- The engine source root contains `StateMachineEngine.java`.
- The engine source root contains `impl/ProcessCtrlStateMachineEngine.java`.
- The engine source root contains `pcext/StateMachineProcessHandler.java`.
- The engine source root contains `pcext/StateMachineProcessRouter.java`.
- The engine source root contains `pcext/StateInstruction.java`.
- The engine source root contains `pcext/routers/TaskStateRouter.java`.
- The engine source root contains `pcext/handlers/SubStateMachineHandler.java`.
- The engine source root contains `pcext/handlers/SucceedEndStateHandler.java`.
- The engine source root contains `pcext/interceptors/ServiceTaskHandlerInterceptor.java`.
- The engine source root contains `pcext/utils/EngineUtils.java`.
- The engine source root contains `pcext/utils/ParameterUtils.java`.
- The store source root is `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/`.
- The store source root contains `StateLogStore.java`.
- The store source root contains `db/StateLogStoreSqls.java`.
- The Spring source root is `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/`.
- The Spring source root contains `store/db/DbAndReportTcStateLogStore.java`.
- The Spring source root contains `config/DbStateMachineConfig.java`.
- The compatible source root is `compatible/src/main/java/io/seata/saga/statelang/domain/`.
- The compatible source root contains `StateType.java`.
- The compatible source root contains `ExecutionStatus.java`.
