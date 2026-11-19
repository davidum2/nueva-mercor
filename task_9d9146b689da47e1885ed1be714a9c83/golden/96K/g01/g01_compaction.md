## Objective
- Implement per-request conditional branch execution (dynamic routing) in the Paddle Serving Python Pipeline DAG engine.

## Important Details
- User operators inherit new methods added to `pipeline.operator.Op`.
- `RequestOp` inherits new methods added to `pipeline.operator.Op`.
- Extend `pipeline.operator.Op` with `route(self, output_data, data_id=0, log_id=0)`.
- `route` is a user-overridable hook.
- `route` is invoked at most once per request.
- `route` receives that request's `data_id`.
- For standard `Op`s, `route` runs immediately after successful `postprocess`.
- For standard `Op`s, `route` receives the emitted dict in `output_data`.
- For `RequestOp`, `route` runs on the DAG entry path.
- For `RequestOp`, `route` receives `unpack_request_package`'s output dict in `output_data`.
- Default `route` returns `None` to activate all successors.
- Returning an iterable of successor names from `route` activates only those named successors.
- `route` return handling must tolerate single-use iterables such as generators.
- Returning an empty iterable from `route` activates no successors.
- If any name returned by `route` is not in `self.get_succ_op_names()` (even alongside valid names), that request must fail with `err_no` set to `ChannelDataErrcode.INPUT_PARAMS_ERROR.value`.
- A request failing due to an invalid successor name returned by `route` must still deliver a response promptly.
- An invalid successor name returned by `route` must leave later requests unaffected.
- Extend `pipeline.operator.Op` with `on_skipped(self, data_id=0, log_id=0)`.
- The default implementation of `on_skipped` is a no-op returning `None`.
- `on_skipped` must be invoked exactly once for each request where the `Op` is skipped.
- `on_skipped` receives the skipped request's `data_id`.
- Any exception raised inside `on_skipped` must not stall the DAG.
- Any exception raised inside `on_skipped` must not alter the request's response.
- Extend `pipeline.operator.Op` with `get_succ_op_names(self)`.
- `get_succ_op_names(self)` returns a `set` of `str` naming the `Op`'s immediate successors in the established DAG topology.
- For the final output `Op`, `get_succ_op_names(self)` includes the `@DAGExecutor` sink.
- `get_succ_op_names(self)` must return an empty `set` before the DAG topology is established.
- Extend `pipeline.operator.Op` with `get_pred_op_names(self)`.
- `get_pred_op_names(self)` returns a `set` of `str` naming the upstream producer `Op`s in the established DAG topology.
- `get_pred_op_names(self)` must return an empty `set` before the DAG topology is known.
- `RequestOp` is never reported as a predecessor by `get_pred_op_names(self)`.
- An `Op` fed only by `RequestOp` returns an empty `set` from `get_pred_op_names(self)`.
- Add net-new member `SKIPPED = 3004` to `pipeline.error_catch.CustomExceptionCode`.
- `pipeline.error_catch.CustomExceptionCode` is re-exported as `pipeline.channel.ChannelDataErrcode`.
- An `Op` executes for a request iff at least one incoming edge is active.
- An `Op` is skipped for a request when no incoming edge is active.
- A skipped `Op` does not run `preprocess` for that request.
- A skipped `Op` does not run `process` for that request.
- A skipped `Op` does not run `postprocess` for that request.
- A skipped `Op` does not run `route` for that request.
- A skipped `Op` fires `on_skipped` exactly once for that request.
- A skipped `Op` propagates the skip downstream by deactivating all outgoing edges.
- An executing join `Op` receives in the `input_dicts` argument to `preprocess` only entries from predecessors whose edge to it is active for that request.
- Partial joins omit any placeholder or sentinel entry for a skipped predecessor.
- Partial joins omit any placeholder or sentinel entry for a predecessor that did not select the join in its `route`.
- Skipping must not block other `Op`s reading the same upstream output.
- Skipping must not hold back a join whose remaining predecessors ran.
- Skipping must not leave a request unanswered.
- Concurrent requests must be routed individually without mutual interference.
- Auto-batched requests must be routed individually without mutual interference.
- Routing must behave identically whether `Op`s run as threads or as processes (`is_thread_op`).
- When routing leaves a request with no active path to the response, `DAGExecutor.call()` must return promptly with a `Response` whose `err_no` is set to `CustomExceptionCode.SKIPPED.value`.
- Terminal skip handling applies when a single `route` call cuts the last active path to the response.
- Terminal skip handling applies when combined `route` decisions across multiple `Op`s leave no active path to the response.
- Terminal skip handling applies when the final output `Op` returns an iterable omitting `@DAGExecutor`.
- Operator execution errors take precedence over routing.
- Operator execution errors propagate along all outgoing edges of the failing `Op`.
- Downstream `Op`s do not execute for requests carrying an upstream execution error.
- Downstream `Op`s forward upstream execution errors along all of their own outgoing edges.
- `route` must not be consulted for requests that already failed.
- `route` must not be consulted for requests rejected by `unpack_request_package` with a product error code.
- `get_succ_op_names()` must be populated as soon as `PipelineServer.set_response_op()` returns.
- `get_pred_op_names()` must be populated as soon as `PipelineServer.set_response_op()` returns.
- Populating `get_succ_op_names()` must not require constructing or starting a `DAGExecutor`.
- Populating `get_pred_op_names()` must not require constructing or starting a `DAGExecutor`.
- When all `Op`s use the default `route` returning `None`, the DAG must behave identically to before.
- `Op`s constructed with `jump_to_ops` retain their existing behavior because `route` does not need to be supported for them.
- The once-per-request guarantees for `route` apply to a single DAG pass.
- The once-per-request guarantees for `on_skipped` apply to a single DAG pass.
- When the executor replays a request (`dag.retry` greater than 1), the routing hooks may run again for the replay.
- The working directory `/app` is a symlink pointing to `/workspace/repo`.
- `/app/pipeline` does not exist.
- The `pipeline` package resides at `/workspace/repo/python/pipeline`.
- The `pipeline` package is accessible at `/app/python/pipeline` through the `/app` symlink.
- `/workspace/repo/sitecustomize.py` does not exist.
- `sitecustomize.py` resides at `/workspace/repo/python/sitecustomize.py`.
- The agent reasoned (not yet verified by running Python) that running from `/app` with `PYTHONPATH=python` resolves to `/workspace/repo/python` via the `/app` symlink.
- The agent reasoned (not yet verified by running Python) that placing `/workspace/repo/python` on `sys.path` allows Python to auto-import `sitecustomize` at startup.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.Iterable` to `collections.abc.Iterable`.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.Mapping` to `collections.abc.Mapping`.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.MutableMapping` to `collections.abc.MutableMapping`.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.Sequence` to `collections.abc.Sequence`.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.MutableSequence` to `collections.abc.MutableSequence`.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.Container` to `collections.abc.Container`.
- `/workspace/repo/python/sitecustomize.py` aliases `collections.Callable` to `collections.abc.Callable`.
- `/workspace/repo/python/sitecustomize.py` appends existing `pipeline/proto` subdirectories found under `sys.path` entries to `sys.path`.
- `/workspace/repo/python/sitecustomize.py` appends existing `paddle_serving_client/proto` subdirectories found under `sys.path` entries to `sys.path`.
- `/workspace/repo/python/sitecustomize.py` appends existing `paddle_serving_server/proto` subdirectories found under `sys.path` entries to `sys.path`.
- `/workspace/repo/python/pipeline/channel.py` is 941 lines long.
- `/workspace/repo/python/pipeline/operator.py` is 2039 lines long.
- `/workspace/repo/python/pipeline/dag.py` is 948 lines long.
- `/workspace/repo/python/pipeline/error_catch.py` is 243 lines long.
- `/workspace/repo/python/pipeline/pipeline_server.py` is 570 lines long.
- `/workspace/repo/python/pipeline/__init__.py` is 19 lines long.
- `/workspace/repo/python/pipeline/proto/` contains `pipeline_service.proto`.
- `/workspace/repo/python/pipeline/proto/` contains `pipeline_service_pb2.py`.
- `/workspace/repo/python/pipeline/proto/` contains `pipeline_service_pb2_grpc.py`.
- `/workspace/repo/python/pipeline/` also contains `local_service_handler.py`.
- `/workspace/repo/python/pipeline/` also contains `profiler.py`.
- `/workspace/repo/python/pipeline/` also contains `logger.py`.
- `/workspace/repo/python/pipeline/` also contains `pipeline_client.py`.
- `/workspace/repo/python/pipeline/` also contains `analyse.py`.
- `/workspace/repo/python/pipeline/` also contains `prometheus_metrics.py`.
- `/workspace/repo/python/pipeline/` also contains the `gateway/` subdirectory.
- Git HEAD is `b0af55d0`.
- The repository working tree is clean with no uncommitted modifications.
- `/workspace/repo/python/pipeline/operator.py` imports `ErrorCatch` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` imports `CustomException` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` imports `CustomExceptionCode` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` imports `CustomExceptionCode` as `ChannelDataErrcode` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` imports `ProductErrCode` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` imports `ParamChecker` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` imports `ParamVerify` from `.error_catch`.
- `/workspace/repo/python/pipeline/operator.py` aliases `check_feed_dict = ParamVerify.check_feed_dict`.
- `/workspace/repo/python/pipeline/operator.py` aliases `check_fetch_list = ParamVerify.check_fetch_list`.
- `/workspace/repo/python/pipeline/operator.py` imports `pipeline_service_pb2` from `.proto`.
- `/workspace/repo/python/pipeline/operator.py` imports `ThreadChannel` from `.channel`.
- `/workspace/repo/python/pipeline/operator.py` imports `ProcessChannel` from `.channel`.
- `/workspace/repo/python/pipeline/operator.py` imports `ChannelData` from `.channel`.
- `/workspace/repo/python/pipeline/operator.py` imports `ChannelDataType` from `.channel`.
- `/workspace/repo/python/pipeline/operator.py` imports `ChannelStopError` from `.channel`.
- `/workspace/repo/python/pipeline/operator.py` imports `ChannelTimeoutError` from `.channel`.
- `/workspace/repo/python/pipeline/operator.py` imports `NameGenerator` from `.util`.
- `/workspace/repo/python/pipeline/operator.py` imports `UnsafeTimeProfiler` as `TimeProfiler` from `.profiler`.
- `/workspace/repo/python/pipeline/operator.py` imports `local_service_handler` from `.`.
- `/workspace/repo/python/pipeline/operator.py` imports `Client` from `paddle_serving_client`.
- `/workspace/repo/python/pipeline/operator.py` imports `func_timeout`.
- `/workspace/repo/python/pipeline/operator.py` imports `queue` as `Queue` on Python 3.
- Because the initial read of `/workspace/repo/python/pipeline/operator.py` truncated early in the imports on the 2039-line file, the agent switched to offset-based reading to inspect later code.
- In `/workspace/repo/python/pipeline/operator.py`, the postprocess packaging tail builds `ChannelData` with `ChannelDataType.CHANNEL_NPDATA.value` (`npdata=postped_data`) for NumPy outputs.
- In `/workspace/repo/python/pipeline/operator.py`, the postprocess packaging tail builds `ChannelData` with `ChannelDataType.DICT.value` (`dictdata=postped_data`) for dict outputs.
- In `/workspace/repo/python/pipeline/operator.py`, each packaged postprocess `ChannelData` carries `data_id`.
- In `/workspace/repo/python/pipeline/operator.py`, each packaged postprocess `ChannelData` carries `log_id`.
- In `/workspace/repo/python/pipeline/operator.py`, packaged postprocess outputs are stored in `postped_data_dict[data_id]`.
- In `/workspace/repo/python/pipeline/operator.py`, the postprocess packaging helper returns `(postped_data_dict, err_channeldata_dict)`.
- `/workspace/repo/python/pipeline/operator.py` defines `_auto_batching_generator(self, input_channel, op_name, batch_size, timeout, op_info_prefix)` to merge up to `batch_size` requests for one prediction.
- In `_auto_batching_generator`, when `timeout` is not `None`, `endtime` is computed as `_time() + timeout`.
- The `_auto_batching_generator` docstring states that blocking occurs when `timeout` is `None` and fewer than `batch_size` items arrive.
- `/workspace/repo/python/pipeline/channel.py` imports `ErrorCatch` from `.error_catch`.
- `/workspace/repo/python/pipeline/channel.py` imports `CustomException` from `.error_catch`.
- `/workspace/repo/python/pipeline/channel.py` imports `ProductErrCode` from `.error_catch`.
- `/workspace/repo/python/pipeline/channel.py` imports `CustomExceptionCode` as `ChannelDataErrcode` from `.error_catch`.
- `/workspace/repo/python/pipeline/channel.py` defines `ChannelDataType` as an `enum.Enum`.
- `/workspace/repo/python/pipeline/channel.py` defines `ChannelDataType.DICT = 0`.
- `/workspace/repo/python/pipeline/channel.py` defines `ChannelDataType.CHANNEL_NPDATA = 1`.
- `/workspace/repo/python/pipeline/channel.py` defines `ChannelDataType.ERROR = 2`.
- `/workspace/repo/python/pipeline/channel.py` defines `ChannelData` with `def __init__(self, datatype=None, npdata=None, dictdata=None, data_id=None, log_id=None, error_code=None, error_info=None, prod_error_code=None, prod_error_info=None, client_need_profile=...)`.

## Work State
### Completed
- Listed `/app` directory.
- Listed `/app/python` directory.
- Listed `/workspace/repo` root directory.
- Listed files under `/workspace/repo/python/pipeline/`.
- Checked line counts of the core modules under `/workspace/repo/python/pipeline/`.
- Read `/workspace/repo/python/sitecustomize.py` in full.
- Checked `git log` showing HEAD commit `b0af55d0`.
- Checked `git status` showing a clean working tree.
- Read the top imports of `/workspace/repo/python/pipeline/operator.py`.
- Offset-read `/workspace/repo/python/pipeline/operator.py` from the postprocess packaging tail through the start of `_auto_batching_generator`.
- Partially read `/workspace/repo/python/pipeline/channel.py` through the `ChannelData` `__init__` parameter list.

### Active
- Continuing source inspection of the core `pipeline` modules before designing the per-request routing implementation.
- No code changes have been made to the repository yet.
- `/workspace/repo/python/pipeline/dag.py` has not been read yet.
- `/workspace/repo/python/pipeline/error_catch.py` has not been read yet.
- `/workspace/repo/python/pipeline/pipeline_server.py` has not been read yet.
- `/workspace/repo/python/pipeline/__init__.py` has not been read yet.

### Blocked
- The `glob` tool failed with `ripgrep execution failed`.
- Repository file discovery uses `bash` `find` because `glob` fails with `ripgrep execution failed`.

## Next Move
1. Finish reading the remainder of `/workspace/repo/python/pipeline/channel.py` beyond the `ChannelData` `__init__` header.
2. Read `/workspace/repo/python/pipeline/dag.py`.
3. Read `/workspace/repo/python/pipeline/error_catch.py`.
4. Read `/workspace/repo/python/pipeline/pipeline_server.py`.
5. Read `/workspace/repo/python/pipeline/__init__.py`.
6. Read the remaining unread body of `/workspace/repo/python/pipeline/operator.py` using offset reads.
7. Design the per-request conditional routing mechanism across the `pipeline` modules.
8. Implement the conditional DAG routing changes.
9. Verify the implementation by running Python from `/app` with `PYTHONPATH=python`.

## Relevant Files
- `/workspace/repo/python/pipeline/operator.py`: module containing `Op`.
- `/workspace/repo/python/pipeline/channel.py`: module defining `ChannelData`.
- `/workspace/repo/python/pipeline/dag.py`: module for `DAGExecutor.call()` inspection.
- `/workspace/repo/python/pipeline/error_catch.py`: module defining `CustomExceptionCode`.
- `/workspace/repo/python/pipeline/pipeline_server.py`: module for `PipelineServer.set_response_op()` inspection.
- `/workspace/repo/python/pipeline/__init__.py`: package initialization module.
- `/workspace/repo/python/sitecustomize.py`: Python 3.11 compatibility shims.
