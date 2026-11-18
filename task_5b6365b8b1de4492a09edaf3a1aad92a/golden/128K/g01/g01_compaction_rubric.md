# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the objective of adding an executable bit-exact CAN codec model in `modules.tools.gen_vehicle_protocol.frame_codec` exposing `SignalLayout`, `UnsupportedSignalError`, `signal_layout`, and `FrameCodec` with `decode`, `encode`, and `quantize`.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
States that DBC extraction must capture per-message `dlc` and keep signals longer than 32 bits.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that the emission stages `gen_protocols.py`, `gen_proto_file.py`, and `gen_vehicle_controller_and_manager.py` must skip signals rejected by `signal_layout` and print each skipped signal's name.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that `signal_layout` must slice signals exactly as the existing emitter does for both `motorola` and `intel` byte order.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States that signals rejected by `signal_layout` must appear nowhere in the generated `.proto` messages, C++ classes, or controllers.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: minor
Description:
States that what is generated for accepted signals must not change.
````

## Criterion 7

````text
ID: criteria_6
Category: Decision rationale
Weight: major
Description:
Specifies the rejection rule that `signal["len"] > 32` or any slice `byte_index` outside `[0, dlc - 1]` raises `UnsupportedSignalError` with attribute `signal_name`.
````

## Criterion 8

````text
ID: criteria_7
Category: Decision rationale
Weight: major
Description:
Records that `quantize` writes only one signal onto an all-zero `dlc` frame rather than using full `encode`, because other signals can have defaults with nonzero raw values.
````

## Criterion 9

````text
ID: criteria_8
Category: Decision rationale
Weight: minor
Description:
Records that non-`motorola` byte order falls through to the intel path, mirroring the emitter's else branch.
````

## Criterion 10

````text
ID: criteria_9
Category: Decision rationale
Weight: minor
Description:
Records that `SignalLayout` immutability is planned via `__slots__` with read-only `properties` `slices` and `bit_width`, so rebinding raises `AttributeError`.
````

## Criterion 11

````text
ID: criteria_10
Category: Decision rationale
Weight: minor
Description:
Records that clamping in `encode` applies only to non-enum and non-bool types, mirroring the C++ `BoundedValue` skip for enum and bool.
````

## Criterion 12

````text
ID: criteria_11
Category: Decision rationale
Weight: minor
Description:
Records that `gen_canbus_conf.py` is left untouched because it does not iterate vars.
````

## Criterion 13

````text
ID: criteria_12
Category: Decision rationale
Weight: minor
Description:
Records that the `len > 32` block in `gen_protocols.py` is removed, including its pre-existing `class_name` NameError path.
````

## Criterion 14

````text
ID: criteria_13
Category: Decision rationale
Weight: minor
Description:
Records that int32-overflow of the C++ accumulator is out of scope, with agreement required only where raw values fit `int32_t` and `%f`-printed `precision` and `offset` are lossless.
````

## Criterion 15

````text
ID: criteria_14
Category: Decision rationale
Weight: minor
Description:
Records that the import style is `from modules.tools.gen_vehicle_protocol.frame_codec import filter_protocol_vars`, matching the `gen.py` precedent.
````

## Criterion 16

````text
ID: criteria_15
Category: Decision rationale
Weight: minor
Description:
Records that the committed `vin15` entry in `demo.proto` is a pre-existing out-of-frame bug that is not regenerated because the change stays inside the generator package.
````

## Criterion 17

````text
ID: criteria_16
Category: Decision rationale
Weight: minor
Description:
Records that the `black_list` KeyError extraction bug is left as-is.
````

## Criterion 18

````text
ID: criteria_17
Category: Temporal coherence
Weight: major
Description:
Records that no files have been modified.
````

## Criterion 19

````text
ID: criteria_18
Category: Temporal coherence
Weight: major
Description:
Specifies creating `modules/tools/gen_vehicle_protocol/frame_codec.py` as the next step.
````

## Criterion 20

````text
ID: criteria_19
Category: Temporal coherence
Weight: major
Description:
Specifies the verification plan of running `extract_dbc_meta.py` on `apollo_demo.dbc`, running the emission stages, and diffing accepted-signal output against the committed demo proto and protocol files.
````

## Criterion 21

````text
ID: criteria_20
Category: Temporal coherence
Weight: minor
Description:
Records that exploration of the generator package and the committed generated code is complete and the design is settled.
````

## Criterion 22

````text
ID: criteria_21
Category: Temporal coherence
Weight: minor
Description:
Records that the slicing, decode, and encode semantics were confirmed by reading `throttle_command_100.cc`, where `Speed_Target : 47|12@0+` yields the slices `[(5,0,8),(6,4,4)]`.
````

## Criterion 23

````text
ID: criteria_22
Category: Artifact preservation
Weight: minor
Description:
Names `modules/tools/gen_vehicle_protocol/extract_dbc_meta.py` as the extraction stage to modify.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
Specifies that `protocol["dlc"]` is set to `int(items[3])` on `BO_` line items.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
Names `modules/tools/gen_vehicle_protocol/BUILD` as gaining an `apollo_py_binary` target named `frame_codec` and `deps` on the three stage targets.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
Names `modules/drivers/canbus/common/byte.cc` and `modules/drivers/canbus/common/byte.h` as defining the `get_byte` and `set_value` semantics the model must mirror.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
Names `modules/drivers/canbus/can_comm/protocol_data.h` as the source of the `BoundedValue` semantics that clamping mirrors.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
Names `modules/tools/gen_vehicle_protocol/apollo_demo.dbc` as the test input whose signals are all motorola with enums defined on `VAL_` lines.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
Names `modules/canbus_vehicle/demo/proto/demo.proto` and `modules/canbus_vehicle/demo/protocol/*.cc` as the old-tool baseline for diffing accepted-signal output.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
Specifies `filter_protocol_vars(protocol)` as the helper that returns supported vars and skipped names.
````

## Criterion 31

````text
ID: criteria_30
Category: Compression efficiency
Weight: minor
Description:
Contains at most 11300 characters.
````

## Criterion 32

````text
ID: criteria_31
Category: Structural clarity
Weight: minor
Description:
Presents completed work separately from pending work so the outstanding steps can be found without reading the whole summary.
````

## Criterion 33

````text
ID: criteria_32
Category: Goal fidelity
Weight: negative
Description:
States that `gen_canbus_conf.py` must be modified to skip unsupported signals.
````

## Criterion 34

````text
ID: criteria_33
Category: Decision rationale
Weight: negative
Description:
States that `quantize` is implemented by running full `encode` and then decoding the result.
````

## Criterion 35

````text
ID: criteria_34
Category: Temporal coherence
Weight: negative
Description:
States that `modules/tools/gen_vehicle_protocol/frame_codec.py` has already been written.
````
