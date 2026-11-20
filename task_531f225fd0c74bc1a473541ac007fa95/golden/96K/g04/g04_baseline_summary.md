## Objective
- Add a durable Wait state to Seata Saga: workflows suspend on Wait with persisted `WA` status and resume synchronously via matching signals or due timeouts across engine restarts, including nested SubStateMachine parents and compensation-driven cancellation.

## Important Details
- Domain additions belong in `org.apache.seata.saga.statelang.domain`.
- Add `StateType.WAIT` with value `"Wait"`; state-type lookup must remain case-insensitive.
- Add `ExecutionStatus.WA` with value `"Waiting"` (existing values `RU`, `SU`, `FA`, `UN`, `SK`; `getStatusString()` exists).
- `WaitState` must be an interface extending `State` with `String getEvent()` (required, non-blank), `Map<String, Object> getOutput()` (optional), `java.time.Duration getTimeout()` (optional), `String getTimeoutNext()` (optional).
- Reject a definition containing only one of Timeout and TimeoutNext; supplied Timeout must be ISO-8601 (parse with `java.time.Duration.parse`), strictly positive, and support fractional seconds.
- A Wait's possible subsequent destinations are its configured `Next` plus `TimeoutNext` when present.
- Entering Wait must persist a WAIT state instance in `WA`; persist the suspended machine with status `WA` and `isRunning=false`; return without executing Next; leave completion time unset; skip completion reporting to the transaction coordinator.
- A fresh engine using the same database must reload a suspended workflow and resume it.
- Add `StateMachineInstance signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String, Object> payload)` to `StateMachineEngine`:
  - Atomically claim the exact activation identified by `waitStateInstanceId` on a matching event.
  - Persist a winning signal's activation status as `SU`; persist the payload as the activation's output params (null payload → empty map).
  - Continue synchronously until another suspension or a terminal state; evaluate each Output expression with the recorded payload as root; merge mapped outputs into machine context while preserving completed predecessors' outputs.
  - Replaying the same event on a satisfied activation returns the reloaded machine without rerunning the continuation.
  - A delayed duplicate for an older loop activation must not consume a newer activation of the same Wait state.
  - Null/blank required args → `EngineExecutionException` with `ParameterRequired`/`InvalidParameter`; nonexistent machine ID → `ObjectNotExists`; event mismatch → `OperationDenied`; activation lost to timeout/compensation → `OperationDenied`.
- Add `int fireDueTimeouts(java.time.Instant now)` to `StateMachineEngine`:
  - Claim persisted waits whose deadline ≤ `now` (deadline derived from persisted `gmt_started` plus configured `Timeout`); persist timeout winners as `SK`; resume along `TimeoutNext`; return the number of claims won.
  - Leave indefinite waits and future-deadline waits suspended; after reconstruction the engine discovers due waits and resumes on a winning claim.
  - Null `now` → `EngineExecutionException` with `InvalidParameter`.
- Single-winner races: concurrent duplicate matching signals; matching signal vs due timeout; signal vs compensation; timeout vs compensation.
- Nesting: a waiting child suspends its enclosing SubStateMachine state and parent machine in `WA`; completing/timing out a child synchronously resumes parents through multiple nesting levels, applying each level's output mappings.
- Ancestor compensation must cancel active descendant waits (including grandchildren) before compensating any completed predecessor.
- Add matching `WAIT`/`WA` constants to the deprecated `io.seata.saga.statelang.domain.StateType` and `ExecutionStatus` wrappers; preserve wrap/unwrap round trips for every value of both wrappers.
- Verified code facts: `StateLogStore` declares `recordStateMachineStarted/recordStateMachineFinished(StateMachineInstance, ProcessContext)`; `StateMachineEngine` declares `start(String stateMachineName, String tenantId, Map<String, Object> startParams)` and imports `ForwardInvalidException`; `StateInstruction` implements `Instruction` with visible fields `stateName`, `stateMachineName`, `tenantId`, `end`; `SucceedEndStateHandler` has a no-op `process(ProcessContext)`; `ParameterUtils` declares `ResourceLock INPUT_LOCK`; `StateInstanceImpl` has visible `Date` fields `gmtStarted`, `gmtUpdated`, `gmtEnd`; `StateMachineInstanceImpl` has fields `id`, `machineId`, `tenantId`, `parentId`, `gmtStarted`; `ProcessControllerImpl.process` calls `businessProcessor.process(context)` then `businessProcessor.route(context)`; `CustomizeBusinessProcessor` declares a `processHandlers` map.
- Verified SQL facts: `StateLogStoreSqls.STATE_MACHINE_INSTANCE_FIELDS` = `id, machine_id, tenant_id, parent_id, business_key, gmt_started, gmt_end, status, compensation_status, is_running, gmt_updated, start_params, end_params, excep`; `STATE_MACHINE_INSTANCE_FIELDS_WITHOUT_PARAMS` omits the params/excep columns; `RECORD_STATE_MACHINE_STARTED_SQL` inserts into `${TABLE_PREFIX}state_machine_inst`; the `DbAndReportTcStateLogStore` row mapper reads type via `StateType.getStateType(resultSet.getString("type"))` and status via `ExecutionStatus.valueOf(resultSet.getString("status"))`.
- Verified `DomainConstants` constants: `COMPENSATE_SUB_MACHINE_STATE_NAME_PREFIX = "_compensate_sub_machine_state_"`, `SERVICE_TYPE_SPRING_BEAN = "SpringBean"`, `VAR_NAME_STATEMACHINE_CONTEXT = "context"`, `VAR_NAME_INPUT_PARAMS`, `VAR_NAME_OUTPUT_PARAMS`, `VAR_NAME_CURRENT_EXCEPTION`, `VAR_NAME_BUSINESSKEY = "_business_key_"`, `VAR_NAME_SUB_MACHINE_PARENT_ID = "_sub_machine_parent_id_"`, `VAR_NAME_CURRENT_CHOICE = "_current_choice_"`, `VAR_NAME_STATEMACHINE_ERROR_CODE = "_statemachine_error_code_"`.
- Design decisions: `WaitStateImpl` extends `BaseState` (not a task state); `WaitStateParser` extends `BaseStateParser` with parse-time validation throwing `ParserException`, registered for `"Wait"` in `StateParserFactory`; no schema change (status columns already exist on `state_machine_inst` and `state_inst`); new wait-query SQL must match the type/status encoding written by `recordStateStarted`.
- Engine flow reasoning: `ProcessCtrlEventPublisher` publishes through `DirectEventBus` to `ProcessCtrlEventConsumer` synchronously until the routed instruction is null; `StateMachineProcessRouter.route` calls `EngineUtils.endStateMachine(context)` in its finally block when `instruction == null && !stateInstruction.isEnd()`; `TaskStateRouter.route` returns null when `stateInstruction.isEnd()` or when `DomainConstants.VAR_NAME_IS_LOOP_STATE` is true, skipping `endStateMachine`.
- `WaitStateHandler.process` will persist the WAIT state instance (`WA`) and suspended machine, then set `StateInstruction.end = true` and return without routing Next; register `WaitStateHandler` for `StateType.WAIT` in `StateMachineProcessHandler`; reuse `TaskStateRouter` for `StateType.WAIT` rather than a dedicated router; all entry logic lives in the handler without interceptors (open: implement `StateHandler` directly vs `InterceptableStateHandler`).
- `ServiceTaskHandlerInterceptor.preProcess` records the state instance as `RU` via `recordStateStarted` before handler execution; `postProcess` returns early when the state instance is null or `!stateMachineInstance.isRunning()`.
- `ProcessCtrlStateMachineEngine`: `startInternal` builds a `ProcessContext` via `ProcessContextBuilder` and publishes to `processCtrlEventPublisher`; `clearUp` cleans ThreadLocal state (e.g., XID); `compensateInternal` demonstrates reload → rebuild context → set instruction → publish with `recordStateMachineRestarted`, and only calls `checkStatus` when `compensationStatus` is non-null (a suspended never-compensated machine can be compensated).
- `reloadStateMachineInstance` with `replayContextVariables` replays each state's Output mappings via `ParameterUtils.createOutputParams(resolver, state, output)`; `replayContextVariables` currently casts to `ServiceTaskStateImpl` and must be adjusted to handle `WaitState`.
- `StateInstruction.getState(context)` resolves a temporary state or looks up by name from `State.getStateMachine()`; `EngineUtils.generateParentId` formats parentId from parent machine instance ID + `SEPERATOR_PARENT_ID` + parent state instance ID (constant still to verify in `DomainConstants`).
- Store/claim design: state-row CAS claim SQL on `${TABLE_PREFIX}state_inst` requiring `status='WA'` (one updated row = winner); a losing concurrent duplicate matching signal returns the reloaded machine (winner already persisted `SU`) instead of `OperationDenied`; machine-suspension SQL on `${TABLE_PREFIX}state_machine_inst` sets `status='WA'`, `is_running=false` (open: `WHERE id = ?` vs optimistic `gmt_updated` check pending `recordStateFinished` read); dedicated machine-resume SQL sets `status='RU'`, `is_running=true` rather than modifying shared `updateStateMachineRunningStatusSql`; state-level wait query on `${TABLE_PREFIX}state_inst` finds waiting activations globally including child machines; omit the `ProcessContext` parameter from new wait-claim store methods (no TC reporting); add `updateStateExecutionStatus(StateInstance, ProcessContext)` to `StateLogStore` because parent `SUB_STATE_MACHINE` states start `RU` and must be persisted `WA`; check existing `StateLogStore` implementers in tests before adding methods.
- `fireDueTimeouts` must verify via `getStateMachineInstance` that the machine is still `WA` before claiming; the state-row CAS `WA`→`SK` protects per-activation races.
- `SubStateMachineHandler`: set parent state instance `ExecutionStatus.WA` when child `engine.start` returns `WA`; persist parent machine `WA`/`is_running=false`; set `StateInstruction.end = true`; return without routing `Next`; resume a suspended parent from its `SUB_STATE_MACHINE` state's `Next` after parsing `parentId`, applying `ParameterUtils.createOutputParams`, calling `recordStateFinished`; recurse via `resumeParents` when a resumed parent finishes — continue along `Next` even when the child finished `FA` so the status decision strategy decides the final parent status.
- Cancellation design: scan state instances via `queryStateInstanceListByMachineInstanceId`; CAS-claim each active `WA` WAIT state instance to `SK` (cancelled = skipped); if the CAS fails because a signal already claimed `SU`, compensation proceeds (an already-satisfied wait cannot be cancelled under the single-winner rule); recurse into child machines of each active `WA` `SUB_STATE_MACHINE` state via `queryStateMachineInstanceByParentId(generateParentId(stateInstance))`; place the helper at `WaitStateUtils.cancelActiveDescendantWaits(context, stateMachineInstance)` and invoke it from `CompensationTriggerStateHandler` before compensation stack processing.
- Add `DomainConstants.OPERATION_NAME_SIGNAL` = `"signal"` for continuation contexts because `OPERATION_NAME_FORWARD` triggers retried-state detection in `ServiceTaskHandlerInterceptor.preProcess`.
- `StateMachineProcessRouter` imports `EndStateRouter` and `TaskStateRouter`; `StateMachineProcessHandler` imports `SubStateMachineHandler` and `SucceedEndStateHandler`.

## Work State
### Completed
- Located `/workspace/repo`; listed the `saga` module source trees via bash `ls`.
- Java search matched only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- Read in full: `ExecutionStatus.java`, `SucceedEndStateHandler.java`, `BaseStateParser.java`, `Rule.java`.
- Read `StateType.java` up to `LOOP_START`; read `DbAndReportTcStateLogStore.java` lines 1021–1043 (row mapper).
- Issued reads of key files (transcript shows clipped excerpts; only facts above verified): `DbAndReportTcStateLogStore.java`, `StateLogStore.java`, `StateLogStoreSqls.java`, `ProcessCtrlStateMachineEngine.java`, `StateMachineEngine.java`, `SubStateMachineHandler.java`, `EngineUtils.java`, `DomainConstants.java`, `ParameterUtils.java`, `StateMachineProcessRouter.java`, `TaskStateRouter.java`, `StateInstruction.java`, `StateMachineProcessHandler.java`, `ProcessControllerImpl.java`, `CustomizeBusinessProcessor.java`, `ServiceTaskHandlerInterceptor.java`.
- Verified visible imports for `DbAndReportTcStateLogStore` (TC classes `GlobalStatus`, `BranchStatus`, `BranchType`, `RootContext`, `TransactionException`), `SubStateMachineHandler` (`InterceptableStateHandler`, `StateHandlerInterceptor`, `StateLogStore`), `EngineUtils` (`ScriptTaskStateHandler`, `HierarchicalProcessContext`, `TaskState.ExceptionMatch`), `TaskStateRouter` (`CompensationHolder`, `LoopTaskUtils`, `CompensateSubStateMachineState`).

### Active
- The exploration todo remains `in_progress`.
- Zero source edits have been made; implementation items, unit tests, Maven builds, and lint checks all remain pending with no recorded results.

### Blocked
- The `glob` tool fails with `ripgrep execution failed`; bash `ls` is the workaround for file discovery.
- Reads of large files return clipped excerpts in the transcript; bodies of `recordStateStarted`, `recordStateFinished`, `createOutputParams`, and handler internals still need verification.

## Next Move
1. Finish reading `DbAndReportTcStateLogStore.java` (record states, `recordStateFinished`, `recordStateMachineRestarted`, query methods) to finalize the suspend/resume SQL shape.
2. Finish `ParameterUtils.java` (`createOutputParams`) and `DomainConstants.java` (`SEPERATOR_PARENT_ID`, `OPERATION_NAME_*` constants).
3. Read `CompensationHolder.java`, `CompensationTriggerStateHandler.java`, `DefaultStatusDecisionStrategy.java`, `EndStateRouter`, `EndStateRouterInterceptor.java`.
4. Read proctrl internals: `ProcessCtrlEventPublisher.java`, `ProcessCtrlEventConsumer.java`, `DirectEventBus.java`, `ProcessContextBuilder`, `ProcessContextImpl.java`, `DefaultRouterHandler.java`, plus full `ProcessControllerImpl.java` and `CustomizeBusinessProcessor.java`.
5. Read `StateMachineUtils.java`, remaining statelang domain/parser/validator files, finish `StateType.java` past `LOOP_START`.
6. Read the deprecated `io.seata.saga.statelang.domain` wrappers and compatible engine wrappers; inspect tests under `saga/seata-saga-engine/src/test` and `saga/seata-saga-spring/src/test` (including `StateLogStore` implementers).
7. Add `StateType.WAIT` (`"Wait"`) and `ExecutionStatus.WA` (`"Waiting"`).
8. Add `WaitState` interface and `WaitStateImpl` (extends `BaseState`); update deprecated wrappers with round-trip preservation.
9. Implement `WaitStateParser` (extends `BaseStateParser`, ISO-8601 validation, `ParserException`) and register for `"Wait"` in `StateParserFactory.java`; update `StateMachineUtils.getAllPossibleSubsequentStates`.
10. Add SQL constants (wait-claim, suspend, resume, wait-query) to `StateLogStoreSqls.java`; add `StateLogStore` methods (claim/suspend/resume/query plus `updateStateExecutionStatus`).
11. Implement the store methods in `DbAndReportTcStateLogStore.java`.
12. Implement `WaitStateHandler` and register it for `StateType.WAIT` in `StateMachineProcessHandler.java`.
13. Update `SubStateMachineHandler.java` for parent `WA` suspension and synchronous parent-chain resumption (`resumeParents`).
14. Implement `signal` and `fireDueTimeouts` on `StateMachineEngine`/`ProcessCtrlStateMachineEngine`, including `DomainConstants.OPERATION_NAME_SIGNAL` and replay handling in `reloadStateMachineInstance`.
15. Implement `WaitStateUtils.cancelActiveDescendantWaits` and invoke it from `CompensationTriggerStateHandler` before compensating predecessors.
16. Add unit tests for durable Wait behavior (reload/resume, races, nesting, cancellation).
17. Run Maven builds and lint checks.

## Relevant Files
- Paths relative to `/workspace/repo`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` — `StateType.java`, `ExecutionStatus.java`, `State.java`, `DomainConstants.java`; target for new `domain/WaitState.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` — `BaseState.java`, `AbstractTaskState.java`, `ScriptTaskStateImpl.java`, `StateInstanceImpl.java`, `StateMachineInstanceImpl.java`, `StateMachineImpl.java`; target for new `domain/impl/WaitStateImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/` — `StateParserFactory.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/impl/` — `BaseStateParser.java`, `AbstractTaskStateParser.java`, `ScriptTaskStateParser.java`; target for new `WaitStateParser`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/utils/` — `StateMachineUtils.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/` — `Rule.java`, `RuleFactory.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/` — `StateMachineEngine.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/config/` — `AbstractStateMachineConfig.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/impl/` — `ProcessCtrlStateMachineEngine.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/strategy/impl/` — `DefaultStatusDecisionStrategy.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` — `StateMachineProcessHandler.java`, `StateMachineProcessRouter.java`, `StateInstruction.java`, `InterceptableStateHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/` — `SubStateMachineHandler.java`, `SucceedEndStateHandler.java`, `CompensationTriggerStateHandler.java`; target for new `WaitStateHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/routers/` — `TaskStateRouter.java`, `EndStateRouter.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/interceptors/` — `ServiceTaskHandlerInterceptor.java`, `EndStateRouterInterceptor.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/utils/` — `EngineUtils.java`, `ParameterUtils.java`, `CompensationHolder.java`; target for new `WaitStateUtils.java`.
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/` — `StateLogStore.java`, `db/StateLogStoreSqls.java`.
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/store/db/` — `DbAndReportTcStateLogStore.java`.
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/config/` — `DbStateMachineConfig.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/impl/` — `ProcessControllerImpl.java`, `ProcessContextImpl.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/process/impl/` — `CustomizeBusinessProcessor.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/handler/` — `DefaultRouterHandler.java`.
- `saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/eventing/impl/` — `ProcessCtrlEventPublisher.java`, `ProcessCtrlEventConsumer.java`, `DirectEventBus.java`.
- `compatible/src/main/java/io/seata/saga/statelang/domain/` — deprecated `StateType.java`, `ExecutionStatus.java` wrappers needing `WAIT`/`WA` plus round-trip preservation.
- `compatible/src/test/java/io/seata/common/LockAndCallback.java` — only Java search hit so far.
- Test dirs: `saga/seata-saga-engine/src/test`, `saga/seata-saga-spring/src/test`.
