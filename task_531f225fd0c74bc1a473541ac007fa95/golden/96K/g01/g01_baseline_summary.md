## Objective
- Implement asynchronous approvals for Seata Saga: add a durable "Wait" state type (StateType.WAIT / WaitState) and ExecutionStatus.WA ("Waiting") in org.apache.seata.saga.statelang.domain, with engine support for suspending state machines (persisted), resuming via StateMachineEngine.signal(...), firing expired waits via fireDueTimeouts(Instant), nested SubStateMachine suspension/resume, compensation cancellation of active waits, and matching io.seata compatible-module constants with preserved wrap/unwrap round trips.

## Important Details
- Domain requirements:
  - `StateType.WAIT` with value "Wait"; state-type lookup must be case-insensitive.
  - `WaitState` interface extends `State`: `String getEvent()` (required, non-blank), `Map<String,Object> getOutput()` (optional), `java.time.Duration getTimeout()` (optional), `String getTimeoutNext()` (optional).
  - Reject definitions unless Timeout and TimeoutNext are both present or both absent; supplied timeouts must be strictly positive ISO-8601 durations (incl. fractional seconds).
  - For a Wait state, possible next destinations = exactly configured Next plus TimeoutNext when present (no others).
  - `ExecutionStatus.WA` = "Waiting".
- Wait entering semantics: persist WAIT state instance with status WA; suspend machine with status WA and isRunning=false; return without executing Next, without setting machine completion time, without reporting completion to TC. A fresh engine using the same DB must reload and resume the suspended workflow.
- `StateMachineInstance signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String,Object> payload)` on StateMachineEngine:
  - Matching event atomically claims that exact activation; persist status SU and output params = payload (null payload recorded as empty map); synchronously continue until another suspension or terminal state.
  - Evaluate each Output expression against the recorded payload as root; merge mapped values into machine context without losing completed predecessors' outputs.
  - Repeating same event for an already-satisfied activation returns the reloaded machine without repeating continuation; in loops, a delayed duplicate targeting an older activation must not consume a newer activation of the same Wait state.
  - Errors: null/blank required args → EngineExecutionException with ParameterRequired or InvalidParameter; nonexistent machine ID → ObjectNotExists; event mismatch or activation lost to timeout/compensation → OperationDenied.
- `int fireDueTimeouts(java.time.Instant now)` on StateMachineEngine: claim persisted waits whose configured deadline <= now, persist each winner as SK, continue along TimeoutNext, return number of claims won; indefinite/not-yet-due waits stay suspended; must work after engine reconstruction; null `now` → EngineExecutionException with InvalidParameter.
- Concurrency: signal delivery, timeout sweeps, and compensation must have a single winner per activation (incl. concurrent duplicate signals).
- SubStateMachine: waiting child suspends its enclosing SubStateMachine state and parent machine with WA; completing/timing out child synchronously resumes parent through multiple nesting levels with each level's output mappings applied; compensating an ancestor cancels active descendant waits before any completed predecessor is compensated (incl. waits in grandchildren).
- Compatible module: deprecated `io.seata.saga.statelang.domain.StateType` and `ExecutionStatus` wrappers need matching WAIT and WA constants, preserving wrap/unwrap round trips for every value.
- Repo facts: /workspace/repo is apache/incubator-seata (HEAD 2efc2aab1). No existing Wait/signal/fireDueTimeouts code anywhere (grep of saga + compatible found nothing; only false positive compatible/src/test/java/io/seata/common/LockAndCallback.java) — implement from scratch; evaluation likely via hidden tests.
- Module layout: saga/{seata-saga-annotation, seata-saga-engine, seata-saga-engine-store, seata-saga-processctrl, seata-saga-rm, seata-saga-spring, seata-saga-statelang, seata-saga-statemachine-designer}.
- statelang layout: domain, domain/impl, parser, parser/impl, parser/utils, validator, validator/impl (validator package relevant for Timeout/TimeoutNext pair validation).
- `StateParserFactory` maps state-type string → parser impl (Choice, CompensateSubMachine, CompensationTrigger, FailEnd, ScriptTask, ServiceTask, SubMachine, SucceedEnd) — needs WaitStateParser registration.
- `StateMachineProcessHandler` maps state type → handler (Choice/CompensationTrigger/FailEnd/LoopStart/ScriptTask/ServiceTask/SubStateMachine/SucceedEnd handlers) — needs a Wait handler; `StateMachineProcessRouter` uses EndStateRouter + TaskStateRouter.
- StateLogStore interface lives in seata-saga-engine-store; DB implementation `DbAndReportTcStateLogStore` and `DbStateMachineConfig` live in seata-saga-spring (org.apache.seata.saga.engine.store.db / engine.config); SQLs in `StateLogStoreSqls`.
- Domain impls: `BaseState` (name/type/comment/next/extensions/stateMachine), `AbstractTaskState` (compensateState, isForCompensation, isForUpdate, retry, catches, input, output Map<String,Object>, status, inputExpressions, outputExpressions); `ExecutionStatus` currently RU/SU/FA/UN/SK with getStatusString(); StateType similar string-based enum.
- Tooling note: the `glob` tool failed ("ripgrep execution failed"); use bash `find`/`grep` instead.

## Work State
### Completed
- Explored repo root, saga module tree, engine/engine-store/processctrl/spring file listings, compatible module file listing (io.seata wrappers for statelang domain, engine, store, repo).
- Read (several truncated): StateType.java, ExecutionStatus.java, State.java, StateInstance.java, StateMachineInstance.java, StateMachineEngine.java, ProcessCtrlStateMachineEngine.java, StateMachineProcessHandler.java, StateMachineProcessRouter.java, TaskStateRouter.java, SubStateMachineHandler.java, EngineUtils.java, ServiceTaskHandlerInterceptor.java, BaseState.java, StateParserFactory.java, StateParser.java, ScriptTaskStateParser.java, ScriptTaskStateImpl.java, AbstractTaskState.java.
- Confirmed no pre-existing Wait feature anywhere.
- Created 13-item todo list (domain, parser, engine handler/router, persistence/suspend/resume, signal, fireDueTimeouts, SubStateMachine nesting, compatible wrappers, DB schema/serialization, tests, build/lint).

### Active
- Exploration phase in progress (todo #1 "Explore saga statelang domain, engine, store modules and compatible wrappers" marked in_progress). Most reads were truncated; full content of key engine/store/spring/compatible files still unread.

### Blocked
- (none — except `glob` tool unusable; use bash find/grep).

## Next Move
1. Finish reading the key remaining files before implementing: remainder of StateType.java (lookup method used by case-insensitive lookup), DomainConstants.java, StateInstruction.java, SucceedEndStateHandler.java, EndStateRouter.java, LoopStartStateHandler.java, StateLogStore.java, DbAndReportTcStateLogStore.java, StateLogStoreSqls.java, DbStateMachineConfig.java, AbstractStateMachineConfig.java, ParameterUtils.java (createOutputParams), CompensationHolder.java, ProcessCtrlStateMachineEngine.java (full), StateMachineParserFactory/StateMachineParserImpl + validator package, and compatible io/seata StateType.java & ExecutionStatus.java (wrap/unwrap mechanics).
2. Then implement in order: statelang domain (StateType.WAIT, ExecutionStatus.WA, WaitState interface + WaitStateImpl, TaskState-style getters), WaitStateParser + StateParserFactory registration + validator rules (Timeout/TimeoutNext pairing, strictly positive ISO-8601 durations incl. fractional seconds), then engine handler/router + suspension persistence, signal(...), fireDueTimeouts(...), SubStateMachine nesting/compensation, then compatible wrappers, DB/store serialization (wait deadline persistence), then unit tests and `mvn` build of touched modules.

## Relevant Files
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/StateType.java — add WAIT("Wait"); case-insensitive lookup lives here (file read truncated at LOOP_START).
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/ExecutionStatus.java — add WA("Waiting") next to RU/SU/FA/UN/SK.
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/State.java — base interface for WaitState.
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/DomainConstants.java — shared constants (not yet read).
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/BaseState.java, .../impl/AbstractTaskState.java, .../impl/ScriptTaskStateImpl.java — impl patterns for new WaitStateImpl.
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/StateParserFactory.java, .../parser/impl/ScriptTaskStateParser.java, .../parser/impl/AbstractTaskStateParser.java — add WaitStateParser registration/parse logic.
- /workspace/repo/saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/validator/ and validator/impl/ — definition validation (Timeout/TimeoutNext pairing, positive durations).
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/StateMachineEngine.java — add signal(...) and fireDueTimeouts(...).
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/impl/ProcessCtrlStateMachineEngine.java — main engine impl; implement signal/timeout/suspend logic.
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/StateMachineProcessHandler.java, .../StateMachineProcessRouter.java, .../routers/TaskStateRouter.java, .../routers/EndStateRouter.java, .../StateInstruction.java — handler/router registration and routing (Wait destinations = Next/TimeoutNext).
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/handlers/SubStateMachineHandler.java, .../handlers/SucceedEndStateHandler.java, .../handlers/ServiceTaskStateHandler.java, .../handlers/CompensationTriggerStateHandler.java — nesting, completion, compensation integration points.
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/interceptors/ServiceTaskHandlerInterceptor.java, .../pcext/utils/EngineUtils.java, .../pcext/utils/ParameterUtils.java, .../pcext/utils/CompensationHolder.java, .../pcext/utils/LoopTaskUtils.java — state instance creation, output param evaluation/merge, loop handling.
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/exception/EngineExecutionException.java, /workspace/repo/common (FrameworkErrorCode: ParameterRequired, InvalidParameter, ObjectNotExists, OperationDenied) — error codes for signal/fireDueTimeouts.
- /workspace/repo/saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/StateLogStore.java, .../store/db/StateLogStoreSqls.java — persistence interface/SQLs to extend for WA status + wait deadline claims.
- /workspace/repo/saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/store/db/DbAndReportTcStateLogStore.java, /workspace/repo/saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/config/DbStateMachineConfig.java — DB persistence + engine reconstruction/reload path.
- /workspace/repo/saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/config/AbstractStateMachineConfig.java, /workspace/repo/saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/impl/DefaultStateMachineConfig.java — config wiring.
- /workspace/repo/compatible/src/main/java/io/seata/saga/statelang/domain/StateType.java, .../ExecutionStatus.java, /workspace/repo/compatible/src/main/java/io/seata/saga/engine/StateMachineEngine.java, .../engine/impl/ProcessCtrlStateMachineEngine.java, .../engine/store/impl/StateLogStoreImpl.java — deprecated wrappers needing WAIT/WA + round-trip preservation and new API passthrough.
- /workspace/repo/saga/seata-saga-processctrl/src/main/java/org/apache/seata/saga/proctrl/ (ProcessContext, HierarchicalProcessContext, ProcessController, eventing/*) — process control primitives used by engine.
