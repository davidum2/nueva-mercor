## Objective
- Implement per-request conditional branch execution (dynamic routing) in the Paddle Serving Python Pipeline DAG engine: extend `pipeline.operator.Op` with `route`, `on_skipped`, `get_succ_op_names`, `get_pred_op_names`, add `SKIPPED = 3004` to `pipeline.error_catch.CustomExceptionCode` (re-exported as `pipeline.channel.ChannelDataErrcode`), and make DAG execution honor per-request edge activation while preserving full backward compatibility.

## Important Details
- Environment: working dir `/app` (symlink → `/workspace/repo`); run Python from `/app` with `PYTHONPATH=python` (i.e. `/workspace/repo/python` on path); `sitecustomize.py` at `/workspace/repo/python/sitecustomize.py` supplies Py3.11 shims (aliases `collections.Iterable/Mapping/MutableMapping/Sequence/MutableSequence/Container/Callable` to `collections.abc.*`, and appends each sys.path entry's `pipeline/proto`, `paddle_serving_client/proto`, `paddle_serving_server/proto` dirs to sys.path).
- Repo layout fact: pipeline package is at `/workspace/repo/python/pipeline` (NOT `/app/pipeline`, which does not exist); `/app/python/pipeline` is the path via symlink.
- API spec:
  - `route(self, output_data, data_id=0, log_id=0)`: user hook, ≤ once per request; for standard `Op`s runs right after successful `postprocess` with emitted dict in `output_data`; for `RequestOp` runs on DAG entry path with `unpack_request_package` output dict. Returns `None` (default) = activate all successors; or any iterable of successor names to activate (must tolerate single-use iterables like generators; empty = activate none). Any returned name not in `self.get_succ_op_names()` (even alongside valid ones) → that request fails with `err_no = ChannelDataErrcode.INPUT_PARAMS_ERROR.value`, response delivered promptly, later requests unaffected.
  - `on_skipped(self, data_id=0, log_id=0)`: default no-op returning `None`; called exactly once per request for which the Op is skipped; exceptions inside it must not stall the DAG or change the response.
  - `get_succ_op_names()`: `set[str]` of immediate successor names in established topology (including the `@DAGExecutor` sink for the final output Op); empty `set` before topology established.
  - `get_pred_op_names()`: `set[str]` of upstream producer names; empty before topology known; `RequestOp` is never reported as predecessor (Op fed only by `RequestOp` returns empty set).
  - `CustomExceptionCode.SKIPPED = 3004` (net-new member).
- Behavioral invariants:
  - Op executes iff ≥1 incoming edge active; otherwise skipped: none of `preprocess/process/postprocess/route` run, `on_skipped` fires exactly once, and all outgoing edges are deactivated (transitive skip).
  - Partial joins: executing join Op gets in `preprocess`'s `input_dicts` only entries from predecessors whose edge to it is active; NO placeholder/sentinel for skipped predecessors or ones that didn't select it.
  - Liveness/concurrency: skipping must not block other ops reading the same upstream output, hold back a join whose remaining predecessors ran, or leave the request unanswered; routing is per-request (concurrent/auto-batched requests independent); identical behavior for thread ops and process ops (`is_thread_op`).
  - Terminal skips: if no active path to the response remains, `DAGExecutor.call()` must return promptly with a `Response` with `err_no = CustomExceptionCode.SKIPPED.value` — whether cut by one `route` or several ops combined, including final output Op returning an iterable omitting `@DAGExecutor`.
  - Error precedence: operator execution errors beat routing; propagate along ALL outgoing edges of the failing Op; every downstream Op passes the error along all its own outgoing edges without running; `route` never consulted for already-failed requests, including `unpack_request_package` rejections with a product error code.
  - Topology availability: succ/pred name sets populated as soon as `PipelineServer.set_response_op()` returns (no `DAGExecutor` constructed/started).
  - Backward compat: default `route` returning `None` → DAG behaves exactly as before.
  - Scope: `jump_to_ops` ops keep current behavior (`route` unsupported for them); once-per-request guarantees are per single DAG pass; replays (`dag.retry` > 1) may re-run the hooks.
- Import context in `operator.py`: `from .error_catch import ... CustomExceptionCode as ChannelDataErrcode`; `from .channel import (ThreadChannel, ProcessChannel, ChannelData, ChannelDataType, ChannelStopError, ChannelTimeoutError)`; also uses `func_timeout`, `NameGenerator` (`.util`), `UnsafeTimeProfiler as TimeProfiler` (`.profiler`), `.proto.pipeline_service_pb2`, `.local_service_handler`.
- `channel.py` context: `ChannelDataType` enum = `DICT=0, CHANNEL_NPDATA=1, ERROR=2`; `ChannelData.__init__(datatype, npdata, dictdata, data_id, log_id, error_code, error_info, prod_error_code, prod_error_info, client_need_profile, ...)`.
- Git HEAD: `b0af55d0 Update README.md` (clean tree at start).

## Work State
### Completed
- Located package: `/workspace/repo/python/pipeline`; confirmed `/app -> /workspace/repo` and that `/app/pipeline` does not exist.
- Read `/workspace/repo/python/sitecustomize.py` fully (shim behavior noted above).
- File sizes: `channel.py` 941 lines, `operator.py` 2039 lines, `dag.py` 948 lines, `error_catch.py` 243 lines, `pipeline_server.py` 570 lines, `__init__.py` 19 lines.
- Partially read `operator.py` (imports at top; tail from ~line 1224: postprocess output handling building `ChannelData(DICT/CHANNEL_NPDATA)` per `data_id` into `postped_data_dict` + `err_channeldata_dict`; `_auto_batching_generator` batching loop with `timeout`/`endtime`).
- Partially read `channel.py` (lines 1–58: imports, `_LOGGER`, `ChannelDataType`, start of `ChannelData`).

### Active
- Reading core sources (`operator.py`, `channel.py`, `dag.py`, `error_catch.py`, `pipeline_server.py`) to map Op/RequestOp/DAGExecutor/channel architecture and identify hook points for per-request edge activation, `route` invocation, skip propagation (`on_skipped`), error precedence, and topology recording in `set_response_op`.

### Blocked
- `glob` tool call fails with "ripgrep execution failed" — use `bash` `find`/`grep` instead.
- (Otherwise none)

## Next Move
1. Finish reading `channel.py` (all 941 lines): `ChannelData` methods, `ThreadChannel`/`ProcessChannel` producer-consumer mechanics.
2. Read `dag.py` (948 lines) and `pipeline_server.py` (570 lines) to understand `DAGExecutor`, `PipelineServer.set_response_op`, and where topology can be captured.
3. Read the unread middle of `operator.py` (`Op.__init__`, `_process`, `RequestOp.unpack_request_package`, `DAGExecutor`, thread vs process launch paths) and `error_catch.py` (243 lines, to add `SKIPPED = 3004`).
4. Then design and implement the routing/skipping mechanism (edge-activation bookkeeping per request) and verify with `PYTHONPATH=python python ...` from `/app`.

## Relevant Files
- `/workspace/repo/python/pipeline/operator.py`: Op base class, `RequestOp`, `DAGExecutor` — main implementation target for `route`/`on_skipped`/`get_succ_op_names`/`get_pred_op_names` and execution/skip logic.
- `/workspace/repo/python/pipeline/channel.py`: `ChannelData`, `ThreadChannel`, `ProcessChannel` — where per-request edge activation / partial joins must be enforced for both concurrency modes.
- `/workspace/repo/python/pipeline/dag.py`: DAG executor internals — terminal-skip response (`SKIPPED`), error propagation, replay semantics.
- `/workspace/repo/python/pipeline/error_catch.py`: `CustomExceptionCode` — add `SKIPPED = 3004`.
- `/workspace/repo/python/pipeline/pipeline_server.py`: `PipelineServer.set_response_op` — where succ/pred topology must be populated before return.
- `/workspace/repo/python/sitecustomize.py`: Py3.11 shims needed for imports (auto-loaded via `PYTHONPATH=python`).
- `/workspace/repo/python/pipeline/__init__.py`: package re-exports (may need updating for new API surface).
