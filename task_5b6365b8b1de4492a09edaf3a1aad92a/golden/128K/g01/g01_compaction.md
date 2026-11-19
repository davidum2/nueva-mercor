## Objective
- Add an executable bit-exact CAN codec model in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Expose `SignalLayout` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Expose `UnsupportedSignalError` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Expose `signal_layout` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Expose `FrameCodec` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Implement `FrameCodec.decode` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Implement `FrameCodec.encode` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Implement `quantize` on `FrameCodec` in `modules.tools.gen_vehicle_protocol.frame_codec`.
- Update DBC extraction in `extract_dbc_meta.py` to capture per-message `dlc`.
- Update DBC extraction in `extract_dbc_meta.py` to keep signals longer than 32 bits in YAML metadata.
- Re-plumb `gen_protocols.py` to skip signals rejected by `signal_layout`.
- Update `gen_protocols.py` to print each skipped signal name to stdout.
- Re-plumb `gen_proto_file.py` to skip signals rejected by `signal_layout`.
- Update `gen_proto_file.py` to print each skipped signal name to stdout.
- Re-plumb `gen_vehicle_controller_and_manager.py` to skip signals rejected by `signal_layout`.
- Update `gen_vehicle_controller_and_manager.py` to print each skipped signal name to stdout.
- Extend `modules/tools/gen_vehicle_protocol/BUILD` with a `frame_codec` target.
- Extend `modules/tools/gen_vehicle_protocol/BUILD` so `gen_protocols` depends on `frame_codec`.
- Extend `modules/tools/gen_vehicle_protocol/BUILD` so `gen_proto_file` depends on `frame_codec`.
- Extend `modules/tools/gen_vehicle_protocol/BUILD` so `gen_vehicle_controller_and_manager` depends on `frame_codec`.
- `signal_layout` must slice signals identically to the existing emitter for `motorola` byte order.
- `signal_layout` must slice signals identically to the existing emitter for `intel` byte order.
- `FrameCodec.decode` must match the generated C++ parse functions where `%f`-printed `precision` and `offset` are lossless and raw values fit `int32_t`.
- `FrameCodec.encode` must match the generated C++ set functions where `%f`-printed `precision` and `offset` are lossless and raw values fit `int32_t`.
- Signals rejected by `signal_layout` must be omitted from generated `.proto` messages.
- Signals rejected by `signal_layout` must be omitted from generated C++ protocol classes.
- Signals rejected by `signal_layout` must be omitted from generated controllers.
- Generated output for accepted signals must remain unchanged.

## Important Details
- `signal_layout(signal, dlc)` must replicate `gen_protocols.py`'s `get_byte_info` slicing algorithm.
- Based on the agent's finding (the file read of `gen_protocols.py` was truncated before `get_byte_info`), for `motorola` order `get_byte_info` sets `byte_idx = bit // 8` and MSB `bit_start = bit % 8`, takes `len = min(bit_start + 1, left)`, computes `start_bit = bit_start - len + 1`, and advances with `byte_idx += 1` and `bit_start = 7`.
- Based on the agent's finding (`gen_protocols.py` read truncated before `get_byte_info`), for `intel` order `get_byte_info` sets LSB `bit_start = bit % 8`, takes `len = min(8 - bit_start, left)`, advances with `byte_idx += 1` and `bit_start = 0`, and reverses the slice list.
- Based on the agent's finding (`gen_protocols.py` read truncated before `get_byte_info`), non-`motorola` `order` values fall through to the `intel` path, mirroring the emitter's `else` branch.
- Based on the agent's finding (`gen_protocols.py` read truncated before `get_byte_info`), the `motorola` path produces MSB-to-LSB-ordered `(byte_index, start_bit, length)` slices.
- Based on the agent's finding (`gen_protocols.py` read truncated before `get_byte_info`), the `intel` path produces MSB-to-LSB-ordered `(byte_index, start_bit, length)` slices after reversing the slice list.
- `signal_layout` raises `UnsupportedSignalError` carrying `signal_name = signal["name"]` if `signal["len"] > 32`.
- `signal_layout` raises `UnsupportedSignalError` carrying `signal_name = signal["name"]` if any slice `byte_index` lies outside `[0, dlc - 1]`.
- `UnsupportedSignalError` defines `def __init__(self, signal_name, message=None)` providing a default message when `message` is `None`.
- `SignalLayout` defines `def __init__(self, slices=(), bit_width=0)` defaulting `slices` to `()`.
- `SignalLayout` defines `def __init__(self, slices=(), bit_width=0)` defaulting `bit_width` to `0`.
- `SignalLayout` defines `__slots__ = ("_slices", "_bit_width")`.
- `SignalLayout` exposes `slices` as a read-only property so rebinding raises `AttributeError`.
- `SignalLayout` exposes `bit_width` as a read-only property so rebinding raises `AttributeError`.
- `SignalLayout` normalizes `slices` to a tuple of tuples in `__init__`.
- `SignalLayout` defines `__eq__` based on `(slices, bit_width)`.
- `SignalLayout` defines `__hash__` based on `(slices, bit_width)`.
- `SignalLayout` defines `__repr__` based on `(slices, bit_width)`.
- In `extract_dbc_meta.py`, `BO_` lines (e.g., `BO_ 1104 BMS_0x450: 8 VCU`) set `protocol["dlc"] = int(items[3])`.
- In `extract_dbc_meta.py`, the `protocol["dlc"] = int(items[3])` assignment is planned to be placed after the `protocol["name"]` line.
- In `extract_dbc_meta.py`, removing the `if var_info["len"] <= 32` filter keeps signals wider than 32 bits in YAML.
- `FrameCodec(protocol)` stores `self.dlc = int(protocol["dlc"])`.
- `FrameCodec.__init__` validates each signal in `vars` by calling `signal_layout(var, dlc)`.
- `FrameCodec.__init__` raises `UnsupportedSignalError` on the first signal rejected by `signal_layout`.
- `FrameCodec` treats extracted YAML signal names as-is (exact-case match) without lowercasing them.
- `extract_dbc_meta.py` preserves original DBC signal-name casing in YAML (prefixing C++ reserved words with `MY_`).
- `gen_protocols.py` mutates `var["name"]` to lowercase only later during C++ code generation.
- `FrameCodec.layout(name)` returns the `SignalLayout` for a known signal name.
- `FrameCodec.layout(name)` raises `KeyError` for an unknown signal name.
- `FrameCodec.decode` raises `ValueError` if `len(data) < self.dlc`.
- `FrameCodec.decode` accumulates raw bits MSB-to-LSB via `raw = (raw << length) | ((data[byte_index] >> start_bit) & ((1 << length) - 1))`.
- `FrameCodec.decode` sign-extends `raw` when `is_signed_var` via `raw -= 1 << bit_width` if `raw >= 1 << (bit_width - 1)`, which the agent reasoned matches C++ `x <<= (32 - len); x >>= (32 - len)` (generated C++ parse code not shown).
- `FrameCodec.decode` returns `raw != 0` for `bool` signals.
- `FrameCodec.decode` returns unscaled `int(raw)` for `enum` signals, which the agent reasoned matches `static_cast<Enum>(x)` (generated C++ parse code not shown).
- `FrameCodec.decode` computes `phys = raw * precision + offset` for numeric signals.
- `FrameCodec.decode` returns `int(phys)` truncated toward zero for `int` signals.
- `FrameCodec.decode` returns `float(phys)` for `double` signals.
- `int32_t` overflow of the C++ accumulator is out of scope for `FrameCodec` agreement.
- `FrameCodec.encode` raises `ValueError` if `data` is provided with `len(data) < self.dlc`.
- `FrameCodec.encode` initializes a zero-filled `bytearray(self.dlc)` when `data` is `None`.
- `FrameCodec.encode` initializes the working buffer from `bytearray(data[:self.dlc])` when `data` is provided.
- `FrameCodec.encode` truncates a provided `data` buffer longer than `self.dlc` to `self.dlc` bytes.
- `FrameCodec.encode` raises `KeyError(name)` when `values` contains any unknown signal name.
- `FrameCodec.encode` validates `data` length (`ValueError`) before validating `values` keys (`KeyError`) because buffer construction precedes key checking.
- `FrameCodec.encode` applies all signals in `vars` declaration order so later signals overwrite shared bits.
- Unspecified `bool` signals in `encode` default to `False`.
- Unspecified `int` signals in `encode` default to `0`.
- Unspecified `double` signals in `encode` default to `0.0`.
- Unspecified `enum` signals in `encode` default to key `0` if present, otherwise `next(iter(enum))`.
- `FrameCodec.encode` clamps physical values only for non-enum and non-bool signal types.
- The agent reasoned that skipping clamping for `enum` and `bool` mirrors C++ `BoundedValue` behavior (generated C++ set code not shown).
- `FrameCodec.encode` parses float bounds from `physical_range` (`[low|high]`) by splitting on `'|'` and stripping the surrounding square brackets.
- `FrameCodec.encode` leaves the physical value unchanged without clamping when the parsed `low > high`.
- `FrameCodec.encode` computes `raw = int((val - offset) / precision)` truncated toward zero.
- `FrameCodec.encode` writes slices LSB-to-MSB via `piece = (raw >> shift) & ((1 << length) - 1)` and `frame[byte_index] = (frame[byte_index] & ~mask) | (piece << start_bit)`.
- `quantize(values=None)` on `FrameCodec` processes each signal in `vars` independently by writing only that signal onto an all-zero `dlc` frame and decoding that signal.
- `quantize` must not call full `encode` because other signals' defaults can have nonzero raw values (e.g., `offset=-40` gives raw `40`) that corrupt shared bits.
- `quantize` returns an entry for every signal in `vars`.
- `quantize` on `FrameCodec` silently ignores unknown keys in `values` because the specification defines `KeyError` only for `encode`.
- `frame_codec.py` provides `filter_protocol_vars(protocol)` returning `(supported_vars, skipped_names)` via `signal_layout(var, protocol["dlc"])`.
- `filter_protocol_vars` returns `(supported_vars, skipped_names)` without printing so callers handle stdout reporting explicitly.
- `gen_protocols.py` calls `filter_protocol_vars` at its entry function.
- Filtering runs once per protocol at the entry function of `gen_protocols.py` rather than inside inner generators to avoid printing skipped signal names twice.
- `gen_proto_file.py` calls `filter_protocol_vars` at its entry function.
- In `gen_proto_file.py`, the `filter_protocol_vars` normalization loop is planned to be inserted right after `protocols = content["protocols"]`.
- `gen_vehicle_controller_and_manager.py` calls `filter_protocol_vars` at its entry function.
- `gen_protocols.py` mutates `protocol["vars"] = supported_vars`.
- `gen_proto_file.py` mutates `protocol["vars"] = supported_vars`.
- `gen_vehicle_controller_and_manager.py` mutates `protocol["vars"] = supported_vars`.
- `gen_protocols.py` prints e.g. `print("Skip unsupported signal: %s" % skipped_name)` for each skipped signal.
- `gen_proto_file.py` prints e.g. `print("Skip unsupported signal: %s" % skipped_name)` for each skipped signal.
- `gen_vehicle_controller_and_manager.py` prints e.g. `print("Skip unsupported signal: %s" % skipped_name)` for each skipped signal.
- A protocol whose signals are all rejected by `signal_layout` is still emitted at the protocol level because the spec does not skip protocols.
- `gen_protocols.py` imports `filter_protocol_vars` via `from modules.tools.gen_vehicle_protocol.frame_codec import filter_protocol_vars`, matching `gen.py`.
- `gen_proto_file.py` imports `filter_protocol_vars` via `from modules.tools.gen_vehicle_protocol.frame_codec import filter_protocol_vars`, matching `gen.py`.
- `gen_vehicle_controller_and_manager.py` imports `filter_protocol_vars` via `from modules.tools.gen_vehicle_protocol.frame_codec import filter_protocol_vars`, matching `gen.py`.
- `gen_protocols.py` removes the `if var["len"] > 32` block in `gen_control_value_func_impl` so the stage retains no width or frame-length rule.
- The agent noted an unverified finding that the `if var["len"] > 32` block in `gen_control_value_func_impl` also references an undefined `class_name`.
- The agent inferred (unverified because the file read was truncated) that `gen_canbus_conf.py` does not iterate `vars`.
- The agent planned to leave `gen_canbus_conf.py` untouched because it is inferred not to iterate `vars`.
- `modules/tools/gen_vehicle_protocol/BUILD` adds `apollo_py_binary(name = "frame_codec", srcs = ["frame_codec.py"])`.
- In `modules/tools/gen_vehicle_protocol/BUILD`, the `frame_codec` target is placed alphabetically after `extract_dbc_meta`.
- `modules/tools/gen_vehicle_protocol/BUILD` adds `":frame_codec"` to `deps` of `gen_proto_file`.
- `modules/tools/gen_vehicle_protocol/BUILD` adds `":frame_codec"` to `deps` of `gen_protocols`.
- `modules/tools/gen_vehicle_protocol/BUILD` adds `":frame_codec"` to `deps` of `gen_vehicle_controller_and_manager`.
- In `modules/tools/gen_vehicle_protocol/BUILD`, `gen` receives no direct `":frame_codec"` dependency because it depends transitively on the stage targets without importing `frame_codec` directly.
- In `modules/tools/gen_vehicle_protocol/BUILD`, `extract_dbc_meta` receives no direct `":frame_codec"` dependency because `extract_dbc_meta.py` only writes `dlc` without importing `frame_codec` or consulting `signal_layout`.
- The agent inferred `Byte::get_byte` semantics from `modules/drivers/canbus/common/byte.cc` (unverified, file read truncated).
- The agent inferred `Byte::set_value` semantics from `modules/drivers/canbus/common/byte.cc` (unverified, file read truncated).
- `ProtocolData::BoundedValue` (`lower > upper` returns `val`) was confirmed in `modules/drivers/canbus/can_comm/protocol_data.h`.
- In `apollo_demo.dbc`, all signals use motorola `@0+` order with no `@1` intel examples.
- In `apollo_demo.dbc`, `VAL_` lines define enums such as `Gear_Actual` and `Turn_Light_Actual`.
- `VIN15 : 63|16` in `vin_resp2` yields byte 8 (outside an 8-byte frame).
- `VIN15` in `vin_resp2` will be skipped by `signal_layout` under the updated emitters.
- `gen_protocols.py` will print `VIN15` to stdout when skipping it.
- `gen_proto_file.py` will print `VIN15` to stdout when skipping it.
- `gen_vehicle_controller_and_manager.py` will print `VIN15` to stdout when skipping it.
- `modules/canbus_vehicle/demo/proto/demo.proto` contains `optional int32 vin15 = 1;`.
- Existing generated code under `modules/canbus_vehicle/demo` will not be regenerated because task scope is limited to `modules/tools/gen_vehicle_protocol`.
- The agent noted an unverified hypothesis that a blacklisted `BO_` line followed by `SG_` lines in `extract_dbc_meta.py` may hit a `KeyError` on `protocol["vars"]`.
- The agent chose to leave the `black_list` extraction behavior unchanged because the potential `protocol["vars"]` `KeyError` is a pre-existing bug outside the requested task scope.
- The agent noted that the pre-existing `black_list` `KeyError` presumably does not trigger with the empty `black_list: []` config lists.
- No Python tests exist for this package in the repo.
- Existing C++ tests under `modules/canbus_vehicle/...` remain untouched because task scope is limited to `modules/tools/gen_vehicle_protocol`.

## Work State
### Completed
- Read `modules/tools/gen_vehicle_protocol/extract_dbc_meta.py`.
- Read `modules/tools/gen_vehicle_protocol/gen_protocols.py`.
- Read `modules/tools/gen_vehicle_protocol/gen_proto_file.py`.
- Read `modules/tools/gen_vehicle_protocol/gen_vehicle_controller_and_manager.py`.
- Read `modules/tools/gen_vehicle_protocol/gen.py`.
- Read `modules/tools/gen_vehicle_protocol/gen_canbus_conf.py`.
- Read `modules/tools/gen_vehicle_protocol/BUILD`.
- Read `modules/tools/gen_vehicle_protocol/README.md`.
- Read `modules/tools/gen_vehicle_protocol/gem_conf.yml`.
- Read `modules/tools/gen_vehicle_protocol/lincoln_conf.yml`.
- Read `modules/tools/gen_vehicle_protocol/apollo_demo.dbc`.
- Read `modules/tools/gen_vehicle_protocol/template/control_protocol.cc.tpl`.
- Read `modules/tools/gen_vehicle_protocol/template/control_protocol.h.tpl`.
- Read `modules/tools/gen_vehicle_protocol/template/report_protocol.cc.tpl`.
- Read `modules/drivers/canbus/common/byte.h`.
- Read `modules/drivers/canbus/common/byte.cc`.
- Read `modules/drivers/canbus/can_comm/protocol_data.h`.
- Read `modules/canbus_vehicle/demo/protocol/throttle_command_100.cc`.
- Grepped `modules/canbus_vehicle/demo` for `vin15`.
- Grepped `modules/canbus_vehicle/demo` for `vin_resp`.
- Read `tools/proto/proto.bzl` (`apollo_py_binary`).
- Confirmed slicing semantics in `modules/canbus_vehicle/demo/protocol/throttle_command_100.cc`: `Speed_Target : 47|12@0+` yields slices `[(5,0,8),(6,4,4)]`.
- Confirmed encode write semantics in `modules/canbus_vehicle/demo/protocol/throttle_command_100.cc`: `set_p_speed_target` writes `data+6 (4,4)` then `data+5 (0,8)`.
- Inferred decode semantics in `modules/canbus_vehicle/demo/protocol/throttle_command_100.cc` (the `Parse` implementation was truncated in the read output).
- Settled the design for `frame_codec.py`.
- Settled the design for `extract_dbc_meta.py`.
- Settled the design for `gen_protocols.py`.
- Settled the design for `gen_proto_file.py`.
- Settled the design for `gen_vehicle_controller_and_manager.py`.
- Settled the design for `modules/tools/gen_vehicle_protocol/BUILD`.

### Active
- About to write `modules/tools/gen_vehicle_protocol/frame_codec.py`.
- No files have been modified yet.

### Blocked
- Nothing is currently blocked.

## Next Move
1. Create `modules/tools/gen_vehicle_protocol/frame_codec.py` with the Apollo license header.
2. Add the `#!/usr/bin/env python3` shebang to `modules/tools/gen_vehicle_protocol/frame_codec.py`.
3. Implement `UnsupportedSignalError` in `modules/tools/gen_vehicle_protocol/frame_codec.py`.
4. Implement `SignalLayout` in `modules/tools/gen_vehicle_protocol/frame_codec.py`.
5. Implement `signal_layout` in `modules/tools/gen_vehicle_protocol/frame_codec.py`.
6. Implement `filter_protocol_vars` in `modules/tools/gen_vehicle_protocol/frame_codec.py`.
7. Implement `FrameCodec` in `modules/tools/gen_vehicle_protocol/frame_codec.py`.
8. Update `extract_dbc_meta.py` to set `protocol["dlc"] = int(items[3])`.
9. Update `extract_dbc_meta.py` to drop the `len <= 32` filter.
10. Wire `filter_protocol_vars` into `gen_protocols.py`.
11. Add skipped-signal name printing to stdout in `gen_protocols.py`.
12. Remove the `if var["len"] > 32` branch from `gen_protocols.py`.
13. Wire `filter_protocol_vars` into `gen_proto_file.py`.
14. Add skipped-signal name printing to stdout in `gen_proto_file.py`.
15. Wire `filter_protocol_vars` into `gen_vehicle_controller_and_manager.py`.
16. Add skipped-signal name printing to stdout in `gen_vehicle_controller_and_manager.py`.
17. Add the `apollo_py_binary(name = "frame_codec", srcs = ["frame_codec.py"])` target to `modules/tools/gen_vehicle_protocol/BUILD`.
18. Add `":frame_codec"` to `deps` of `gen_proto_file` in `modules/tools/gen_vehicle_protocol/BUILD`.
19. Add `":frame_codec"` to `deps` of `gen_protocols` in `modules/tools/gen_vehicle_protocol/BUILD`.
20. Add `":frame_codec"` to `deps` of `gen_vehicle_controller_and_manager` in `modules/tools/gen_vehicle_protocol/BUILD`.
21. Write a scratch sanity-test script in `/tmp/opencode` rather than placing test files inside `modules/tools/gen_vehicle_protocol/`.
22. Run `gen_protocols.py` on extracted YAML from `apollo_demo.dbc`.
23. Run `gen_proto_file.py` on extracted YAML from `apollo_demo.dbc`.
24. Run `gen_vehicle_controller_and_manager.py` on extracted YAML from `apollo_demo.dbc`.
25. Diff accepted-signal output against `modules/canbus_vehicle/demo/proto/demo.proto`.
26. Diff accepted-signal output against `modules/canbus_vehicle/demo/protocol/*`.
27. Verify that out-of-range signals are omitted from generated outputs.
28. Verify that omitted signal names are printed to stdout.
29. Sanity-test `FrameCodec.decode` in `/tmp/opencode` against expected C++ logic.
30. Sanity-test `FrameCodec.encode` in `/tmp/opencode` against expected C++ logic.
31. Sanity-test `quantize` on `FrameCodec` in `/tmp/opencode` against expected C++ logic.

## Relevant Files
- `modules/tools/gen_vehicle_protocol/frame_codec.py`: new module to create with the executable codec model.
- `modules/tools/gen_vehicle_protocol/frame_codec.py`: new module to create with the `filter_protocol_vars` helper.
- `modules/tools/gen_vehicle_protocol/extract_dbc_meta.py`: extraction stage to modify.
- `modules/tools/gen_vehicle_protocol/gen_protocols.py`: C++ protocol emitter to re-plumb.
- `modules/tools/gen_vehicle_protocol/gen_proto_file.py`: `.proto` emitter to re-plumb.
- `modules/tools/gen_vehicle_protocol/gen_vehicle_controller_and_manager.py`: vehicle controller emitter to re-plumb.
- `modules/tools/gen_vehicle_protocol/BUILD`: build file to extend.
- `modules/tools/gen_vehicle_protocol/apollo_demo.dbc`: test DBC input containing `VIN15 : 63|16`.
- `modules/drivers/canbus/common/byte.cc`: `Byte::get_byte` implementation.
- `modules/drivers/canbus/common/byte.cc`: `Byte::set_value` implementation.
- `modules/drivers/canbus/common/byte.h`: `Byte` header declarations.
- `modules/drivers/canbus/can_comm/protocol_data.h`: `BoundedValue` reference semantics.
- `modules/canbus_vehicle/demo/proto/demo.proto`: committed demo `.proto` containing `vin15`.
- `modules/canbus_vehicle/demo/protocol/throttle_command_100.cc`: committed C++ protocol file confirming slice order.
- `modules/tools/gen_vehicle_protocol/gen.py`: absolute import precedent.
- `modules/tools/gen_vehicle_protocol/gen_canbus_conf.py`: file left untouched.
- `modules/tools/gen_vehicle_protocol/template/*`: template files left untouched.
