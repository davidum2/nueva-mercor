# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the objective of adding a durable `Wait` state to Seata Saga with external-event approval, durable suspension, and resume across engine restarts, spanning the statelang domain and parser, the engine, the store, and the compatible layers.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
Specifies a `signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String,Object> payload)` method on `StateMachineEngine`.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
Specifies an `int fireDueTimeouts(java.time.Instant now)` method on `StateMachineEngine`.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that the work is correct when every item of the requirement spec is implemented and the planned unit tests, Maven builds, and lint checks pass.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: minor
Description:
States that `StateType.WAIT` carries the value "Wait" with case-insensitive lookup preserved and `ExecutionStatus.WA` carries the value "Waiting".
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
Lists the `WaitState` accessors and their optionality, namely `getEvent()` required and non-blank, `getOutput()` an optional `Map<String,Object>`, `getTimeout()` an optional `java.time.Duration`, and `getTimeoutNext()` optional.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: minor
Description:
States that a `Wait` definition where only one of Timeout and TimeoutNext is present is rejected, that Timeout must be strictly positive ISO-8601, and that Event must be non-blank.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: minor
Description:
States that `StateMachineUtils.getAllPossibleSubsequentStates` must return a Wait state's Next plus its optional TimeoutNext.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: major
Description:
States the Wait entry behavior of persisting the WAIT state instance with status WA, persisting the machine with status WA and `isRunning=false`, returning without executing Next, leaving the machine completion time unset, and skipping TC completion reporting.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: minor
Description:
States that a fresh engine on the same DB must reload a suspended workflow and resume it.
````

## Criterion 11

````text
ID: criteria_10
Category: Goal fidelity
Weight: major
Description:
States the signal winner semantics of persisting the winner SU with the payload as output params, mapping a null payload to an empty map, and continuing synchronously to the next suspension or terminal state.
````

## Criterion 12

````text
ID: criteria_11
Category: Goal fidelity
Weight: minor
Description:
States the signal error mapping of `EngineExecutionException` carrying `ParameterRequired` or `InvalidParameter` for null or blank required args, `ObjectNotExists` for a nonexistent machine, and `OperationDenied` for an event mismatch or an activation lost to timeout or compensation.
````

## Criterion 13

````text
ID: criteria_12
Category: Goal fidelity
Weight: minor
Description:
States that replaying a satisfied activation returns the reloaded machine without re-running the continuation and that a delayed duplicate for an older loop activation must not consume a newer activation of the same Wait state.
````

## Criterion 14

````text
ID: criteria_13
Category: Goal fidelity
Weight: minor
Description:
States that Output expressions are evaluated with the recorded payload as root and that mapped outputs are merged into the machine context preserving completed predecessors' outputs.
````

## Criterion 15

````text
ID: criteria_14
Category: Goal fidelity
Weight: major
Description:
States the `fireDueTimeouts` semantics of claiming persisted waits with deadline <= now, persisting the winner SK, resuming along TimeoutNext, and returning the number of claims won.
````

## Criterion 16

````text
ID: criteria_15
Category: Goal fidelity
Weight: minor
Description:
States that indefinite waits and not-yet-due waits stay suspended and that a reconstructed engine discovers and resumes due waits.
````

## Criterion 17

````text
ID: criteria_16
Category: Goal fidelity
Weight: minor
Description:
States that a null `now` passed to `fireDueTimeouts` raises `EngineExecutionException` carrying `InvalidParameter`.
````

## Criterion 18

````text
ID: criteria_17
Category: Goal fidelity
Weight: minor
Description:
States the concurrency requirement of a single winner via atomic claim across duplicate matching signals, signal versus due timeout, signal versus compensation, and timeout versus compensation.
````

## Criterion 19

````text
ID: criteria_18
Category: Goal fidelity
Weight: major
Description:
States the nesting rule that a waiting child suspends the enclosing `SubStateMachine` state in WA and its parent machine in WA and that completing or timing out a child synchronously resumes parents through multiple nesting levels applying each level's output mappings.
````

## Criterion 20

````text
ID: criteria_19
Category: Goal fidelity
Weight: minor
Description:
States that ancestor compensation cancels active descendant waits including grandchildren and that cancellation precedes compensation of any completed predecessor.
````

## Criterion 21

````text
ID: criteria_20
Category: Goal fidelity
Weight: minor
Description:
States that the compatible wrappers under `io.seata.saga.statelang.domain` add WAIT to the deprecated `StateType` and WA to the deprecated `ExecutionStatus` while preserving wrap and unwrap round trips for every value.
````

## Criterion 22

````text
ID: criteria_21
Category: Decision rationale
Weight: major
Description:
Explains that `state_machine_inst` and `state_inst` use the `${TABLE_PREFIX}` prefix and both expose a `status` column, so no schema change is needed and the timeout deadline is derived from persisted `gmt_started` plus the configured `Timeout` instead of adding a column.
````

## Criterion 23

````text
ID: criteria_22
Category: Decision rationale
Weight: minor
Description:
Explains the suspension design in which `WaitStateHandler.process` performs all persistence and then sets `instruction.setEnd(true)`, so `TaskStateRouter.route` returns null and `EngineUtils.endStateMachine` is bypassed with no gmtEnd and no TC report.
````

## Criterion 24

````text
ID: criteria_23
Category: Decision rationale
Weight: minor
Description:
Explains that `WaitStateHandler` is planned as a plain `StateHandler` with no interceptors, creating the WAIT state instance inside `process()` so it records WA rather than the RU that `ServiceTaskHandlerInterceptor.preProcess` records before handlers, and registered in `StateMachineProcessHandler`'s StateType to handler map.
````

## Criterion 25

````text
ID: criteria_24
Category: Decision rationale
Weight: minor
Description:
Explains that a state-level query for waits is preferred over a machine-status query because it finds waits globally, including waits in child machines.
````

## Criterion 26

````text
ID: criteria_25
Category: Decision rationale
Weight: minor
Description:
Explains that `ServiceTaskHandlerInterceptor.postProcess` early-returns when the state instance is null or `!stateMachineInstance.isRunning()`, so the interceptor is skipped once the machine is suspended.
````

## Criterion 27

````text
ID: criteria_26
Category: Decision rationale
Weight: minor
Description:
Explains that `parentId` combines the parent machine instance id, `SEPERATOR_PARENT_ID`, and the parent state instance id via `EngineUtils.generateParentId`, enabling exact parent `SUB_STATE_MACHINE` activation lookup on child resume.
````

## Criterion 28

````text
ID: criteria_27
Category: Decision rationale
Weight: minor
Description:
Explains that compensating a suspended, never-compensated machine is allowed because `compensateInternal` only calls `checkStatus` when `compensationStatus` is not null.
````

## Criterion 29

````text
ID: criteria_28
Category: Decision rationale
Weight: minor
Description:
Explains that `SubStateMachineHandler` must be modified so that when the child engine start returns a WA instance, the parent state instance is set to WA, the suspension is persisted, end is set, and the parent returns without routing to Next.
````

## Criterion 30

````text
ID: criteria_29
Category: Decision rationale
Weight: minor
Description:
Explains that `reloadStateMachineInstance` with `replayContextVariables` replays each state's Output via `ParameterUtils.createOutputParams(resolver, state, output)` and that the cast to `ServiceTaskStateImpl` needs handling for Wait.
````

## Criterion 31

````text
ID: criteria_30
Category: Decision rationale
Weight: minor
Description:
Specifies the parent resume design of parsing `parentId`, reloading the parent, finding its WA `SUB_STATE_MACHINE` state instance by id, setting the status from the child's final status, and continuing the parent from the sub-state Next with replayed parent variables.
````

## Criterion 32

````text
ID: criteria_31
Category: Decision rationale
Weight: minor
Description:
Specifies the descendant wait cancellation design of a recursive walk that CAS-claims WA Wait states to SK and recurses into child machines for WA `SUB_STATE_MACHINE` states via `queryStateMachineInstanceByParentId`, hooked before compensation stack processing in `CompensationTriggerStateHandler`.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: minor
Description:
States that new claim, suspend, resume, and query methods must be added to `StateLogStore.java`, `StateLogStoreSqls.java`, and `DbAndReportTcStateLogStore.java`.
````

## Criterion 34

````text
ID: criteria_33
Category: Artifact preservation
Weight: minor
Description:
States the planned claim mechanism as a CAS update on `${TABLE_PREFIX}state_inst` that sets status, `output_params`, and `gmt_updated` where the row still holds status WA, with one updated row meaning a win.
````

## Criterion 35

````text
ID: criteria_34
Category: Artifact preservation
Weight: minor
Description:
States that machine resume persists `status='RU'` and `is_running=true`.
````

## Criterion 36

````text
ID: criteria_35
Category: Artifact preservation
Weight: minor
Description:
Names `WaitState.java`, `WaitStateImpl.java`, and `WaitStateParser.java` as new files to create in the statelang modules, with `WaitStateParser` registered for `Wait` in `StateParserFactory`.
````

## Criterion 37

````text
ID: criteria_36
Category: Artifact preservation
Weight: minor
Description:
States that the state instance row mapper reads type via `StateType.getStateType(...)` with case-insensitive lookup and status via `ExecutionStatus.valueOf(...)`, so new query SQL must match the insert encoding.
````

## Criterion 38

````text
ID: criteria_37
Category: Artifact preservation
Weight: minor
Description:
States that a search of `saga` and `compatible` matched only `compatible/src/test/java/io/seata/common/LockAndCallback.java`, so no Wait-related files exist in main sources.
````

## Criterion 39

````text
ID: criteria_38
Category: Artifact preservation
Weight: minor
Description:
States the planned `DomainConstants` addition of `OPERATION_NAME_SIGNAL` with value "signal" for continuation contexts.
````

## Criterion 40

````text
ID: criteria_39
Category: Temporal coherence
Weight: major
Description:
Records that zero source edits have been made, that the exploration todo remains in progress, and that implementation, the planned unit tests, the Maven builds, and the lint checks remain pending.
````

## Criterion 41

````text
ID: criteria_40
Category: Temporal coherence
Weight: major
Description:
Records that the `glob` tool fails with `ripgrep execution failed` on every attempt and that `bash ls` and `find` are the workaround in use.
````

## Criterion 42

````text
ID: criteria_41
Category: Temporal coherence
Weight: major
Description:
Lists the next steps of finishing the remaining file reads, implementing the statelang, store, and engine changes, adding unit tests for durable Wait behavior, and running the Maven builds and lint checks.
````

## Criterion 43

````text
ID: criteria_42
Category: Temporal coherence
Weight: minor
Description:
Records that the middle sections of `DbAndReportTcStateLogStore.java` remain unread while the state instance row mapper and the opening of the file have been read.
````

## Criterion 44

````text
ID: criteria_43
Category: Temporal coherence
Weight: minor
Description:
Records that `ExecutionStatus.java` and `SucceedEndStateHandler.java` have been read in full while `StateType.java` has been read only up to `LOOP_START`.
````

## Criterion 45

````text
ID: criteria_44
Category: Temporal coherence
Weight: minor
Description:
Records that it remains to be verified whether `recordStateMachineRestarted` sets `status` in addition to `is_running` and `gmt_updated`.
````

## Criterion 46

````text
ID: criteria_45
Category: Structural clarity
Weight: minor
Description:
Organizes the content so that the pending implementation steps are distinguishable from the completed exploration work without reading the entire text.
````

## Criterion 47

````text
ID: criteria_46
Category: Compression efficiency
Weight: minor
Description:
Contains at most 20800 characters.
````

## Criterion 48

````text
ID: criteria_47
Category: Artifact preservation
Weight: negative
Description:
States that implementing Wait requires a schema change adding a deadline column to `state_inst`.
````

## Criterion 49

````text
ID: criteria_48
Category: Goal fidelity
Weight: negative
Description:
States that a timed-out Wait resumes along the state's Next rather than its TimeoutNext.
````

## Criterion 50

````text
ID: criteria_49
Category: Decision rationale
Weight: negative
Description:
States that the choice between a dedicated `WaitStateRouter` and reusing `TaskStateRouter` has been settled in favor of a dedicated `WaitStateRouter`.
````

## Criterion 51

````text
ID: criteria_50
Category: Temporal coherence
Weight: negative
Description:
States that the type and status insert encoding in `recordStateStarted` has been verified to match the new query SQL.
````
