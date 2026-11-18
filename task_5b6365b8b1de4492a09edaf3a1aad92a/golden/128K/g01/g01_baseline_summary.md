## Objective
- Add an executable bit-exact CAN codec model in `modules.tools.gen_vehicle_protocol.frame_codec` (`SignalLayout`, `UnsupportedSignalError`, `signal_layout`, `FrameCodec` with `decode`/`encode`/`quantize`), make DBC extraction capture per-message `dlc` and keep >32-bit signals, and re-plumb the three emission stages (`gen_protocols.py`, `gen_proto_file.py`, `gen_vehicle_controller_and_manager.py`) to skip/print signals rejected by `signal_layout`, plus BUILD target/deps changes.

## Important Details
- `signal_layout(signal, dlc)` must replicate `gen_protocols.py`'s `get_byte_info` exactly: motorola → `byte_idx = bit // 8`, `bit_start = bit % 8` (MSB pos), slice `len = min(bit_start + 1, left)`, `start_bit = bit_start - len + 1`, then `byte_idx += 1`, `bit_start = 7`; intel → `bit_start = bit % 8` (LSB pos), `len = min(8 - bit_start, left)`, then `byte_idx += 1`, `bit_start = 0`, list reversed. Both produce MSB→LSB-ordered slices. Non-`motorola` order falls through to intel (mirrors emitter's else branch).
- Rejections: `signal["len"] > 32` OR any slice `byte_index` outside `[0, dlc - 1]` → `UnsupportedSignalError` with attribute `signal_name` (use `signal["name"]`).
- `SignalLayout` immutability plan: `__slots__ = ("_slices", "_bit_width")` + read-only `properties` `slices`/`bit_width` (rebind → AttributeError), normalize slices to `tuple(tuple(s) ...)` in `__init__`, define `__eq__`/`__hash__`/`__repr__` on key `(slices, bit_width)`.
- DBC extraction (`extract_dbc_meta.py`): on `BO_` line (shlex items, e.g. `BO_ 1104 BMS_0x450: 8 VCU`) set `protocol["dlc"] = int(items[3])`; delete the `if var_info["len"] <= 32` filter so all signals are written to YAML.
- `FrameCodec(protocol)`: `self.dlc = int(protocol["dlc"])`; `__init__` calls `signal_layout(var, dlc)` per var, raising `UnsupportedSignalError` for the first rejected; `.layout(name)` → `KeyError` for unknown names.
- `decode(data)`: `ValueError` if `len(data) < self.dlc`; raw accumulates MSB→LSB: `raw = (raw << length) | ((data[byte_index] >> start_bit) & ((1 << length) - 1))`; sign extension when `is_signed_var`: `raw -= 1 << bit_width` if `raw >= 1 << (bit_width - 1)` (matches C++ `x <<= (32-len); x >>= (32-len)`); types: `bool` → `raw != 0`, `enum` → `int(raw)` (unscaled, matches `static_cast<Enum>(x)`), `int` → `int(phys)` truncated toward zero, `double` → `float(phys)` where `phys = raw * precision + offset`. int32-overflow of C++ accumulator explicitly out of scope (agreement only where raw fits int32 and `%f`-printed precision/offset are lossless).
- `encode(values=None, data=None)`: buffer `bytearray(self.dlc)` (zeros) or `bytearray(data[:self.dlc])` (decision: truncate longer data to dlc); `ValueError` if `len(data) < self.dlc`; explicit validation loop over `values` keys → `KeyError(name)` for unknown names; apply ALL vars in declaration order (unspecified get defaults: `False`/`0`/`0.0`, enum → key `0` if present else `next(iter(enum))`); clamping ONLY for non-enum/non-bool types (mirrors C++ `BoundedValue` skip for enum/bool), bounds parsed from `physical_range` via `split('|')`, `items[0].split('[')[1]`, `items[1].split(']')[0]` as floats, left unchanged if low > high; raw `= int((val - offset) / precision)` truncated toward zero; write slices LSB→MSB: `piece = (raw >> shift) & ((1 << length) - 1)`, `frame[byte] = (frame[byte] & ~mask) | (piece << start_bit)` (Python two's-complement `&`/`>>` on negatives matches C++ arithmetic-shift semantics).
- `quantize(values=None)`: per signal, isolated: take `values.get(name, default)`, clamp+convert to raw, write ONLY that signal onto an all-zero `dlc` frame, then decode that signal (must NOT use full `encode`, because other signals' defaults can have nonzero raw e.g. offset=-40 → raw 40 and would corrupt shared bits); result entry for every var; unknown keys in `values` silently ignored (decided).
- Emission stages plan: helper in `frame_codec.py` `filter_protocol_vars(protocol)` → `(supported_vars, skipped_names)` calling `signal_layout(var, protocol["dlc"])` per var; each of the 3 stages filters at its entry function and mutates `protocol["vars"] = supported_vars` (each stage loads its own YAML copy, so mutation is safe), printing e.g. `print("Skip unsupported signal: %s" % skipped_name)` per skipped signal; import style `from modules.tools.gen_vehicle_protocol.frame_codec import filter_protocol_vars` (package-absolute, matching `gen.py` precedent).
- `gen_protocols.py`: remove the `if var["len"] > 32` block in `gen_control_value_func_impl` (it also references undefined `class_name` — pre-existing NameError path) so the stage "keeps no width or frame-length rule of its own".
- `gen_canbus_conf.py`: untouched (doesn't iterate vars; not in the stage list).
- BUILD: add `apollo_py_binary(name = "frame_codec", srcs = ["frame_codec.py"])`; add `deps = [":frame_codec"]` to `gen_proto_file`, `gen_protocols`, `gen_vehicle_controller_and_manager` targets (mirrors how `gen.py` deps on stage targets).
- `Byte::get_byte`/`set_value` semantics confirmed in `modules/drivers/canbus/common/byte.cc`; `ProtocolData::BoundedValue` (lower>upper → return val) in `modules/drivers/canbus/can_comm/protocol_data.h`.
- Demo DBC facts: all signals motorola `@0+` (no `@1` intel examples); `VAL_` lines define enums (e.g. `Gear_Actual`, `Turn_Light_Actual`); `VIN15 : 63|16` in `vin_resp2` yields byte 8 → will be newly skipped/reported, whereas committed old-tool output `modules/canbus_vehicle/demo/proto/demo.proto` still contains `optional int32 vin15 = 1;` (line 450) — pre-existing out-of-frame bug, not to be regenerated (change stays inside the generator package).
- Pre-existing extraction bug (leave as-is): blacklisted `BO_` followed by `SG_` lines hits `len(protocol["vars"])` KeyError since `vars` unset; only triggers with non-empty `black_list`.
- No existing Python tests for this package in repo; existing C++ tests under `modules/canbus_vehicle/...` are left as-is.

## Work State
### Completed
- Full exploration: `extract_dbc_meta.py`, `gen_protocols.py`, `gen_proto_file.py`, `gen_vehicle_controller_and_manager.py`, `gen.py`, `gen_canbus_conf.py`, `BUILD`, `README.md`, conf ymls, `apollo_demo.dbc` (BO_/SG_/VAL_ content), templates, `byte.h`/`byte.cc`, `protocol_data.h`, committed generated demo code, `tools/proto/proto.bzl` (`apollo_py_binary` macro).
- Verified slicing/encode/decode semantics against committed generated code (e.g. `modules/canbus_vehicle/demo/protocol/throttle_command_100.cc`: `Speed_Target : 47|12@0+` → slices `[(5,0,8),(6,4,4)]`, encode writes `data+6 (4,4)` then `data+5 (0,8)`).
- Complete design for `frame_codec.py` (data structures, error paths, decode/encode/quantize algorithms), extraction change, stage filtering pattern, and BUILD wiring — all settled as described above.

### Active
- About to write `modules/tools/gen_vehicle_protocol/frame_codec.py` (no files modified yet).

### Blocked
- (none)

## Next Move
1. Create `modules/tools/gen_vehicle_protocol/frame_codec.py` with `UnsupportedSignalError`, `SignalLayout`, `signal_layout`, `filter_protocol_vars`, and `FrameCodec` per the design above (keep Apollo license header + `#!/usr/bin/env python3` style).
2. Modify `extract_dbc_meta.py` (add `protocol["dlc"] = int(items[3])`, drop the `len <= 32` filter), then wire `filter_protocol_vars` + skip-print into `gen_protocols.py` (also remove its `len > 32` branch), `gen_proto_file.py`, `gen_vehicle_controller_and_manager.py`; update `BUILD` with the `frame_codec` target and deps on the three stage targets.
3. Verify: run `extract_dbc_meta.py` on `apollo_demo.dbc` (expect `dlc` keys, YAML keeps all signals), then run the stages and diff accepted-signal output against `modules/canbus_vehicle/demo/proto/demo.proto` + `modules/canbus_vehicle/demo/protocol/*` (expect only removal of out-of-range signals like `VIN15`/`VIN07`-class entries plus skip prints), and sanity-test `FrameCodec.decode`/`encode`/`quantize` round-trips against the generated C++ logic.

## Relevant Files
- `modules/tools/gen_vehicle_protocol/frame_codec.py`: new module to create (model + `filter_protocol_vars` helper).
- `modules/tools/gen_vehicle_protocol/extract_dbc_meta.py`: add `dlc` capture, drop >32-bit signal filter.
- `modules/tools/gen_vehicle_protocol/gen_protocols.py`: filter vars, print skips, remove its own `len > 32` rule in `gen_control_value_func_impl`.
- `modules/tools/gen_vehicle_protocol/gen_proto_file.py`: filter vars in `gen_proto_file()`/`write_single_protocol_vars` path, print skips.
- `modules/tools/gen_vehicle_protocol/gen_vehicle_controller_and_manager.py`: filter vars in `gen_vehicle_controller_and_manager()`, print skips.
- `modules/tools/gen_vehicle_protocol/BUILD`: add `:frame_codec` target, deps for the three stage targets.
- `modules/tools/gen_vehicle_protocol/apollo_demo.dbc`: test input (all-motorola, `BO_ ...: 8`, `VAL_` enums; `VIN15 : 63|16` is the out-of-range case).
- `modules/drivers/canbus/common/byte.cc`, `modules/drivers/canbus/common/byte.h`: `get_byte`/`set_value` semantics the model must mirror.
- `modules/drivers/canbus/can_comm/protocol_data.h`: `BoundedValue` semantics (lower > upper → return val; skip for enum/bool in emitter).
- `modules/canbus_vehicle/demo/proto/demo.proto`, `modules/canbus_vehicle/demo/protocol/*.cc`: old-tool baseline to verify accepted-signal output unchanged (modulo newly skipped out-of-range signals).
- `modules/tools/gen_vehicle_protocol/gen.py`, `modules/tools/gen_vehicle_protocol/gen_canbus_conf.py`, `modules/tools/gen_vehicle_protocol/template/*`: import-style precedent (`from modules.tools.gen_vehicle_protocol.X import Y`) and untouched files (gen_canbus_conf not re-plumbed).
