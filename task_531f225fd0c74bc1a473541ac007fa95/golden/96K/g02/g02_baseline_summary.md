## Objective
- Add durable external-event approvals ("Wait" states) to Seata Saga so suspended workflows can resume through signals or timeouts across engine restarts, spanning the statelang domain, parser, engine, persistence layer, and deprecated compatible wrappers.

## Important Details
- Domain additions belong in `org.apache.seata.saga.statelang.domain`.
- Add `StateType.WAIT` with value `"Wait"`; state-type lookup must remain case-insensitive.
- Add `ExecutionStatus.WA` with value `"Waiting"`.
- `WaitState` interface extends `State`: `String getEvent()` (required, non-blank), `Map<String,Object> getOutput()` (optional mappings), `java.time.Duration getTimeout()` (optional), `String getTimeoutNext()` (optional); `WaitStateImpl` extends `BaseState`.
- Reject a definition containing only one of Timeout and TimeoutNext.
- A supplied Timeout must be a strictly positive ISO-8601 duration supporting fractional seconds (e.g. `PT1.5S`, `PT0.001S`); plan: parse via `java.time.Duration.parse` in `WaitStateParser` (parser-level validation).
- A Wait's possible subsequent destinations must be exactly its configured Next and its TimeoutNext when present — maps to modifying `StateMachineUtils.getAllPossibleSubsequentStates(State)` (used by the validator's graph traversal) with a WAIT case.
- Entering Wait must persist a WAIT state instance in WA, suspend the machine with status WA and `isRunning=false`, return without executing Next, leave completion time unset, and not report completion to the TC.
- Add `StateMachineInstance signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String,Object> payload)` to `StateMachineEngine`:
  - Matching signal atomically claims the exact activation identified by waitStateInstanceId.
  - Persist winning signal's activation status SU; payload recorded as activation's output params; null payload recorded as empty map.
  - Continue synchronously until another suspension or terminal state.
  - Evaluate each Output expression using the recorded payload as root; merge mapped outputs into machine context; preserve completed predecessors' outputs when merging.
  - Replaying the same event on an already satisfied activation returns the reloaded machine without re-running continuation.
  - A delayed duplicate for an older loop activation must not consume a newer activation of the same Wait state.
  - Null/blank required args raise `EngineExecutionException` with `ParameterRequired`/`InvalidParameter`; nonexistent machine ID reports `ObjectNotExists`; event mismatch reports `OperationDenied`; activation lost to timeout or compensation reports `OperationDenied`.
- Add `int fireDueTimeouts(java.time.Instant now)` to `StateMachineEngine`:
  - Claim persisted waits whose configured deadline ≤ now; persist each timeout winner as SK; resume along TimeoutNext; return number of claims won.
  - Leave indefinite waits and waits with later deadlines suspended after a sweep.
  - After engine reconstruction, discover persisted waits with due deadlines and resume when a claim wins.
  - Null now raises `EngineExecutionException` with `InvalidParameter`.
- Concurrent duplicate matching signals for the same Wait activation yield a single winning claim; signal vs due timeout, signal vs compensation, and timeout vs compensation races each have a single winner.
- A waiting child suspends its enclosing SubStateMachine state in WA and its parent machine in WA (`isRunning=false`); completing or timing out a child synchronously resumes parents through multiple nesting levels; apply each nesting level's output mappings during resumption.
- Ancestor compensation must cancel active descendant waits (including grandchildren) before compensating any completed predecessor.
- Add the WAIT constant to deprecated `io.seata.saga.statelang.domain.StateType` and WA to deprecated `io.seata.saga.statelang.domain.ExecutionStatus`; preserve wrap/unwrap round trips for every value of both wrappers.
- Deadline persistence decision (in progress): lean toward deriving deadline = state instance `gmtStarted` + timeout from the state machine definition reloaded from the repo (avoids schema changes), versus adding a `wait_deadline` column; needs confirmation against `StateLogStoreSqls`/table schema.
- `fireDueTimeouts` after reconstruction needs a way to enumerate persisted waiting machine instances; `StateLogStore` currently lacks a query-by-status method — plan to add e.g. a `queryStateMachineInstanceByStatus(ExecutionStatus)`-style method (naming TBD) implemented in `DbAndReportTcStateLogStore` via SQL on `seata_state_machine_instance` (verify `status` column in `StateLogStoreSqls`).
- Engine design: `WaitStateHandler` implements `StateHandler`; either a companion interceptor (analogous to `ServiceTaskHandlerInterceptor`, e.g. `WaitStateHandlerInterceptor`) or inline logic creates the WAIT state instance; register in `StateMachineProcessHandler`.
- Router choice still open: dedicated `WaitStateRouter` vs reuse of `TaskStateRouter`.
- `SubStateMachineHandler` calls `engine.start` and (in sync publisher mode) runs the child to completion within the parent handler thread; a suspended (WA) child means the parent's SubStateMachine state instance and parent machine instance must become WA with `isRunning=false`.
- Validator infra: `org.apache.seata.saga.statelang.validator.Rule` (SPI: `validate(StateMachine)`, `getName()`, `getHint()`) + `RuleFactory`.
- Useful `DomainConstants` seen: `VAR_NAME_STATEMACHINE_CONTEXT="context"`, `VAR_NAME_INPUT_PARAMS="inputParams"`, `VAR_NAME_OUTPUT_PARAMS="outputParams"`, `VAR_NAME_CURRENT_EXCEPTION`, `VAR_NAME_BUSINESSKEY="_business_key_"`, `VAR_NAME_SUB_MACHINE_PARENT_ID`, `VAR_NAME_CURRENT_CHOICE`, `VAR_NAME_STATEMACHINE_ERROR_CODE/_MSG`, `SERVICE_TYPE_SPRING_BEAN="SpringBean"`.
- `BaseStateParser.parseBaseAttributes` reads `Comment`, `Next`, `Extensions` keys from the node map.
- `StateInstanceImpl` fields: id, machineInstanceId, name, `StateType type`, serviceName, serviceMethod, serviceType, businessKey, gmtStarted, gmtUpdated, gmtEnd, isForUpdate, exception, status.
- `StateMachineInstanceImpl` fields: id, machineId, tenantId, parentId, gmtStarted, businessKey, startParams, status, stateList, etc.
- `SucceedEndStateHandler.process` is empty; terminal semantics handled via `StateInstruction` end flag/routing.
- `StateMachineProcessHandler` statically registers handlers: ChoiceStateHandler, CompensationTriggerStateHandler, FailEndStateHandler, LoopStartStateHandler, ScriptTaskStateHandler, ServiceTaskStateHandler, SubStateMachineHandler, SucceedEndStateHandler.
- Feature-name search found no existing implementation to reuse; new Wait support is required.

## Work State
### Completed
- Located the working repository at `/workspace/repo`.
- Search under `saga` and `compatible` for `fireDueTimeouts`, `WaitState`, `getTimeoutNext`, `signal(` returned only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- Confirmed full `ExecutionStatus.java` contains RU, SU, FA, UN, SK plus `getStatusString()`.
- Read (this session, several truncated): `DomainConstants.java`, `StateLogStore.java` (recordStateMachineStarted/recordStateMachineFinished seen), `validator/Rule.java`, `validator/RuleFactory.java`, `StateMachineUtils.java`, `StateMachineParserImpl.java`, `AbstractTaskStateParser.java`, `BaseStateParser.java` (full), `StateInstruction.java`, `ParameterUtils.java`, `SucceedEndStateHandler.java` (full), `ProcessCtrlStateMachineEngine.java`, `StateMachineEngine.java`, `StateMachineProcessHandler.java`, `TaskStateRouter.java`, `EngineUtils.java`, `ServiceTaskHandlerInterceptor.java`, `SubStateMachineHandler.java`, `StateInstanceImpl.java`, `StateMachineInstanceImpl.java`, `DbAndReportTcStateLogStore.java`.
- Confirmed the destinations requirement maps to `StateMachineUtils.getAllPossibleSubsequentStates`.
- Confirmed no source edits have been made yet.

### Active
- Exploration is still in progress; most engine/store file reads were truncated and need completion (`ProcessCtrlStateMachineEngine`, `StateMachineProcessHandler`, `TaskStateRouter`, `EngineUtils`, `ServiceTaskHandlerInterceptor`, `SubStateMachineHandler`, `ParameterUtils`, `StateInstruction`, `DbAndReportTcStateLogStore`).
- Open design decisions: deadline persistence approach (derived vs new column), StateLogStore query method(s) for waiting instances, `WaitStateRouter` vs `TaskStateRouter`, interceptor vs inline state-instance creation.
- Implementation items remain pending.
- Planned unit tests, Maven build, and lint checks are pending execution; no results recorded.

### Blocked
- No blocker is established.

## Next Move
1. Finish reading `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/store/db/DbAndReportTcStateLogStore.java` (state instance persistence, `getStateMachineInstance` deserialization, TC reporting paths).
2. Read `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/db/StateLogStoreSqls.java` to confirm `seata_state_machine_instance`/`seata_state_instance` columns (esp. `status`) for the waiting-instance query and deadline derivation.
3. Read `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/config/DbStateMachineConfig.java` and `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/config/AbstractStateMachineConfig.java`/`DefaultStateMachineConfig` (event publisher sync/async, `getProcessCtrlEventPublisher`).
4. Read remaining engine pieces: `DefaultStatusDecisionStrategy`, `LoopStartStateHandler`, `CompensationHolder`, `LoopTaskUtils`, `StateMachineImpl` (getState), expression utils.
5. Read the unread deprecated wrappers `compatible/src/main/java/io/seata/saga/statelang/domain/StateType.java` (clipped after LOOP_START) and `ExecutionStatus.java`.
6. Inspect test infrastructure: `saga/seata-saga-engine/src/test`, `saga/seata-saga-spring/src/test`, `DbAndReportTcStateLogStore`-related tests.
7. After exploration, implement: domain (`StateType.WAIT`, `ExecutionStatus.WA`, `WaitState`, `WaitStateImpl`), parser (`WaitStateParser`, `StateMachineUtils` WAIT case), engine (`WaitStateHandler` + interceptor, `StateMachineProcessHandler` registration, `signal()`/`fireDueTimeouts()` in `ProcessCtrlStateMachineEngine`), store additions, compatible wrapper constants.
8. Run planned unit tests, Maven build, and lint checks.

## Relevant Files
- Paths relative to `/workspace/repo`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` — `StateType.java`, `ExecutionStatus.java`, `State.java`, `DomainConstants.java`; targets for WAIT/WA and `WaitState`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` — `BaseState.java`, `AbstractTaskState.java`, `StateInstanceImpl.java`, `StateMachineInstanceImpl.java`; `WaitStateImpl` target.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/` — `StateParserFactory.java`, `impl/StateMachineParserImpl.java`, `impl/BaseStateParser.java` (full read), `impl/AbstractTaskStateParser.java`; `WaitStateParser` target.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/utils/StateMachineUtils.java` — `getAllPossibleSubsequentStates` needs WAIT case.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/` — `Rule.java`, `RuleFactory.java`; definition validation infra.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/` — `StateMachineEngine.java`, `impl/ProcessCtrlStateMachineEngine.java`; `signal`/`fireDueTimeouts` targets.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` — `StateMachineProcessHandler.java` (handler registry), `StateInstruction.java`, `routers/TaskStateRouter.java`, `handlers/SubStateMachineHandler.java`, `handlers/SucceedEndStateHandler.java` (full), `interceptors/ServiceTaskHandlerInterceptor.java`, `utils/EngineUtils.java`, `utils/ParameterUtils.java`; `WaitStateHandler`/interceptor target.
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/` — `StateLogStore.java`, `db/StateLogStoreSqls.java` (unread).
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/store/db/DbAndReportTcStateLogStore.java` and `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/config/DbStateMachineConfig.java` — persistence/reload implementation.
- `compatible/src/main/java/io/seata/saga/statelang/domain/` — deprecated enum wrappers `StateType.java` (partly read, clipped after LOOP_START), `ExecutionStatus.java`.
- `compatible/src/test/java/io/seata/common/LockAndCallback.java` — only search hit; unrelated.
