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
- `StateMachineProcessRouter.java` includes `import org.apache.seata.saga.engine.pcext.routers.TaskStateRouter;` in its opening excerpt.
- `StateLogStore.java` declares `recordStateMachineStarted(StateMachineInstance machineInstance, ProcessContext context)` in its opening excerpt.
- `StateLogStore.java` declares `recordStateMachineFinished(StateMachineInstance machineInstance, ProcessContext context)` in its opening excerpt.
- `StateLogStoreSqls.java` defines `STATE_MACHINE_INSTANCE_FIELDS` including the `status` column.
- `StateLogStoreSqls.java` defines `RECORD_STATE_MACHINE_STARTED_SQL` inserting into `${TABLE_PREFIX}state_machine_inst`.
- `DbAndReportTcStateLogStore.java` lines 1021–1043 populate a `StateInstanceImpl` row mapper from `resultSet`.
- The `DbAndReportTcStateLogStore.java` row mapper reads state type via `StateType.getStateType(resultSet.getString("type"))`.
- The `DbAndReportTcStateLogStore.java` row mapper reads state status via `ExecutionStatus.valueOf(resultSet.getString("status"))`.
- `ProcessControllerImpl` calls `businessProcessor.process(context)` inside `process(ProcessContext context)` in its opening excerpt.
- `ProcessControllerImpl` calls `businessProcessor.route(context)` after processing inside `process(ProcessContext context)` in its opening excerpt.
- `CustomizeBusinessProcessor` declares a `processHandlers` map in its opening excerpt.
- The solver planned new Wait support because a Java search matched only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- The solver planned `WaitStateImpl` to extend `BaseState` because `WaitState` is not a task state.
- The solver planned `WaitStateImpl` to implement `WaitState`.
- The solver planned to register `WaitStateParser` for `"Wait"` in `StateParserFactory.java`.
- The solver decided that `WaitStateParser` extends `BaseStateParser` because `WaitState` is not a task state.
- The solver decided to perform parse-time validation in `WaitStateParser` by throwing `ParserException` because parse-time exceptions are directly testable for rejecting invalid Wait definitions.
- The solver planned to parse ISO-8601 `Timeout` values with `java.time.Duration.parse` in `WaitStateParser`.
- The solver planned to update `StateMachineUtils.getAllPossibleSubsequentStates` so graph traversal returns `Next` plus optional `TimeoutNext` for a Wait state.
- The solver verified in `StateLogStoreSqls.java` that `${TABLE_PREFIX}state_machine_inst` exposes a `status` column.
- The solver believed from the `DbAndReportTcStateLogStore.java` row mapper that `${TABLE_PREFIX}state_inst` exposes a `status` column.
- The solver decided to derive the timeout deadline from persisted `gmt_started` plus the configured `Timeout` because the solver believed the existing tables already expose `status` and require no schema change.
- The solver noted that new wait-query SQL must match the state type and status encoding written by `recordStateStarted` in `DbAndReportTcStateLogStore.java`.
- The solver reasoned that `ProcessCtrlEventPublisher` publishes `ProcessContext` events through `DirectEventBus` to `ProcessCtrlEventConsumer` in a synchronous loop until the routed instruction is null.
- The solver reasoned that `StateMachineProcessRouter.route` calls `EngineUtils.endStateMachine(context)` in its finally block when `instruction == null && !stateInstruction.isEnd()`.
- The solver planned for `WaitStateHandler.process` to persist the waiting state and suspended machine before setting `StateInstruction.end` to `true`.
- The solver reasoned that `TaskStateRouter.route` returns null when `stateInstruction.isEnd()` is true, which skips `EngineUtils.endStateMachine(context)`.
- The solver reasoned that `TaskStateRouter.route` also returns null when `DomainConstants.VAR_NAME_IS_LOOP_STATE` is true in context.
- The solver reasoned that `ServiceTaskHandlerInterceptor.preProcess` creates a state instance with status `RU` via `recordStateStarted` before handler execution.
- The solver reasoned that `ServiceTaskHandlerInterceptor.postProcess` returns early when the state instance is null or `!stateMachineInstance.isRunning()`.
- The solver reasoned from `ProcessCtrlStateMachineEngine` that `startInternal` builds a `ProcessContext` via `ProcessContextBuilder`.
- The solver reasoned from `ProcessCtrlStateMachineEngine` that `startInternal` publishes the built context to `processCtrlEventPublisher`.
- The solver reasoned that `compensateInternal` demonstrates reloading a machine instance, rebuilding context, setting an instruction, and publishing resumption with `recordStateMachineRestarted`.
- The solver reasoned that `reloadStateMachineInstance` with `replayContextVariables` replays each state's Output mappings via `ParameterUtils.createOutputParams(resolver, state, output)`.
- The solver reasoned that `replayContextVariables` casts to `ServiceTaskStateImpl`.
- The solver planned to adjust `replayContextVariables` so it handles `WaitState`.
- The solver inferred that `stateMachineConfig.getStateLogStore().clearUp(processContext)` in `startInternal` probably cleans `ThreadLocal` state such as `XID`.
- The solver reasoned that `StateInstruction` method `getState(context)` resolves a temporary state or looks up the state by name from `State.getStateMachine()`.
- The solver reasoned that `EngineUtils.generateParentId` formats `parentId` from the parent machine instance ID, `SEPERATOR_PARENT_ID`, and the parent state instance ID.
- The solver planned to verify the `SEPERATOR_PARENT_ID` constant in `DomainConstants.java`.
- The solver inferred that `StateHandlerInterceptor` implementations are probably attached to `InterceptableStateHandler` subclasses via `@LoadLevel` and `EnhancedServiceLoader`.
- The solver planned to verify the `StateHandlerInterceptor` attachment mechanism in `InterceptableStateHandler`.
- The solver decided to put all Wait entry logic in `WaitStateHandler.process` without interceptors because it was the simplest robust design.
- The solver left open whether `WaitStateHandler` implements `StateHandler` directly or implements `InterceptableStateHandler` with no interceptors.
- The solver planned for `WaitStateHandler` to create the `WAIT` state instance with status `WA` inside `WaitStateHandler.process`.
- The solver planned to register `WaitStateHandler` for `StateType.WAIT` in `StateMachineProcessHandler`.
- The solver decided to reuse `TaskStateRouter` registered for `StateType.WAIT` rather than a dedicated `WaitStateRouter` because reusing `TaskStateRouter` is simpler than adding a dedicated router.
- The solver reasoned that `compensateInternal` only calls `checkStatus` when `compensationStatus` is non-null, so a suspended never-compensated machine can be compensated.
- The solver planned a conditional SQL claim update on `${TABLE_PREFIX}state_inst` requiring `status='WA'` where one updated row indicates a winning claim to serialize concurrent claims with a single winner.
- The solver decided that a losing concurrent duplicate matching signal returns the reloaded machine without rerunning the continuation instead of raising `OperationDenied` because the winning signal already persisted status `SU` as a satisfied-activation replay.
- The solver planned a machine-suspension SQL update on `${TABLE_PREFIX}state_machine_inst` setting `status='WA'` with running status set to false.
- The solver left open whether the machine-suspension SQL update uses `WHERE id = ?` or an optimistic `gmt_updated` check until reading `recordStateFinished` in `DbAndReportTcStateLogStore.java`.
- The solver planned to check for existing `StateLogStore` implementers in tests because adding non-default methods to `StateLogStore` breaks implementers.
- The solver decided to omit the `ProcessContext` parameter from the new wait-claim store methods because wait claims never report to the transaction coordinator.
- The solver decided to add a dedicated machine-resumption SQL update on `${TABLE_PREFIX}state_machine_inst` setting `status='RU'` with running status set to true rather than modifying `updateStateMachineRunningStatusSql`, because changing that shared SQL could affect other behaviors in forward flows.
- The solver planned to confirm whether `recordStateMachineRestarted` sets `status` in addition to `is_running` and `gmt_updated` as a subordinate check alongside the dedicated resume SQL design.
- The solver preferred a state-level query on `${TABLE_PREFIX}state_inst` for waiting states over a machine-status query because it finds waiting activations globally, including in child machines.
- The solver planned for `fireDueTimeouts` to check that the machine instance loaded via `getStateMachineInstance` still has status `WA` before timeout claiming in case a concurrent signal has already resumed the machine.
- The solver relied on the state-row CAS from `WA` to `SK` to protect each activation if a concurrent signal races during the `fireDueTimeouts` sweep.
- The solver planned for `SubStateMachineHandler` to set the parent state instance status to `ExecutionStatus.WA` when a child `engine.start` call returns a `WA` instance.
- The solver decided to add `updateStateExecutionStatus(StateInstance stateInstance, ProcessContext context)` to `StateLogStore` because the solver reasoned that `ServiceTaskHandlerInterceptor.preProcess` initially records the parent `SUB_STATE_MACHINE` state instance as `RU` and `SubStateMachineHandler` needs to persist it as `WA` when a child suspends.
- The solver planned for `SubStateMachineHandler` to persist parent machine suspension in `WA` with `isRunning=false` when a child machine suspends in `WA`.
- The solver planned for `SubStateMachineHandler` to set `StateInstruction.end` to `true` when a child machine suspends in `WA`.
- The solver planned for `SubStateMachineHandler` to return without routing to `Next` when a child machine suspends in `WA`.
- The solver planned to resume a suspended parent machine from its `SUB_STATE_MACHINE` state's `Next` after parsing `parentId`, applying `ParameterUtils.createOutputParams`, and calling `recordStateFinished`.
- The solver planned to recurse parent resumption up multiple nesting levels via `resumeParents` when a resumed parent finishes.
- The solver decided that `resumeParents` continues a resumed parent along `Next` even when a child finishes `FA` so the status decision strategy decides the final parent status at machine end.
- The solver planned to scan each machine's state instances via `queryStateInstanceListByMachineInstanceId` during active descendant wait cancellation.
- The solver decided to CAS-claim each active `WA` `WAIT` state instance to `SK` during cancellation because cancelled waits are skipped rather than failed.
- The solver decided that when a cancellation CAS fails because a signal already claimed the wait as `SU`, compensation proceeds with compensating completed predecessors without aborting because under the single-winner rule an already-satisfied wait cannot be cancelled.
- The solver planned to recurse into child machines of each active `WA` `SUB_STATE_MACHINE` state instance via `queryStateMachineInstanceByParentId(generateParentId(stateInstance))`.
- The solver planned to place the recursive cancellation helper at `WaitStateUtils.cancelActiveDescendantWaits(context, stateMachineInstance)`.
- The solver planned to invoke `WaitStateUtils.cancelActiveDescendantWaits(context, stateMachineInstance)` from `CompensationTriggerStateHandler` before compensation stack processing.
- The solver decided to add `DomainConstants.OPERATION_NAME_SIGNAL` with value `"signal"` for continuation contexts because the solver reasoned that `OPERATION_NAME_FORWARD` triggers retried-state detection in `ServiceTaskHandlerInterceptor.preProcess`.

## Work State
### Completed
- Located `/workspace/repo`.
- A Java search matched only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- Read `ExecutionStatus.java` in full.
- Read `SucceedEndStateHandler.java` in full.
- Read `BaseStateParser.java` in full.
- Read `Rule.java` in full.
- Read `StateType.java` up to `LOOP_START`.
- Read `DbAndReportTcStateLogStore.java` lines 1021–1043.
- Read the clipped opening excerpt of `DbAndReportTcStateLogStore.java` lines 1–34.
- Read the clipped opening excerpt of `StateLogStoreSqls.java`.
- Read the clipped opening excerpt of `StateLogStore.java`.
- Read the clipped opening excerpt of `StateMachineEngine.java`.
- Read the clipped opening excerpt of `ProcessCtrlStateMachineEngine.java`.
- Read the clipped opening excerpt of `StateInstruction.java`.
- Read the clipped opening excerpt of `StateMachineProcessHandler.java`.
- Read the clipped opening excerpt of `StateMachineProcessRouter.java`.
- Read the clipped opening excerpt of `TaskStateRouter.java`.
- Read the clipped opening excerpt of `EngineUtils.java`.
- Read the clipped opening excerpt of `ServiceTaskHandlerInterceptor.java`.
- Read the clipped opening excerpt of `SubStateMachineHandler.java`.
- Read the clipped opening excerpt of `ProcessControllerImpl.java`.
- Read the clipped opening excerpt of `CustomizeBusinessProcessor.java`.
- Read the opening excerpt of `ParameterUtils.java`.
- Read the opening excerpt of `StateInstanceImpl.java`.
- Read the opening excerpt of `StateMachineInstanceImpl.java`.
- Listed the `saga` module directories and source trees via bash `ls`.

### Active
- The exploration todo remains `in_progress`.
- Zero source edits have been made.
- Implementation items remain pending.
- Planned unit tests remain pending execution.
- Planned Maven builds remain pending execution.
- Planned lint checks remain pending execution.
- No execution results were recorded for these checks.

### Blocked
- The `glob` tool fails with `ripgrep execution failed`.
- Directory listing via bash `ls` is in use as a workaround for file discovery.

## Next Move
1. Finish reading the unread implementation of `DbAndReportTcStateLogStore.java` to verify `recordStateStarted` encoding.
2. Finish reading `ProcessControllerImpl.java` past its clipped opening excerpt.
3. Finish reading `CustomizeBusinessProcessor.java` past its clipped opening excerpt.
4. Read `DefaultRouterHandler.java`.
5. Read `ProcessCtrlEventPublisher.java`.
6. Read `ProcessCtrlEventConsumer.java`.
7. Read `DirectEventBus.java`.
8. Read `ProcessContextBuilder`.
9. Read `ProcessContextImpl.java`.
10. Read `DomainConstants.java` in full.
11. Read `ParameterUtils.java` in full to inspect `createOutputParams`.
12. Read `CompensationHolder.java`.
13. Read `CompensationTriggerStateHandler.java`.
14. Read `DefaultStatusDecisionStrategy.java`.
15. Read `AbstractStateMachineConfig.java`.
16. Read `DbStateMachineConfig.java`.
17. Read `EndStateRouter`.
18. Read `EndStateRouterInterceptor.java`.
19. Finish reading `StateType.java` past `LOOP_START`.
20. Read `StateMachineUtils.java`.
21. Read the remaining statelang domain files.
22. Read the remaining statelang parser files.
23. Read the remaining statelang validator files.
24. Read the deprecated `io.seata.saga.statelang.domain.StateType` wrapper implementation.
25. Read the deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper implementation.
26. Read the `StateMachineEngine` wrappers under `compatible`.
27. Inspect tests under `saga/seata-saga-engine/src/test`.
28. Inspect tests under `saga/seata-saga-spring/src/test`.
29. Add `StateType.WAIT` with value `"Wait"` in `StateType.java`.
30. Add `ExecutionStatus.WA` with value `"Waiting"` in `ExecutionStatus.java`.
31. Add the `WaitState` interface extending `State`.
32. Implement `WaitStateImpl`.
33. Add `WAIT` to the deprecated `io.seata.saga.statelang.domain.StateType` wrapper.
34. Preserve wrap/unwrap round trips for every value in the deprecated `StateType` wrapper.
35. Add `WA` to the deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper.
36. Preserve wrap/unwrap round trips for every value in the deprecated `ExecutionStatus` wrapper.
37. Register `WaitStateParser` for `"Wait"` in `StateParserFactory.java`.
38. Implement `WaitStateParser` extending `BaseStateParser` with parse-time validation throwing `ParserException`.
39. Update `StateMachineUtils.getAllPossibleSubsequentStates` for `WaitState`.
40. Add the wait-claim SQL constant to `StateLogStoreSqls.java`.
41. Add the suspend SQL constant to `StateLogStoreSqls.java`.
42. Add the resume SQL constant to `StateLogStoreSqls.java`.
43. Add the wait-query SQL constant to `StateLogStoreSqls.java`.
44. Add the wait-claim method to `StateLogStore.java`.
45. Add the suspend method to `StateLogStore.java`.
46. Add the resume method to `StateLogStore.java`.
47. Add the wait-query method to `StateLogStore.java`.
48. Add `updateStateExecutionStatus` to `StateLogStore.java`.
49. Implement the wait-claim method in `DbAndReportTcStateLogStore.java`.
50. Implement the suspend method in `DbAndReportTcStateLogStore.java`.
51. Implement the resume method in `DbAndReportTcStateLogStore.java`.
52. Implement the wait-query method in `DbAndReportTcStateLogStore.java`.
53. Implement `updateStateExecutionStatus` in `DbAndReportTcStateLogStore.java`.
54. Implement `WaitStateHandler`.
55. Register `WaitStateHandler` for `StateType.WAIT` in `StateMachineProcessHandler.java`.
56. Update `SubStateMachineHandler.java` for parent `WA` suspension.
57. Implement `signal` on `StateMachineEngine`.
58. Implement `fireDueTimeouts` on `StateMachineEngine`.
59. Implement synchronous parent-chain resumption for completed or timed-out waiting child machines.
60. Implement active descendant wait cancellation before predecessor compensation in `CompensationTriggerStateHandler.java`.
61. Add unit tests for durable Wait behavior.
62. Run Maven builds.
63. Run lint checks.

## Relevant Files
- Paths are relative to `/workspace/repo`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` contains `StateType.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` contains `ExecutionStatus.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` contains `State.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` contains `DomainConstants.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` is the target directory for `domain/WaitState.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` contains `BaseState.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` contains `AbstractTaskState.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` contains `ScriptTaskStateImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` contains `StateInstanceImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` contains `StateMachineInstanceImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` contains `StateMachineImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` is the target directory for `domain/impl/WaitStateImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/` contains `StateParserFactory.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/` contains `BaseStateParser.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/` contains `AbstractTaskStateParser.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/` contains `ScriptTaskStateParser.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/` subdirectory `parser/utils` contains `StateMachineUtils.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/` contains `Rule.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/` contains `RuleFactory.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/` contains `StateMachineEngine.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/config/` contains `AbstractStateMachineConfig.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/impl/` contains `ProcessCtrlStateMachineEngine.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/strategy/impl/` contains `DefaultStatusDecisionStrategy.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` contains `StateMachineProcessHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` contains `StateMachineProcessRouter.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` contains `StateInstruction.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` contains `InterceptableStateHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/` contains `SubStateMachineHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/` contains `SucceedEndStateHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/` contains `CompensationTriggerStateHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` contains `routers/TaskStateRouter.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/interceptors/` contains `ServiceTaskHandlerInterceptor.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/interceptors/` contains `EndStateRouterInterceptor.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/` contains `EngineUtils.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/` contains `ParameterUtils.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/` contains `CompensationHolder.java`.
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/` contains `StateLogStore.java`.
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/` contains `db/StateLogStoreSqls.java`.
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/store/db/` contains `DbAndReportTcStateLogStore.java`.
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/` contains `config/DbStateMachineConfig.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/impl` contains `ProcessControllerImpl.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/impl` contains `ProcessContextImpl.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/process/impl` contains `CustomizeBusinessProcessor.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/handler` contains `DefaultRouterHandler.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl` contains `ProcessCtrlEventPublisher.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl` contains `ProcessCtrlEventConsumer.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl` contains `DirectEventBus.java`.
- `compatible/src/main/java/io/seata/saga/statelang/domain/` contains `StateType.java`.
- `compatible/src/main/java/io/seata/saga/statelang/domain/` contains `ExecutionStatus.java`.
