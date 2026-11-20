import json, math, pathlib

base = pathlib.Path("task_531f225fd0c74bc1a473541ac007fa95/golden/96K")
g03_md = (base / "g03/g03_compaction.md").read_text(encoding="utf-8")
g03_cap = int(math.ceil(1.1 * len(g03_md) / 100.0) * 100)
print(f"g03_compaction.md len={len(g03_md)}, D1.5 cap={g03_cap}")

STRUCT_DESC = "Keeps related facts grouped together so information on each topic is directly findable."

def process_rubric(pt, drop_ids, replacements, d15_cap=None):
    p = base / pt / f"{pt}_compaction_rubric.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    new_criteria = []
    for c in data["criteria"]:
        cid = c["criteria_id"]
        if cid in drop_ids:
            continue
        if cid in replacements:
            c["description"] = replacements[cid].get("description", c["description"])
            if "weight" in replacements[cid]:
                c["metadata"]["weight"] = replacements[cid]["weight"]
        if c["metadata"]["category"] == "Structural clarity":
            c["description"] = STRUCT_DESC
            c["metadata"]["weight"] = "minor"
        if d15_cap is not None and c["metadata"]["category"] == "Compression efficiency":
            c["description"] = f"Contains at most {d15_cap} characters."
        new_criteria.append(c)

    # Re-index
    for idx, c in enumerate(new_criteria):
        c["criteria_id"] = f"criteria_{idx}"

    # Ensure D1.5 is NOT at idx % 4 == 3
    for idx, c in enumerate(new_criteria):
        if c["metadata"]["category"] == "Compression efficiency" and idx % 4 == 3:
            # swap with idx - 1
            new_criteria[idx - 1], new_criteria[idx] = new_criteria[idx], new_criteria[idx - 1]
            new_criteria[idx - 1]["criteria_id"] = f"criteria_{idx - 1}"
            new_criteria[idx]["criteria_id"] = f"criteria_{idx}"
            break

    pos = [c for c in new_criteria if c["metadata"]["weight"] != "negative"]
    maj = [c for c in pos if c["metadata"]["weight"] == "major"]
    neg = [c for c in new_criteria if c["metadata"]["weight"] == "negative"]
    print(f"{pt}: total={len(new_criteria)}, pos={len(pos)}, maj={len(maj)} ({len(maj)/len(pos)*100:.2f}%), neg={len(neg)}")
    p.write_text(json.dumps({"criteria": new_criteria}, indent=2) + "\n", encoding="utf-8")

# g01: drop 21, 43, 48, 49, 50, 52, 56 (7 criteria -> 83 total, 81 pos)
process_rubric(
    "g01",
    drop_ids={"criteria_21", "criteria_43", "criteria_48", "criteria_49", "criteria_50", "criteria_52", "criteria_56"},
    replacements={
        "criteria_20": {"description": "States that a fresh engine using the same database must reload and resume a suspended workflow."},
        "criteria_42": {"description": "States that indefinite waits and waits whose deadline is later than now stay suspended after a timeout sweep."},
        "criteria_47": {"description": "States that signal delivery, timeout sweeps, and compensation must have a single winner per activation, including concurrent duplicate signals."},
        "criteria_51": {"description": "States that a waiting child suspends its enclosing SubStateMachine state and parent machine with WA."},
        "criteria_55": {"description": "States that compensating an ancestor cancels active descendant waits, including in grandchildren, before any completed predecessor is compensated."},
    }
)

# g02: drop 15, 32, 36, 37, 38, 42 (6 criteria -> 84 total, 81 pos)
process_rubric(
    "g02",
    drop_ids={"criteria_15", "criteria_32", "criteria_36", "criteria_37", "criteria_38", "criteria_42"},
    replacements={
        "criteria_14": {"description": "States that a fresh engine using the same database must reload and resume a suspended workflow."},
        "criteria_31": {"description": "States that indefinite waits and waits whose deadline is later than `now` stay suspended after a timeout sweep."},
        "criteria_35": {"description": "States that signal delivery, timeout sweeps, and compensation must have a single winner per activation, including concurrent duplicate signals."},
        "criteria_41": {"description": "States that a waiting child suspends its enclosing SubStateMachine state and parent machine with WA."},
    }
)

# g03: drop 21, 42, 47, 48, 49, 51, 55 (7 criteria -> 83 total, 80 pos)
process_rubric(
    "g03",
    drop_ids={"criteria_21", "criteria_42", "criteria_47", "criteria_48", "criteria_49", "criteria_51", "criteria_55"},
    replacements={
        "criteria_20": {"description": "States that a fresh engine using the same database must reload and resume a suspended workflow."},
        "criteria_22": {"description": "Specifies a `signal(String stateMachineInstanceId, String waitStateInstanceId, String event, Map<String, Object> payload)` method on `StateMachineEngine`."},
        "criteria_41": {"description": "States that indefinite waits and waits whose deadline is later than `now` stay suspended after a timeout sweep."},
        "criteria_46": {"description": "States that signal delivery, timeout sweeps, and compensation must have a single winner per activation, including concurrent duplicate signals."},
        "criteria_50": {"description": "States that a waiting child suspends its enclosing SubStateMachine state and parent machine with WA."},
        "criteria_54": {"description": "States that compensating an ancestor cancels active descendant waits, including in grandchildren, before any completed predecessor is compensated."},
    },
    d15_cap=g03_cap
)
