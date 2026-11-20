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
- Persist suspended machine with execution status WA.
- Persist suspended machine with `isRunning=false`.
- Wait entry: return without executing Next.
- Wait entry: leave the machine completion time unset.
- Wait entry: skip completion reporting to the transaction coordinator.
- Fresh engine on same DB must reload a suspended workflow.
- Fresh engine must resume the reloaded workflow.
- Add `StateMachineInstance signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String, Object> payload)` to `StateMachineEngine`.
  - Atomically claim `waitStateInstanceId` on matching event.
  - Persist winning signal activation status as SU.
  - Persist signal payload as activation output params.
  - Record a null payload as an empty map.
  - Continue synchronously until next suspension or terminal state.
  - Evaluate Output expressions with recorded payload as root.
  - Merge mapped signal outputs into machine context.
  - Preserve predecessor outputs when merging signal outputs.
  - Replaying same event on satisfied activation returns reloaded machine without rerunning continuation.
  - Delayed duplicate for older loop activation must not consume newer Wait activation.
  - Null/blank required args raise `EngineExecutionException` (`ParameterRequired`/`InvalidParameter`).
  - Nonexistent machine ID reports `ObjectNotExists`.
  - Event mismatch reports `OperationDenied`.
  - Activation lost to timeout or compensation reports `OperationDenied`.
- Add `int fireDueTimeouts(java.time.Instant now)` to `StateMachineEngine`.
  - Claim persisted waits with deadline <= `now`.
  - Persist timeout winner as SK.
  - Resume timeout winner along TimeoutNext.
  - Return count of claims won.
  - Leave indefinite waits suspended.
  - Leave future-deadline waits suspended.
  - After restart, engine must discover persisted waits with due deadlines.
  - After restart, engine must resume execution when a timeout claim wins.
  - Null `now` raises `EngineExecutionException` (`InvalidParameter`).
- Concurrent duplicate matching signals yield a single winning claim.
- Signal vs due timeout race yields a single winner.
- Signal vs compensation race yields a single winner.
- Timeout vs compensation race yields a single winner.
- Waiting child suspends enclosing SubStateMachine state in WA.
- Waiting child suspends parent machine in WA.
- Child completion or timeout synchronously resumes parent chain.
- Apply output mappings at each resumed nesting level.
- Ancestor compensation cancels active descendant waits including grandchildren.
- Descendant wait cancellation precedes compensating completed predecessors.
- Add WAIT to deprecated `io.seata.saga.statelang.domain.StateType` wrapper.
- Add WA to deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper.
- Preserve wrap/unwrap round trips for deprecated `io.seata.saga.statelang.domain.StateType` wrapper.
- Preserve wrap/unwrap round trips for deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper.
- `ExecutionStatus.java` defines `RU`.
- `ExecutionStatus.java` defines `SU`.
- `ExecutionStatus.java` defines `FA`.
- `ExecutionStatus.java` defines `UN`.
- `ExecutionStatus.java` defines `SK`.
- `ExecutionStatus.java` exposes `getStatusString()`.
- `SucceedEndStateHandler` implements `StateHandler`.
- `SucceedEndStateHandler` has a no-op `process(ProcessContext context)` body.
- `StateInstruction` implements `Instruction`.
- `StateInstruction` has field `stateName`.
- `StateInstruction` has field `stateMachineName`.
- `StateInstruction` has field `tenantId`.
- `StateInstruction` has field `end`.
- `ParameterUtils` declares `ResourceLock INPUT_LOCK`.
- `ParameterUtils.createOutputParams` lies past the clipped `ParameterUtils.java` excerpt.
- `StateInstanceImpl` implements `StateInstance`.
- `StateInstanceImpl` has `java.util.Date` field `gmtStarted`.
- `StateInstanceImpl` has `java.util.Date` field `gmtUpdated`.
- `StateInstanceImpl` has `java.util.Date` field `gmtEnd`.
- `StateMachineInstanceImpl` implements `StateMachineInstance`.
- `StateMachineInstanceImpl` has field `id`.
- `StateMachineInstanceImpl` has field `machineId`.
- `StateMachineInstanceImpl` has field `tenantId`.
- `StateMachineInstanceImpl` has field `parentId`.
- `StateMachineInstanceImpl` has field `gmtStarted`.
- `StateMachineEngine.java` shows `start(String stateMachineName, String tenantId, Map<String, Object> startParams)`.
- `StateMachineProcessHandler.java` imports `SubStateMachineHandler`.
- `StateMachineProcessHandler.java` imports `SucceedEndStateHandler`.
- `StateMachineProcessRouter.java` imports `TaskStateRouter`.
- `StateMachineProcessRouter.java` imports `EndStateRouter`.
- Reasoned: `DbAndReportTcStateLogStore` extends `AbstractStore`.
- `StateLogStore.java` declares `recordStateMachineStarted(StateMachineInstance machineInstance, ProcessContext context)`.
- `StateLogStore.java` declares `recordStateMachineFinished(StateMachineInstance machineInstance, ProcessContext context)`.
- `StateLogStoreSqls.java` defines `STATE_MACHINE_INSTANCE_FIELDS` including the `status` column.
- `StateLogStoreSqls.java` defines `STATE_MACHINE_INSTANCE_FIELDS_WITHOUT_PARAMS`.
- `StateLogStoreSqls.java` defines `RECORD_STATE_MACHINE_STARTED_SQL` inserting into `${TABLE_PREFIX}state_machine_inst`.
- `DbAndReportTcStateLogStore.java` lines 1021–1043 populate a `StateInstanceImpl` row mapper from `resultSet`.
- The `DbAndReportTcStateLogStore.java` row mapper reads state type via `StateType.getStateType(resultSet.getString("type"))`.
- The `DbAndReportTcStateLogStore.java` row mapper reads state status via `ExecutionStatus.valueOf(resultSet.getString("status"))`.
- `ProcessControllerImpl` calls `businessProcessor.process(context)` inside `process(ProcessContext context)`.
- `ProcessControllerImpl` calls `businessProcessor.route(context)` after processing inside `process(ProcessContext context)`.
- `CustomizeBusinessProcessor` declares a `processHandlers` map.
- Planned new Wait support because a Java search matched only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- Planned `WaitStateImpl` to extend `BaseState` because `WaitState` is not a task state.
- Planned `WaitStateImpl` to implement `WaitState`.
- Planned: register `WaitStateParser` for `"Wait"` in `StateParserFactory.java`.
- Decided: `WaitStateParser` extends `BaseStateParser` because `WaitState` is not a task state.
- Decided to perform parse-time validation in `WaitStateParser` by throwing `ParserException` because parse-time exceptions are directly testable for rejecting invalid Wait definitions.
- Planned: parse ISO-8601 `Timeout` values with `java.time.Duration.parse` in `WaitStateParser`.
- Planned: update `StateMachineUtils.getAllPossibleSubsequentStates` so graph traversal returns `Next` plus optional `TimeoutNext` for a Wait state.
- Verified in `StateLogStoreSqls.java` that `${TABLE_PREFIX}state_machine_inst` exposes a `status` column.
- Believed from the `DbAndReportTcStateLogStore.java` row mapper that `${TABLE_PREFIX}state_inst` exposes a `status` column.
- Decided to derive the timeout deadline from persisted `gmt_started` plus the configured `Timeout` because believed the existing tables require no schema change.
- Believed the existing tables already expose the `status` column.
- Noted: new wait-query SQL must match the state type and status encoding written by `recordStateStarted` in `DbAndReportTcStateLogStore.java`.
- Reasoned: `ProcessCtrlEventPublisher` publishes `ProcessContext` events through `DirectEventBus` to `ProcessCtrlEventConsumer` in a synchronous loop until the routed instruction is null.
- Reasoned: `StateMachineProcessRouter.route` calls `EngineUtils.endStateMachine(context)` in its finally block when `instruction == null && !stateInstruction.isEnd()`.
- Planned: `WaitStateHandler.process` to persist the waiting state before setting `StateInstruction.end` to `true`.
- Planned: `WaitStateHandler.process` to persist the suspended machine before setting `StateInstruction.end` to `true`.
- Planned: `WaitStateHandler.process` to set `StateInstruction.end` to `true` after persistence completes.
- Reasoned: `TaskStateRouter.route` returns null when `stateInstruction.isEnd()` is true, which skips `EngineUtils.endStateMachine(context)`.
- Reasoned: `TaskStateRouter.route` also returns null when `DomainConstants.VAR_NAME_IS_LOOP_STATE` is true in context.
- Unverified assumption: `ServiceTaskHandlerInterceptor.preProcess` creates a state instance with status `RU` via `recordStateStarted` before handler execution.
- Reasoned: `ServiceTaskHandlerInterceptor.postProcess` returns early when `!stateMachineInstance.isRunning()`.
- Unverified prior assumption: `ServiceTaskHandlerInterceptor.postProcess` also returns early when the state instance is null.
- Reasoned from `ProcessCtrlStateMachineEngine` that `startInternal` builds a `ProcessContext` via `ProcessContextBuilder`.
- Reasoned from `ProcessCtrlStateMachineEngine` that `startInternal` publishes the built context to `processCtrlEventPublisher`.
- Reasoned: `compensateInternal` reloads a machine instance.
- Reasoned: `compensateInternal` rebuilds context.
- Reasoned: `compensateInternal` sets a state instruction.
- Reasoned: `compensateInternal` publishes resumption with `recordStateMachineRestarted`.
- Reasoned: `reloadStateMachineInstance` with `replayContextVariables` replays each state's Output mappings via `ParameterUtils.createOutputParams(resolver, state, output)`.
- Reasoned: `replayContextVariables` casts to `ServiceTaskStateImpl`.
- Planned: adjust `replayContextVariables` so it handles `WaitState`.
- Inferred: `stateMachineConfig.getStateLogStore().clearUp(processContext)` in `startInternal` probably cleans `ThreadLocal` state such as `XID`.
- Reasoned: `StateInstruction` method `getState(context)` resolves a temporary state or looks up the state by name from `State.getStateMachine()`.
- Reasoned: `EngineUtils.generateParentId` formats `parentId` from the parent machine instance ID, `SEPERATOR_PARENT_ID`, and the parent state instance ID.
- Planned: verify the `SEPERATOR_PARENT_ID` constant in `DomainConstants.java`.
- Inferred: `StateHandlerInterceptor` implementations attach to `InterceptableStateHandler` subclasses via `@LoadLevel`.
- Inferred: `StateHandlerInterceptor` implementations are discovered via `EnhancedServiceLoader`.
- Planned: verify the `StateHandlerInterceptor` attachment mechanism in `InterceptableStateHandler`.
- Decided to put all Wait entry logic in `WaitStateHandler.process` without interceptors because it was the simplest robust design.
- Open: whether `WaitStateHandler` implements `StateHandler` directly or implements `InterceptableStateHandler` with no interceptors.
- Planned: `WaitStateHandler` to create the `WAIT` state instance with status `WA` inside `WaitStateHandler.process`.
- Planned: register `WaitStateHandler` for `StateType.WAIT` in `StateMachineProcessHandler`.
- Decided to reuse `TaskStateRouter` registered for `StateType.WAIT` rather than a dedicated `WaitStateRouter` because reusing `TaskStateRouter` is simpler than adding a dedicated router.
- Reasoned: `compensateInternal` only calls `checkStatus` when `compensationStatus` is non-null, so a suspended never-compensated machine can be compensated.
- Planned a conditional SQL claim update on `${TABLE_PREFIX}state_inst` requiring `status='WA'` where one updated row indicates a winning claim to serialize concurrent claims with a single winner.
- Decided: a losing concurrent duplicate matching signal returns the reloaded machine without rerunning the continuation instead of raising `OperationDenied` because the winning signal already persisted status `SU` as a satisfied-activation replay.
- Planned a machine-suspension SQL update on `${TABLE_PREFIX}state_machine_inst` setting `status='WA'` with running status set to false.
- Open: whether the machine-suspension SQL update uses `WHERE id = ?` or an optimistic `gmt_updated` check until reading `recordStateFinished` in `DbAndReportTcStateLogStore.java`.
- Planned: check for existing `StateLogStore` implementers in tests because adding non-default methods to `StateLogStore` breaks implementers.
- Decided to omit the `ProcessContext` parameter from the new wait-claim store methods because wait claims never report to the transaction coordinator.
- Decided to add a dedicated machine-resumption SQL update on `${TABLE_PREFIX}state_machine_inst` setting `status='RU'` with running status set to true rather than modifying `updateStateMachineRunningStatusSql`, because changing that shared SQL could affect other behaviors in forward flows.
- Planned: confirm whether `recordStateMachineRestarted` updates `status` in addition to running state as a subordinate check alongside the dedicated resume SQL design.
- Preferred a state-level query on `${TABLE_PREFIX}state_inst` for waiting states over a machine-status query because it finds waiting activations globally, including in child machines.
- Planned: `fireDueTimeouts` to check that the machine instance loaded via `getStateMachineInstance` still has status `WA` before timeout claiming in case a concurrent signal has already resumed the machine.
- Relied on the state-row CAS from `WA` to `SK` to protect each activation if a concurrent signal races during the `fireDueTimeouts` sweep.
- Planned: `SubStateMachineHandler` to set the parent state instance status to `ExecutionStatus.WA` when a child `engine.start` call returns a `WA` instance.
- Decided to add `updateStateExecutionStatus(StateInstance stateInstance, ProcessContext context)` to `StateLogStore` because `SubStateMachineHandler` must persist a parent `SUB_STATE_MACHINE` state instance as `WA` when a child suspends.
- Unverified assumption: `ServiceTaskHandlerInterceptor.preProcess` initially records the parent `SUB_STATE_MACHINE` state instance as `RU`.
- Planned: `SubStateMachineHandler` to persist parent machine suspension in `WA` with `isRunning=false` when child suspends in `WA`.
- Planned: `SubStateMachineHandler` to set `StateInstruction.end` to `true` when child suspends in `WA`.
- Planned: `SubStateMachineHandler` to return without routing to `Next` when child suspends in `WA`.
- Parent resumption plan: parse `parentId` into its parent identifiers.
- Parent resumption plan: reload the parent machine.
- Parent resumption plan: find the parent `SUB_STATE_MACHINE` state instance by ID.
- Parent resumption plan: verify that the located parent state instance has status `WA`.
- Parent resumption plan: assign the child machine's final status to the parent `SUB_STATE_MACHINE` state instance.
- Parent resumption plan: apply `ParameterUtils.createOutputParams` for the parent `SUB_STATE_MACHINE` state.
- Parent resumption plan: call `recordStateFinished` for the parent `SUB_STATE_MACHINE` state instance.
- Parent resumption plan: continue the parent machine from its `SUB_STATE_MACHINE` state's `Next` with replayed parent context variables.
- Planned: recurse parent resumption up multiple nesting levels via `resumeParents` when a resumed parent finishes.
- Decided: `resumeParents` continues a resumed parent along `Next` even when a child finishes `FA` so the status decision strategy decides the final parent status at machine end.
- Planned: scan each machine's state instances via `queryStateInstanceListByMachineInstanceId` during active descendant wait cancellation.
- Decided to CAS-claim each active `WA` `WAIT` state instance to `SK` during cancellation because cancelled waits are skipped rather than failed.
- Decided: when a cancellation CAS fails because a signal already claimed the wait as `SU`, compensation proceeds with compensating completed predecessors without aborting because under the single-winner rule an already-satisfied wait cannot be cancelled.
- Planned: recurse into child machines of each active `WA` `SUB_STATE_MACHINE` state instance via `queryStateMachineInstanceByParentId(generateParentId(stateInstance))`.
- Planned: place the recursive cancellation helper at `WaitStateUtils.cancelActiveDescendantWaits(context, stateMachineInstance)`.
- Planned: invoke `WaitStateUtils.cancelActiveDescendantWaits(context, stateMachineInstance)` from `CompensationTriggerStateHandler` before compensation stack processing.
- Decided to add `DomainConstants.OPERATION_NAME_SIGNAL` with value `"signal"` for continuation contexts because of unverified assumption that `OPERATION_NAME_FORWARD` triggers retried-state detection in `ServiceTaskHandlerInterceptor.preProcess`.

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
- Read clipped excerpt of `DbAndReportTcStateLogStore.java` lines 1–34.
- Read clipped excerpt of `StateLogStoreSqls.java`.
- Read clipped excerpt of `StateLogStore.java`.
- Read clipped excerpt of `StateMachineEngine.java`.
- Read clipped excerpt of `ProcessCtrlStateMachineEngine.java`.
- Read clipped excerpt of `StateInstruction.java`.
- Read clipped excerpt of `StateMachineProcessHandler.java`.
- Read clipped excerpt of `StateMachineProcessRouter.java`.
- Read clipped excerpt of `TaskStateRouter.java`.
- Read clipped excerpt of `EngineUtils.java`.
- Read clipped excerpt of `ServiceTaskHandlerInterceptor.java`.
- Read clipped excerpt of `SubStateMachineHandler.java`.
- Read clipped excerpt of `ProcessControllerImpl.java`.
- Read clipped excerpt of `CustomizeBusinessProcessor.java`.
- Read clipped excerpt of `ParameterUtils.java`.
- Read clipped excerpt of `StateInstanceImpl.java`.
- Read clipped excerpt of `StateMachineInstanceImpl.java`.
- Listed the `saga` module directories and source trees via bash `ls`.
- Read clipped opening excerpt of `DomainConstants.java` (truncated tool output).
- Reasoning noted full read of `DbAndReportTcStateLogStore.java` in full (tool output truncated).
- Reasoning noted full read of `ProcessCtrlStateMachineEngine.java` in full (tool output truncated).

### Active
- The exploration todo remains `in_progress`.
- Zero source edits have been made.
- Implementation items remain pending.
- Unit tests remain pending.
- Maven builds remain pending.
- Lint checks remain pending.
- No check results recorded.

### Blocked
- The `glob` tool fails with `ripgrep execution failed`.
- Using bash `ls` for file discovery.

## Next Move
1. Read `ServiceTaskHandlerInterceptor.java` in full.
2. Read `StateMachineProcessHandler.java` in full.
3. Read `StateInstruction.java` in full.
4. Verify `recordStateStarted` encoding in `DbAndReportTcStateLogStore.java`.
5. Finish reading `ProcessControllerImpl.java` past clipped excerpt.
6. Finish reading `CustomizeBusinessProcessor.java` past clipped excerpt.
7. Read `DefaultRouterHandler.java`.
8. Read `ProcessCtrlEventPublisher.java`.
9. Read `ProcessCtrlEventConsumer.java`.
10. Read `DirectEventBus.java`.
11. Read `ProcessContextBuilder`.
12. Read `ProcessContextImpl.java`.
13. Verify `SEPERATOR_PARENT_ID` in `DomainConstants.java` past clipped excerpt.
14. Verify `createOutputParams` in `ParameterUtils.java` past clipped excerpt.
15. Read `CompensationHolder.java`.
16. Read `CompensationTriggerStateHandler.java`.
17. Read `DefaultStatusDecisionStrategy.java`.
18. Read `AbstractStateMachineConfig.java`.
19. Read `DbStateMachineConfig.java`.
20. Read `EndStateRouter`.
21. Read `EndStateRouterInterceptor.java`.
22. Finish reading `StateType.java` past `LOOP_START`.
23. Read `StateMachineUtils.java`.
24. Read remaining statelang domain files.
25. Read remaining statelang parser files.
26. Read remaining statelang validator files.
27. Read deprecated `io.seata.saga.statelang.domain.StateType` wrapper implementation.
28. Read deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper implementation.
29. Read the `StateMachineEngine` wrappers under `compatible`.
30. Inspect tests under `saga/seata-saga-engine/src/test`.
31. Inspect tests under `saga/seata-saga-spring/src/test`.
32. Add `StateType.WAIT` with value `"Wait"` in `StateType.java`.
33. Add `ExecutionStatus.WA` with value `"Waiting"` in `ExecutionStatus.java`.
34. Add the `WaitState` interface extending `State`.
35. Implement `WaitStateImpl`.
36. Add `WAIT` to the deprecated `io.seata.saga.statelang.domain.StateType` wrapper.
37. Preserve wrap/unwrap round trips for deprecated `StateType` wrapper.
38. Add `WA` to the deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper.
39. Preserve wrap/unwrap round trips for deprecated `ExecutionStatus` wrapper.
40. Register `WaitStateParser` for `"Wait"` in `StateParserFactory.java`.
41. Implement `WaitStateParser` extending `BaseStateParser` with parse-time validation throwing `ParserException`.
42. Update `StateMachineUtils.getAllPossibleSubsequentStates` for `WaitState`.
43. Add wait-claim SQL to `StateLogStoreSqls.java`.
44. Add suspend SQL to `StateLogStoreSqls.java`.
45. Add resume SQL to `StateLogStoreSqls.java`.
46. Add wait-query SQL to `StateLogStoreSqls.java`.
47. Add wait-claim method to `StateLogStore.java`.
48. Add suspend method to `StateLogStore.java`.
49. Add resume method to `StateLogStore.java`.
50. Add wait-query method to `StateLogStore.java`.
51. Add `updateStateExecutionStatus` to `StateLogStore.java`.
52. Implement wait-claim in `DbAndReportTcStateLogStore.java`.
53. Implement suspend in `DbAndReportTcStateLogStore.java`.
54. Implement resume in `DbAndReportTcStateLogStore.java`.
55. Implement wait-query in `DbAndReportTcStateLogStore.java`.
56. Implement `updateStateExecutionStatus` in `DbAndReportTcStateLogStore.java`.
57. Implement `WaitStateHandler`.
58. Register `WaitStateHandler` for `StateType.WAIT` in `StateMachineProcessHandler.java`.
59. Update `SubStateMachineHandler.java` for parent `WA` suspension.
60. Implement `signal` on `StateMachineEngine`.
61. Implement `fireDueTimeouts` on `StateMachineEngine`.
62. Implement synchronous parent-chain resumption for completed or timed-out waiting child machines.
63. Implement active descendant wait cancellation before predecessor compensation in `CompensationTriggerStateHandler.java`.
64. Add unit tests for durable Wait behavior.
65. Run Maven builds.
66. Run lint checks.

## Relevant Files
- Paths are relative to `/workspace/repo`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/StateType.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/ExecutionStatus.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/State.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/DomainConstants.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` target for `domain/WaitState.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/BaseState.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/AbstractTaskState.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/ScriptTaskStateImpl.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/StateInstanceImpl.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/StateMachineInstanceImpl.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/StateMachineImpl.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` target for `domain/impl/WaitStateImpl.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/StateParserFactory.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/BaseStateParser.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/AbstractTaskStateParser.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/ScriptTaskStateParser.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/utils/StateMachineUtils.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/Rule.java`
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/RuleFactory.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/StateMachineEngine.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/config/AbstractStateMachineConfig.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/impl/ProcessCtrlStateMachineEngine.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/strategy/impl/DefaultStatusDecisionStrategy.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/StateMachineProcessHandler.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/StateMachineProcessRouter.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/StateInstruction.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/InterceptableStateHandler.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/SubStateMachineHandler.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/SucceedEndStateHandler.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/CompensationTriggerStateHandler.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/routers/TaskStateRouter.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/interceptors/ServiceTaskHandlerInterceptor.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/interceptors/EndStateRouterInterceptor.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/EngineUtils.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/ParameterUtils.java`
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/CompensationHolder.java`
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/StateLogStore.java`
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/db/StateLogStoreSqls.java`
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/store/db/DbAndReportTcStateLogStore.java`
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/config/DbStateMachineConfig.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/impl/ProcessControllerImpl.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/impl/ProcessContextImpl.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/process/impl/CustomizeBusinessProcessor.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/handler/DefaultRouterHandler.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl/ProcessCtrlEventPublisher.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl/ProcessCtrlEventConsumer.java`
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl/DirectEventBus.java`
- `compatible/src/main/java/io/seata/saga/statelang/domain/StateType.java`
- `compatible/src/main/java/io/seata/saga/statelang/domain/ExecutionStatus.java`
