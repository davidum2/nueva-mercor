# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the objective of implementing asynchronous approvals for Seata Saga by adding a durable Wait state type with `StateType.WAIT` and `WaitState` plus `ExecutionStatus.WA` in org.apache.seata.saga.statelang.domain.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: minor
Description:
Specifies `StateType.WAIT` with the value `Wait` and a case-insensitive state-type lookup.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: minor
Description:
Specifies `ExecutionStatus.WA` with the value `Waiting`.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
Specifies that the `WaitState` interface extends `State` with `String getEvent()` required and non-blank and with optional `Map<String,Object> getOutput()`, `java.time.Duration getTimeout()`, and `String getTimeoutNext()`.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States that a Wait definition is rejected unless Timeout and TimeoutNext are both present or both absent and that a supplied timeout must be a strictly positive ISO-8601 duration allowing fractional seconds.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
States that the possible next destinations of a Wait state are exactly the configured Next plus TimeoutNext when present.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: major
Description:
Specifies `signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String,Object> payload)` on `StateMachineEngine` as atomically claiming the matching activation, persisting status SU with the payload as output params where a null payload is recorded as an empty map, and synchronously continuing until another suspension or a terminal state.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: minor
Description:
States that each Output expression is evaluated against the recorded payload as root and that mapped values are merged into the machine context without losing completed predecessors' outputs.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: minor
Description:
States that repeating the same event for an already-satisfied activation returns the reloaded machine without repeating continuation and that a delayed duplicate in a loop must not consume a newer activation of the same Wait state.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: minor
Description:
States that signal raises EngineExecutionException with ParameterRequired or InvalidParameter for null or blank required arguments, ObjectNotExists for a nonexistent machine ID, and OperationDenied for an event mismatch or an activation lost to timeout or compensation.
````

## Criterion 11

````text
ID: criteria_10
Category: Goal fidelity
Weight: major
Description:
Specifies `int fireDueTimeouts(java.time.Instant now)` on `StateMachineEngine` as claiming persisted waits whose configured deadline is at or before now, persisting each winner as SK, continuing along TimeoutNext, and returning the number of claims won.
````

## Criterion 12

````text
ID: criteria_11
Category: Goal fidelity
Weight: minor
Description:
States that indefinite and not-yet-due waits stay suspended after a fireDueTimeouts sweep and that fireDueTimeouts must work after engine reconstruction.
````

## Criterion 13

````text
ID: criteria_12
Category: Goal fidelity
Weight: minor
Description:
States that a null `now` passed to fireDueTimeouts raises EngineExecutionException with InvalidParameter.
````

## Criterion 14

````text
ID: criteria_13
Category: Goal fidelity
Weight: major
Description:
States that entering a Wait persists the WAIT state instance with status WA, suspends the machine with status WA and `isRunning=false`, and returns without executing Next, without setting the machine completion time, and without reporting completion to TC.
````

## Criterion 15

````text
ID: criteria_14
Category: Goal fidelity
Weight: minor
Description:
States that a fresh engine using the same DB must reload and resume the suspended workflow.
````

## Criterion 16

````text
ID: criteria_15
Category: Goal fidelity
Weight: minor
Description:
States that signal delivery, timeout sweeps, and compensation must produce a single winner per activation including under concurrent duplicate signals.
````

## Criterion 17

````text
ID: criteria_16
Category: Goal fidelity
Weight: major
Description:
States that a waiting child suspends its enclosing SubStateMachine state and parent machine with WA and that completing or timing out the child synchronously resumes the parent through multiple nesting levels with each level's output mappings applied.
````

## Criterion 18

````text
ID: criteria_17
Category: Goal fidelity
Weight: minor
Description:
States that compensating an ancestor cancels active descendant waits including waits in grandchildren before any completed predecessor is compensated.
````

## Criterion 19

````text
ID: criteria_18
Category: Goal fidelity
Weight: minor
Description:
States that the deprecated io.seata `StateType` and `ExecutionStatus` wrappers need matching WAIT and WA constants preserving wrap and unwrap round trips for every value.
````

## Criterion 20

````text
ID: criteria_19
Category: Goal fidelity
Weight: minor
Description:
Records that evaluation is likely to run via hidden tests.
````

## Criterion 21

````text
ID: criteria_20
Category: Artifact preservation
Weight: minor
Description:
Names /workspace/repo as apache/incubator-seata at HEAD 2efc2aab1.
````

## Criterion 22

````text
ID: criteria_21
Category: Artifact preservation
Weight: minor
Description:
Lists the saga modules as seata-saga-annotation, seata-saga-engine, seata-saga-engine-store, seata-saga-processctrl, seata-saga-rm, seata-saga-spring, seata-saga-statelang, and seata-saga-statemachine-designer.
````

## Criterion 23

````text
ID: criteria_22
Category: Artifact preservation
Weight: minor
Description:
Lists the seata-saga-statelang packages as domain, domain/impl, parser, parser/impl, parser/utils, validator, and validator/impl.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
Names `StateParserFactory` as the mapping from state-type string to parser implementation that needs WaitStateParser registration.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
Names `StateMachineProcessHandler` as the mapping from state type to handler that needs a Wait handler.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
Names `StateMachineProcessRouter` as routing through EndStateRouter plus TaskStateRouter.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
Names the `StateLogStore` interface in seata-saga-engine-store and `StateLogStoreSqls` as the persistence interface and SQLs to extend for WA status and wait deadline claims.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
Names `DbAndReportTcStateLogStore` and `DbStateMachineConfig` in seata-saga-spring as the DB persistence and engine reconstruction reload path.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
Names `BaseState` and `AbstractTaskState` in domain/impl as the implementation patterns for the new `WaitStateImpl`.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
Lists the `AbstractTaskState` fields as compensateState, isForCompensation, isForUpdate, retry, catches, input, output, status, inputExpressions, and outputExpressions.
````

## Criterion 31

````text
ID: criteria_30
Category: Artifact preservation
Weight: minor
Description:
Lists the current `ExecutionStatus` values as RU, SU, FA, UN, and SK with `getStatusString()` and `StateType` as a similar string-based enum.
````

## Criterion 32

````text
ID: criteria_31
Category: Artifact preservation
Weight: minor
Description:
Names `EngineUtils`, `ServiceTaskHandlerInterceptor`, `ParameterUtils`, `CompensationHolder`, and `LoopTaskUtils` as the engine utilities for state instance creation, output param evaluation and merge, and loop handling.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: minor
Description:
Names `SubStateMachineHandler.java`, `SucceedEndStateHandler.java`, `ServiceTaskStateHandler.java`, and `CompensationTriggerStateHandler.java` as the nesting, completion, and compensation integration points.
````

## Criterion 34

````text
ID: criteria_33
Category: Artifact preservation
Weight: minor
Description:
Names the compatible module wrappers io/seata `StateType.java`, `ExecutionStatus.java`, `StateMachineEngine.java`, `ProcessCtrlStateMachineEngine.java`, and `StateLogStoreImpl.java` as needing WAIT and WA plus new API passthrough.
````

## Criterion 35

````text
ID: criteria_34
Category: Artifact preservation
Weight: minor
Description:
Names the org.apache.seata.saga.proctrl package with ProcessContext, HierarchicalProcessContext, ProcessController, and eventing as the process control primitives used by the engine.
````

## Criterion 36

````text
ID: criteria_35
Category: Artifact preservation
Weight: minor
Description:
Names `DomainConstants.java` as carrying the shared context-variable, operation, and sequence constants.
````

## Criterion 37

````text
ID: criteria_36
Category: Decision rationale
Weight: major
Description:
Records that grep over /workspace/repo/saga and /workspace/repo/compatible found no existing Wait, signal, or fireDueTimeouts code apart from a false positive in compatible LockAndCallback.java, so the feature is implemented from scratch.
````

## Criterion 38

````text
ID: criteria_37
Category: Decision rationale
Weight: minor
Description:
Records the choice of bash find and grep for file searches because the glob tool fails with `ripgrep execution failed`.
````

## Criterion 39

````text
ID: criteria_38
Category: Decision rationale
Weight: major
Description:
Specifies the implementation order as statelang domain first, then parser and validator, then engine handler and router with suspension persistence, then signal and fireDueTimeouts, then SubStateMachine nesting and compensation, then compatible wrappers, then DB store serialization, and then unit tests and mvn build of the touched modules.
````

## Criterion 40

````text
ID: criteria_39
Category: Temporal coherence
Weight: major
Description:
Records that the tool truncated the reads of StateType.java, ExecutionStatus.java, State.java, StateInstance.java, StateMachineInstance.java, StateMachineEngine.java, ProcessCtrlStateMachineEngine.java, StateMachineProcessHandler.java, StateMachineProcessRouter.java, TaskStateRouter.java, SubStateMachineHandler.java, EngineUtils.java, ServiceTaskHandlerInterceptor.java, BaseState.java, StateParserFactory.java, ScriptTaskStateParser.java, ScriptTaskStateImpl.java, and AbstractTaskState.java so their full content is still needed.
````

## Criterion 41

````text
ID: criteria_40
Category: Temporal coherence
Weight: major
Description:
Records that the exploration phase is still in progress and that no implementation has started.
````

## Criterion 42

````text
ID: criteria_41
Category: Temporal coherence
Weight: minor
Description:
Records a todo list spanning domain, parser, engine handler and router, persistence and suspend/resume, signal, fireDueTimeouts, SubStateMachine nesting, compatible wrappers, DB schema and serialization, tests, and build and lint.
````

## Criterion 43

````text
ID: criteria_42
Category: Temporal coherence
Weight: minor
Description:
Records that DomainConstants.java, StateLogStore.java, StateMachineParserImpl.java, StateParser.java, BaseStateParser.java, AbstractTaskStateParser.java, StateMachineUtils.java, and the validator package were read in full.
````

## Criterion 44

````text
ID: criteria_43
Category: Temporal coherence
Weight: major
Description:
Lists the not-yet-read files as StateInstruction.java, SucceedEndStateHandler.java, EndStateRouter.java, LoopStartStateHandler.java, StateMachineParserFactory.java, DbAndReportTcStateLogStore.java, StateLogStoreSqls.java, DbStateMachineConfig.java, AbstractStateMachineConfig.java, ParameterUtils.java, CompensationHolder.java, and the compatible io/seata StateType.java and ExecutionStatus.java.
````

## Criterion 45

````text
ID: criteria_44
Category: Structural clarity
Weight: minor
Description:
Organizes the summary so that the completed exploration, the active work, and the next steps can each be located without reading the entire text.
````

## Criterion 46

````text
ID: criteria_45
Category: Compression efficiency
Weight: minor
Description:
Contains at most 14700 characters.
````

## Criterion 47

````text
ID: criteria_46
Category: Goal fidelity
Weight: negative
Description:
States that the `WaitState` interface extends `AbstractTaskState`.
````

## Criterion 48

````text
ID: criteria_47
Category: Goal fidelity
Weight: negative
Description:
Presents the deprecated io.seata compatible wrappers as out of scope for the task.
````

## Criterion 49

````text
ID: criteria_48
Category: Temporal coherence
Weight: negative
Description:
States that the full contents of StateMachineEngine.java and ProcessCtrlStateMachineEngine.java have already been read.
````

## Criterion 50

````text
ID: criteria_49
Category: Artifact preservation
Weight: negative
Description:
States that the `StateLogStore` interface lives in the seata-saga-engine module.
````
