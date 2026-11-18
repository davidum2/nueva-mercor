#!/bin/bash
# Apply the submission to a clean checkout before running the tests.
if ! sh /tests/apply_submission.sh "/app"; then
  mkdir -p /logs/verifier; cat /logs/verifier/apply_submission.log 2>/dev/null
  echo 0 > /logs/verifier/reward.txt; exit 0
fi
# Run the test suites, write their reports under /logs/verifier and grade them.
set -uo pipefail
trap 'if [ ! -f /logs/verifier/reward.json ] && [ ! -f /logs/verifier/reward.txt ]; then mkdir -p /logs/verifier; echo -1 > /logs/verifier/reward.txt; fi' EXIT
log() { echo "[verifier] $*"; }
cd /app || { mkdir -p /logs/verifier; exit 6; }

python3 /tests/grader.py prepare || exit $?

# Raw output of every build and test run.
export RUN_LOG=/logs/verifier/run.log
: > "$RUN_LOG" 2>/dev/null || true
run_log() { echo "+ $*" >> "$RUN_LOG" 2>/dev/null; "$@" 2>&1 | tee -a "$RUN_LOG"; return "${PIPESTATUS[0]}"; }

require_cmd() { command -v "$1" >/dev/null 2>&1 || { log "ERROR: missing $1; PATH=$PATH"; exit 127; }; }
require_cmd cmake ctest python3

# The existing CableSpan tests and the friction tests get separate reports; a failing test must not stop the script.
set +e

# The build directory comes from the image; a submission may not change it.
if git -c safe.directory='*' diff --name-only HEAD refs/submission/final -- | grep -Eq '^out(/|$)' || [ -L /app/out ] || [ -L /app/out/build ]; then
  log "ERROR: the submission changes the build directory out/"; echo 0 > /logs/verifier/reward.txt; exit 0
fi

# Compilers and test programs run as an unprivileged user; cmake configure, ctest, reports and grading stay root-only.
TEST_UID=65534
as_test_user() { python3 -I -S -c 'import os, sys; os.setgroups([]); os.setgid(int(sys.argv[1])); os.setuid(int(sys.argv[1])); os.execvp(sys.argv[2], sys.argv[2:])' "$TEST_UID" "$@"; }
stop_test_user() {
  for _ in 1 2 3; do
    python3 -I -S -c "import os, signal; os.setgroups([]); os.setgid($TEST_UID); os.setuid($TEST_UID); os.kill(-1, signal.SIGKILL)" 2>/dev/null
  done
}
VERIFIER_MODE=$(stat -c %a /logs/verifier)
chmod 700 /tests /logs/verifier

# Reconfigure cmake so any new tests registered in CMakeLists.txt are discovered,
# then build the test executables.
install -m 644 /tests/friction_values.cpp /app/Simbody/tests/CableSpanFrictionValues.cpp
cmake -B /app/out/build -S /app 2>&1 | tee -a "$RUN_LOG"
chown -R "$TEST_UID:$TEST_UID" /app/out/build
(cd /app/out/build && as_test_user cmake --build . --target TestCableSpan TestCableSpan_Forces TestCableSpan_LengthDot TestCableSpanFriction) 2>&1 | tee -a "$RUN_LOG"
(cd /app/out/build && as_test_user cmake --build . --target CableSpanFrictionValues) 2>&1 | tee -a "$RUN_LOG"
stop_test_user
chown -R root:root /app/out/build
chmod -R go-w,o+rX /app/out/build
for t in TestCableSpan TestCableSpan_Forces TestCableSpan_LengthDot TestCableSpanFriction CableSpanFrictionValues; do
  exe=$(find /app/out/build -maxdepth 3 -type f -name "$t" | head -n 1)
  [ -n "$exe" ] || [ "$t" = CableSpanFrictionValues ] || { log "ERROR: test program $t was not built"; echo 0 > /logs/verifier/reward.txt; exit 0; }
  [ -n "$exe" ] || continue
  mv -f "$exe" "$exe.bin"
  cat > "$exe" <<EOF
#!/bin/sh
exec python3 -I -S -c 'import os, sys; os.setgroups([]); os.setgid($TEST_UID); os.setuid($TEST_UID); os.execv(sys.argv[1], sys.argv[1:])' "$exe.bin" "\$@"
EOF
  chmod 755 "$exe"
done

# 1. Existing CableSpan tests
ctest --test-dir /app/out/build -R '^(TestCableSpan|TestCableSpan_Forces|TestCableSpan_LengthDot)$' --output-junit /logs/verifier/base.xml --output-on-failure 2>&1 | tee -a "$RUN_LOG"
stop_test_user

# Canonicalize base.xml: clear classname so testcase names match p2p_node_ids
python3 -I -c '
import xml.etree.ElementTree as ET
try:
    tree = ET.parse("/logs/verifier/base.xml")
    for tc in tree.iter("testcase"):
        tc.attrib["classname"] = ""
    tree.write("/logs/verifier/base.xml")
except Exception as e:
    print(f"base fixup error: {e}")
'

# 2. Capstan friction tests
ctest --test-dir /app/out/build -R '^CableSpanFriction\.' --output-junit /logs/verifier/new.xml --output-on-failure 2>&1 | tee -a "$RUN_LOG"
stop_test_user
# Friction quantities of further configurations, including two-sphere cases offset by a digest of the submitted code, checked after the run.
python3 -I /tests/check_values.py cases /logs/verifier/sphere_cases.txt /app/Simbody/include/simbody/internal/CableSpan.h /app/Simbody/src/CableSpan.cpp 2>&1 | tee -a "$RUN_LOG"
(cd /app/out/build && timeout 600 ./CableSpanFrictionValues) < /logs/verifier/sphere_cases.txt > /logs/verifier/friction_values.out 2>> "$RUN_LOG"
stop_test_user

# Canonicalize new.xml: set classname to CableSpanFriction, name to subtest, and populate failure message
python3 -I -c '
import xml.etree.ElementTree as ET
try:
    tree = ET.parse("/logs/verifier/new.xml")
    for tc in tree.iter("testcase"):
        name = tc.attrib.get("name", "")
        if "." in name:
            cn, nm = name.split(".", 1)
            tc.attrib["classname"] = cn
            tc.attrib["name"] = nm
        fail = tc.find("failure")
        if fail is not None and not fail.attrib.get("message"):
            sysout = tc.find("system-out")
            if sysout is not None and sysout.text:
                lines = [l.strip() for l in sysout.text.strip().splitlines() if "Internal bug detected" in l]
                if lines:
                    fail.attrib["message"] = lines[0]
                else:
                    fail.attrib["message"] = sysout.text.strip().splitlines()[-1]
    tree.write("/logs/verifier/new.xml")
except Exception as e:
    print(f"new fixup error: {e}")
'
python3 -I /tests/check_values.py /logs/verifier/new.xml /logs/verifier/friction_values.out /tests/friction_values.json /logs/verifier/sphere_cases.txt 2>&1 | tee -a "$RUN_LOG"
chmod "$VERIFIER_MODE" /logs/verifier

set -e

# Print the raw logs so a failure can be diagnosed from the verifier output.
_seen=""
for _rl in "$RUN_LOG" /logs/verifier/*_run.log /logs/verifier/*-run.log /logs/verifier/*-mocha.log /logs/verifier/*.log /logs/verifier/*.out; do
  [ -f "$_rl" ] && [ -s "$_rl" ] || continue
  case " $_seen " in *" $_rl "*) continue ;; esac
  case "${_rl##*/}" in *convert*.log|ctrf*.log|junit*.log) continue ;; esac
  _seen="$_seen $_rl"
  echo "===== raw suite output: ${_rl##*/} ====="
  cat "$_rl"
done 2>/dev/null
echo "===== grade ====="

python3 /tests/grader.py grade
log "reward.json=$(cat /logs/verifier/reward.json 2>/dev/null)"

# Keep the reward, ctrf.json and run.log at the top level; move the other reports under reports/.
mkdir -p /logs/verifier/reports 2>/dev/null
for _f in /logs/verifier/*; do
  case "${_f##*/}" in
    reward.json|reward.txt|ctrf.json|run.log|test-stdout.txt|reports) continue ;;
  esac
  [ -f "$_f" ] && mv -f "$_f" /logs/verifier/reports/ 2>/dev/null
done
