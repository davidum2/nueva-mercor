## Objective
- Add durable external-event approvals to Seata Saga so suspended workflows can resume through signals or timeouts across engine restarts.

## Important Details
- The domain additions belong in `org.apache.seata.saga.statelang.domain`.
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
- A Wait's possible subsequent destinations must be exactly its configured Next and its TimeoutNext when present.
- Entering Wait must persist a WAIT state instance in WA.
- Persist the suspended machine with execution status WA.
- Persist the suspended machine with `isRunning=false`.
- Wait entry must return without executing Next.
- Wait entry must leave the machine completion time unset.
- Wait entry must not report completion to the transaction coordinator.
- A fresh engine using the same database must reload a suspended workflow.
- A fresh engine must resume the reloaded workflow.
- Add `StateMachineInstance signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String, Object> payload)` to `StateMachineEngine`.
  - A matching signal must atomically claim the exact activation identified by waitStateInstanceId.
  - Persist a winning signal's activation status as SU.
  - Persist the signal payload as the activation's output parameters.
  - Record a null payload as an empty map.
  - Continue synchronously until another suspension or a terminal state.
  - Evaluate each Output expression using the recorded payload as its root.
  - Merge mapped signal outputs into machine context.
  - Preserve completed predecessors' outputs when merging mapped signal outputs.
  - Replaying the same event for an already satisfied activation must return the reloaded machine without running its continuation again.
  - A delayed duplicate for an older loop activation must not consume a newer activation of the same Wait state.
  - Null or blank required arguments must raise `EngineExecutionException` carrying `ParameterRequired` or `InvalidParameter`.
  - A nonexistent machine ID must report `ObjectNotExists`.
  - An event mismatch must report `OperationDenied`.
  - An activation already lost to timeout or compensation must report `OperationDenied`.
- Add `int fireDueTimeouts(java.time.Instant now)` to `StateMachineEngine`.
  - Claim persisted waits whose deadline is less than or equal to now.
  - Persist each timeout winner as SK.
  - Resume a timeout winner along TimeoutNext.
  - Return the number of claims won.
  - Leave indefinite waits suspended after a timeout sweep.
  - Leave waits whose deadline is later than now suspended after a timeout sweep.
  - After reconstruction, the engine must discover persisted waits with due deadlines.
  - After reconstruction, the engine must resume execution when a timeout claim wins.
  - A null now must raise `EngineExecutionException` carrying `InvalidParameter`.
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
- The solver planned new Wait support because the scoped feature-name search found no relevant implementation to reuse.
- The solver proposed `WaitStateImpl` for the domain implementation.
- The solver proposed registering `WaitStateHandler` through `StateMachineProcessHandler` for Wait execution.
- The solver had not chosen between a dedicated `WaitStateRouter` and reuse of `TaskStateRouter`.

## Work State
### Completed
- Located the working repository at `/workspace/repo`.
- The Java search under `saga` and `compatible` for `fireDueTimeouts`, `WaitState`, `getTimeoutNext` and `signal(` returned only `compatible/src/test/java/io/seata/common/LockAndCallback.java`.
- The complete visible `ExecutionStatus.java` result contains RU, SU, FA, UN and SK, plus the existing `getStatusString()` method.
- The `StateType.java` read was clipped after `LOOP_START`, leaving the state-type lookup implementation unseen.
- The `StateMachineEngine.java` read returned only a clipped opening excerpt.
- The `ProcessCtrlStateMachineEngine.java` read returned only a clipped opening excerpt.

### Active
- The exploration todo remains in_progress.
- Implementation items remain pending.
- No source edits have been made.
- The planned unit tests are pending execution.
- The planned Maven build is pending execution.
- The planned lint checks are pending execution.
- No execution results were recorded for these checks.
- The solver left open whether durable timeout storage needs a deadline column.

### Blocked
- No blocker is established.

## Next Move
1. Investigate durable Wait suspension, starting with `DbAndReportTcStateLogStore.java`.
2. Investigate database reload, starting with `DbStateMachineConfig.java`.
3. Inspect the output helper the solver named `ParameterUtils.createOutputParams`, whose behavior has not been shown.
4. Finish inspecting `SubStateMachineHandler.java` to understand nested execution.
5. Read the unread deprecated `io.seata.saga.statelang.domain.StateType` wrapper implementation.
6. Read the unread deprecated `io.seata.saga.statelang.domain.ExecutionStatus` wrapper implementation.
7. After exploration, begin the pending domain additions.
8. After exploration, begin the pending parser additions.

## Relevant Files
- Paths below are relative to `/workspace/repo`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/` holds `StateType.java`, `ExecutionStatus.java` and `State.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/domain/impl/` holds the partly read examples `BaseState.java`, `AbstractTaskState.java` and `ScriptTaskStateImpl.java`.
- `saga/seata-saga-statelang/src/main/java/org/apache/seata/saga/statelang/parser/` contains `StateParserFactory.java` and `impl/ScriptTaskStateParser.java`, both partly read.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/` contains the API target `StateMachineEngine.java` and implementation target `impl/ProcessCtrlStateMachineEngine.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` contains the named integration targets `StateMachineProcessHandler.java`, `StateMachineProcessRouter.java`, `routers/TaskStateRouter.java` and `handlers/SubStateMachineHandler.java`.
- `saga/seata-saga-engine/src/main/java/org/apache/seata/saga/engine/pcext/` also contains `utils/EngineUtils.java` and `interceptors/ServiceTaskHandlerInterceptor.java`, both partly read.
- `saga/seata-saga-engine-store/src/main/java/org/apache/seata/saga/engine/store/` contains the persistence targets `StateLogStore.java` and `db/StateLogStoreSqls.java`.
- `saga/seata-saga-spring/src/main/java/org/apache/seata/saga/engine/` contains `store/db/DbAndReportTcStateLogStore.java` and `config/DbStateMachineConfig.java`, located but unread.
- `compatible/src/main/java/io/seata/saga/statelang/domain/` contains the enum wrapper files `StateType.java` and `ExecutionStatus.java`.