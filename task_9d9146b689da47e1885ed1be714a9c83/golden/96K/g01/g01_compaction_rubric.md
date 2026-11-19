# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States that the goal is to implement per-request conditional branch execution, known as dynamic routing, in the Paddle Serving Python Pipeline DAG engine.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that `pipeline.operator.Op` must be extended with `route`, `on_skipped`, `get_succ_op_names`, and `get_pred_op_names`.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that `SKIPPED = 3004` must be added to `pipeline.error_catch.CustomExceptionCode` and re-exported as `pipeline.channel.ChannelDataErrcode`.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that DAG execution must honor per-request edge activation while preserving full backward compatibility.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States that an Op executes only when at least one incoming edge is active and that a skipped Op runs none of `preprocess`, `process`, `postprocess`, or `route`.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: major
Description:
States that when no active path to the response remains, `DAGExecutor.call()` must return a `Response` with `err_no = CustomExceptionCode.SKIPPED.value`.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: minor
Description:
States that a default `route` returning `None` activates all successors and that a returned empty iterable activates none.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: minor
Description:
States that `route` runs at most once per request and right after successful `postprocess` for standard Ops.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: minor
Description:
States that for `RequestOp` the `route` hook runs on the DAG entry path with the `unpack_request_package` output dict.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: minor
Description:
States that a `route` return naming a successor outside `get_succ_op_names()` fails that request with `err_no = ChannelDataErrcode.INPUT_PARAMS_ERROR.value` and leaves later requests unaffected.
````

## Criterion 11

````text
ID: criteria_10
Category: Goal fidelity
Weight: minor
Description:
States that `get_succ_op_names()` returns the set of immediate successor names in the established topology, including the `@DAGExecutor` sink for the final output Op.
````

## Criterion 12

````text
ID: criteria_11
Category: Goal fidelity
Weight: minor
Description:
States that `get_pred_op_names()` returns the set of upstream producer names and that `RequestOp` is never reported as a predecessor.
````

## Criterion 13

````text
ID: criteria_12
Category: Goal fidelity
Weight: minor
Description:
States that `on_skipped` fires exactly once per skipped request and that exceptions inside it must not stall the DAG or change the response.
````

## Criterion 14

````text
ID: criteria_13
Category: Goal fidelity
Weight: minor
Description:
States that a skipped Op deactivates all of its outgoing edges so that the skip propagates transitively.
````

## Criterion 15

````text
ID: criteria_14
Category: Goal fidelity
Weight: minor
Description:
States that an executing join Op receives in its `preprocess` `input_dicts` only entries from predecessors whose edge to it is active and that no placeholder is inserted for skipped predecessors.
````

## Criterion 16

````text
ID: criteria_15
Category: Goal fidelity
Weight: minor
Description:
States that skipping must not block other ops reading the same upstream output, hold back a join whose remaining predecessors ran, or leave the request unanswered.
````

## Criterion 17

````text
ID: criteria_16
Category: Goal fidelity
Weight: minor
Description:
States that routing is per-request so that concurrent and auto-batched requests are independent and behavior is identical for thread ops and process ops.
````

## Criterion 18

````text
ID: criteria_17
Category: Goal fidelity
Weight: minor
Description:
States that operator execution errors take precedence over routing and propagate along all outgoing edges of the failing Op while downstream ops pass the error along without running.
````

## Criterion 19

````text
ID: criteria_18
Category: Goal fidelity
Weight: minor
Description:
States that `route` is never consulted for requests that already failed, including `unpack_request_package` rejections carrying a product error code.
````

## Criterion 20

````text
ID: criteria_19
Category: Goal fidelity
Weight: minor
Description:
States that successor and predecessor name sets are populated as soon as `PipelineServer.set_response_op()` returns and before any `DAGExecutor` is constructed or started.
````

## Criterion 21

````text
ID: criteria_20
Category: Goal fidelity
Weight: negative
Description:
States that `get_succ_op_names()` returns every downstream Op name in the DAG.
````

## Criterion 22

````text
ID: criteria_21
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/pipeline/operator.py` as the file where `route`, `on_skipped`, `get_succ_op_names`, and `get_pred_op_names` are to be implemented.
````

## Criterion 23

````text
ID: criteria_22
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/pipeline/channel.py` as the file where per-request edge activation and partial joins must be enforced for both `ThreadChannel` and `ProcessChannel`.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/pipeline/dag.py` as the file handling the terminal-skip response, error propagation, and replay semantics.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/pipeline/error_catch.py` as the file where `SKIPPED = 3004` is added to `CustomExceptionCode`.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/pipeline/pipeline_server.py` as the file containing `PipelineServer.set_response_op`.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/pipeline/__init__.py` as the package re-export file for the pipeline package.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
Names `/workspace/repo/python/sitecustomize.py` as the file supplying the Python 3.11 shims that alias `collections` names to `collections.abc` and append proto directories to `sys.path`.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
Records the signature of `route` as `route(self, output_data, data_id=0, log_id=0)`.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
Records the signature of `on_skipped` as `on_skipped(self, data_id=0, log_id=0)` with a default no-op returning `None`.
````

## Criterion 31

````text
ID: criteria_30
Category: Artifact preservation
Weight: minor
Description:
Records that `operator.py` imports `CustomExceptionCode` as `ChannelDataErrcode` and imports `ThreadChannel`, `ProcessChannel`, `ChannelData`, and `ChannelDataType` from `.channel`.
````

## Criterion 32

````text
ID: criteria_31
Category: Artifact preservation
Weight: minor
Description:
Records that the working directory `/app` is a symlink to `/workspace/repo` and that Python is run from `/app` with `PYTHONPATH=python`.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: negative
Description:
States that the pipeline package is located at `/app/pipeline`.
````

## Criterion 34

````text
ID: criteria_33
Category: Decision rationale
Weight: major
Description:
Records that `bash` `find` and `grep` are used instead of the `glob` tool because `glob` fails with `ripgrep execution failed`.
````

## Criterion 35

````text
ID: criteria_34
Category: Decision rationale
Weight: major
Description:
Records the decision that `jump_to_ops` ops keep their current behavior because `route` is unsupported for them.
````

## Criterion 36

````text
ID: criteria_35
Category: Decision rationale
Weight: minor
Description:
Records that the once-per-request guarantees for `route` and `on_skipped` are scoped to a single DAG pass and that replays with `dag.retry` greater than 1 can re-run the hooks.
````

## Criterion 37

````text
ID: criteria_36
Category: Temporal coherence
Weight: minor
Description:
Records that `dag.py` and `error_catch.py` have been read in full.
````

## Criterion 38

````text
ID: criteria_37
Category: Temporal coherence
Weight: major
Description:
Records that the active work is reading the unread middle of `operator.py` and the rest of `channel.py` to map `Op`, `RequestOp`, and `VirtualOp` and the channel producer-consumer mechanics.
````

## Criterion 39

````text
ID: criteria_38
Category: Temporal coherence
Weight: major
Description:
Lists finishing the read of `channel.py`, reading `pipeline_server.py`, and reading the unread middle of `operator.py` as the remaining reading steps.
````

## Criterion 40

````text
ID: criteria_39
Category: Temporal coherence
Weight: major
Description:
Records that the planned work once the reading is done is to design and implement the per-request edge-activation bookkeeping for the routing and skipping mechanism.
````

## Criterion 41

````text
ID: criteria_40
Category: Temporal coherence
Weight: negative
Description:
States that `operator.py` has already been edited with the `route` and `on_skipped` implementations.
````

## Criterion 42

````text
ID: criteria_41
Category: Compression efficiency
Weight: minor
Description:
Contains at most 10200 characters.
````

## Criterion 43

````text
ID: criteria_42
Category: Structural clarity
Weight: minor
Description:
Organizes related facts so that the outstanding reading work, the blocked items, and the planned implementation can be located without reading the entire text.
````
