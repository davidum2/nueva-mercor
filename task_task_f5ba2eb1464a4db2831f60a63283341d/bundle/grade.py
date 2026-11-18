\
#!/usr/bin/env python3
"""Reward grader with multi-framework, per-test FAIL_TO_PASS enforcement.

reward=1 requires ALL of:
  1. the test command exited 0
  2. the output does not look like "no tests were executed at all"
  3. EVERY FAIL_TO_PASS test is individually OBSERVED, in the framework's own STRUCTURED
     per-test output, as run AND PASSED — pytest/unittest -v, `go test -v`/`-json`, cargo
     libtest/nextest, ctest, `dotnet test` detailed (`Passed <name>`), gradle testLogging,
     and JUnit/xUnit/trx XML (jest-junit, mocha-junit, phpunit --log-junit, gradle
     TEST-*.xml). A required test that is absent (never observed run) or observed only on a
     failing line scores 0.

Design (Fix G, rewardhack/grader verdicts): an agent can forge the process exit code
(os.Exit(0), `|| true`, a rigged in-repo runner, a disabled build) AND forge an aggregate
pass-count / summary line ("2 passing", "Tests run: N, Failures: 0", "Passed! - Failed: 0").
It CANNOT forge the framework emitting a per-test PASS for the exact required test it
suppressed. So reward is driven ONLY by observed per-test outcomes for each configured
FAIL_TO_PASS id. There is deliberately NO aggregate-count fallback, NO synthetic-id
fallback, and NO "name visible on a non-failure line" fallback — every such fallback
accepted a forgeable signal without proving each required test actually ran and passed.
"""
import argparse, json, re, sys

# Terminal color/escape sequences. pytest/jest/cargo/etc emit these when color is forced (e.g.
# --color=yes or a pseudo-TTY), and they sit BETWEEN the node id and its "PASSED"/"ok" marker
# ("<node> \x1b[32mPASSED\x1b[0m"), which would break every per-test regex. Strip before parsing.
_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07|\r")

_ZERO_RUN = re.compile(
    r"no tests ran|no tests to run|no tests found|no test files found"
    r"|collected 0 items|ran 0 tests|0 tests, 0 assertions|Executed 0 of"
    r"|no test specification|Tests:\s+0 |Test Files\s+0 ",
    re.I,
)
_FAIL_MARK = re.compile(r"\bFAILED\b|\bFAILURE\b|\bFAIL\b|\bERRORED\b|✗|✘|not ok", re.I)
# A per-test PASS marker on the SAME line overrides a fail-WORD that is merely part of the test name
# (real test names contain "fail"/"error"/"invalid": e.g. jest/vitest `✓ should support failed bdd
# steps`, mocha `✓ should fail if invalid`, tap `ok 3 - rejects failure`). Without this, a passing
# test whose description contains "fail" is misread as a failure by the lenient heuristic.
_PASS_MARK = re.compile(r"✓|✔|√|\bPASSED\b|\bpassing\b|(?:^|\s)ok\s+\d|\bPASS\b")
_JSON_FALSY_FAIL = re.compile(r'"[^"]*fail[^"]*"\s*:\s*(false|0|\[\]|null|"")', re.I)
# PER-TEST pass marker (jest/vitest/mocha `✓ <title>`, tap `ok N - <desc>`, JUnit `PASSED`). Excludes
# the summary word "passing"/"PASS" so a bare forged summary line ("2 passing (1ms)") is NOT accepted.
_JS_PERTEST = re.compile(r"✓|✔|√|\bPASSED\b|(?:^|\s)ok\s+\d+\b")
_VERBOSE_MARK = re.compile(r"\bPASSED\b|\bFAILED\b|\bXFAIL\b|\bXPASS\b|\.\.\.\s+ok\b|\.\.\.\s+(FAIL|ERROR)\b|✓|✗")

# pytest -v "<node> PASSED" and -rA "PASSED <node>" (case-sensitive: pytest emits UPPERCASE per-test)
_PYTEST = re.compile(
    r"^\s*(\S+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b"
    r"|^\s*(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\s+(\S+::\S+)")
# Go `go test -v`: "--- PASS: TestName (0.00s)" / "--- FAIL:" / "--- SKIP:" (subtests too)
_GO_V = re.compile(r"^\s*--- (PASS|FAIL|SKIP): (\S+)")
# Go `go test -json`: {"Action":"pass|fail|skip",...,"Test":"..."} (either field order)
_GO_JSON_AT = re.compile(r'"Action":"(pass|fail|skip)"[^{}]*?"Test":"([^"]+)"')
_GO_JSON_TA = re.compile(r'"Test":"([^"]+)"[^{}]*?"Action":"(pass|fail|skip)"')
# cargo-nextest: "PASS [   0.0s] pkg module::test" / "FAIL [...]"
_NEXTEST = re.compile(r"^\s*(PASS|FAIL|SKIP)\s+\[[^\]]*\]\s+\S+\s+(\S+)")
# cargo libtest: "test module::test ... ok|FAILED|ignored"
_LIBTEST = re.compile(r"^test\s+(\S+)\s+\.\.\.\s+(ok|FAILED|ignored)\b")
# ctest: "1/2 Test #1: name .......... Passed" / "***Failed" / "***Timeout" / "***Exception"
_CTEST = re.compile(r"Test\s+#\d+:\s+(\S+)\s+\.+\s*(Passed|\*\*\*Failed|\*\*\*Timeout|\*\*\*Exception|\*\*\*Not Run)")
# dotnet `dotnet test` per-test line: "Passed Namespace.Class.Method [12 ms]" (NOT the "Passed! - …"
# summary — the required whitespace after the verb excludes "Passed!"/"Failed!").
_DOTNET_TC = re.compile(r"^\s*(Passed|Failed|Skipped)\s+(\S+)")
# Maven/Gradle surefire aggregate (per test-class) + failing test method lines
_SUREFIRE = re.compile(r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)(?:,\s*Skipped:\s*(\d+))?", re.I)
_MVN_ERRLINE = re.compile(r"^\[ERROR\]\s+(\S+?)[:. ]", re.M)
# JUnit / xUnit XML <testcase> — emitted by gradle (TEST-*.xml catted to stdout), phpunit
# (--log-junit), jest-junit, mocha-junit, dotnet trx-to-junit, etc. A passing case has no
# <failure>/<error> child; <skipped/> is a skip. This is the per-test signal for JVM/JS/PHP
# runners that do NOT print each passing method on stdout, so grade.py can require every
# FAIL_TO_PASS method OBSERVED as passed rather than trusting a forgeable aggregate count.
_JUNIT_TC = re.compile(r'<testcase\b([^>]*?)(?:/>|>(.*?)</testcase\s*>)', re.S | re.I)
# gradle `testLogging { events "passed","failed","skipped" }` per-test line:
#   "com.foo.BarTest > testBaz PASSED"  (also "> testBaz() PASSED")
_GRADLE_TL = re.compile(r"^\s*(\S[^>\n]*?)\s+>\s+(\S[^>\n]*?)\s+(PASSED|FAILED|SKIPPED)\s*$", re.M)


def _xml_attr(attr, s):
    m = re.search(r'\b%s\s*=\s*"([^"]*)"' % attr, s) or re.search(r"\b%s\s*=\s*'([^']*)'" % attr, s)
    return m.group(1) if m else None


_GO = re.compile(r"^(=== RUN|--- (PASS|FAIL|SKIP)|ok\s+\S|FAIL\s+\S|\"Action\":\")", re.M)
_MAVEN = re.compile(r"\bmaven\b|surefire|Tests run:|BUILD SUCCESS|BUILD FAILURE|\[INFO\] Running ", re.I)
# JS/TS runners (jest/vitest/mocha/jasmine/ava/tap/node:test) emit test NAMES as free-text `it()`
# descriptions (spaces, not node ids), so per-test id matching is unreliable — grade on the summary
# aggregate instead: tests must have RUN, none may FAIL, and no F2P may appear on a failing line.
_JS = re.compile(r"\b(jest|vitest|mocha|jasmine|\bava\b|node:test|tap-parser|PHPUnit|rspec)\b"
                 r"|^\s*\d+ (passing|failing)\b|Tests?:\s+\d|Test Files\s+\d|# (pass|fail) \d"
                 r"|^OK \(\d+ tests?|\d+ examples?, \d+ (failure|error)|(Passed|Failed)! - Failed:", re.M | re.I)


def _is_fail_line(ln):
    if _PASS_MARK.search(ln):  # explicit per-test PASS marker -> not a failure (fail-word is in the name)
        return False
    if not _FAIL_MARK.search(ln):
        return False
    return bool(_FAIL_MARK.search(_JSON_FALSY_FAIL.sub("", ln)))


def _norm(name):
    s = re.sub(r"^\(\s*\d+\s*/\s*\d+\s*\)\s*", "", str(name)).strip()
    # strip a trailing empty arg-list so a JVM F2P id `Cls::testFoo()` matches the XML `name="testFoo"`
    s = re.sub(r"\(\s*\)$", "", s).strip()
    return s


def _tokens(name):
    n = _norm(name)
    toks = []
    if n:
        toks.append(n)
        last = n.split("::")[-1].strip()
        if last and last != n:
            toks.append(last)
        tail = last.split()[-1] if last.split() else last
        if tail and tail not in toks:
            toks.append(tail)
    return [t for t in toks if len(t) >= 4]


def _json_unescape(s):
    """Decode JSON string escapes in a `go test -json` Test field: Go escapes `<`/`>`/`&` as
    \\u003c/\\u003e/\\u0026, so the raw regex capture (`factor_of_\\u003c=_1`) will not match a
    FAIL_TO_PASS id that carries the literal `<=`. Decoding restores the real subtest name."""
    if "\\" not in s:
        return s
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s


def parse_outcomes(output, lines):
    """{test-identifier: PASSED|FAILED|ERROR|SKIPPED} across all recognized frameworks."""
    node = {}

    def put(k, v, override=True):
        if not k:
            return
        if override or k not in node:
            node[k] = v

    for ln in lines:
        m = _PYTEST.match(ln)
        if m:
            put(m.group(1) or m.group(4), (m.group(2) or m.group(3)).upper())
        m = _GO_V.match(ln)
        if m:
            put(m.group(2), {"PASS": "PASSED", "FAIL": "FAILED", "SKIP": "SKIPPED"}[m.group(1)])
        m = _NEXTEST.match(ln)
        if m:
            put(m.group(2), {"PASS": "PASSED", "FAIL": "FAILED", "SKIP": "SKIPPED"}[m.group(1)])
        m = _LIBTEST.match(ln)
        if m:
            put(m.group(1), {"ok": "PASSED", "FAILED": "FAILED", "ignored": "SKIPPED"}[m.group(2)])
        m = _DOTNET_TC.match(ln)
        if m:
            put(m.group(2), {"Passed": "PASSED", "Failed": "FAILED", "Skipped": "SKIPPED"}[m.group(1)])
    for m in _GO_JSON_AT.finditer(output):
        put(_json_unescape(m.group(2)), {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"}[m.group(1)])
    for m in _GO_JSON_TA.finditer(output):
        put(_json_unescape(m.group(1)), {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"}[m.group(2)], override=False)
    for m in _CTEST.finditer(output):
        put(m.group(1), "PASSED" if m.group(2) == "Passed" else "FAILED")
    # gradle testLogging per-test lines ("Class > method PASSED")
    for m in _GRADLE_TL.finditer(output):
        cls, meth = m.group(1).strip(), re.sub(r"\(\s*\)$", "", m.group(2).strip())
        oc = {"PASSED": "PASSED", "FAILED": "FAILED", "SKIPPED": "SKIPPED"}[m.group(3)]
        put(cls + "::" + meth, oc)
        put(meth, oc, override=False)
    # JUnit / xUnit <testcase> elements (gradle TEST-*.xml, phpunit --log-junit, jest/mocha-junit, trx)
    for m in _JUNIT_TC.finditer(output):
        attrs, body = m.group(1), (m.group(2) or "")
        nm = _xml_attr("name", attrs)
        if not nm:
            continue
        nm = re.sub(r"\(\s*\)$", "", nm.strip())
        cls = _xml_attr("classname", attrs) or _xml_attr("class", attrs)
        if re.search(r"<(failure|error)\b", body, re.I):
            oc = "FAILED"
        elif re.search(r"<skipped\b", body, re.I):
            oc = "SKIPPED"
        else:
            oc = "PASSED"
        if cls:
            put(cls + "::" + nm, oc)
        put(nm, oc, override=False)
    return node


def _f2p_candidates(name, node_outcome):
    """Nodes whose last identifier segment == the F2P's last segment (exact, not substring)."""
    segs = [s for s in re.split(r"::|\.|\s|#|/", _norm(name)) if s]
    tname = segs[-1] if segs else ""
    if not tname:
        return []
    out = []
    for nd in node_outcome:
        nsegs = [s for s in re.split(r"::|\.|#|/", nd) if s]
        if nsegs and nsegs[-1] == tname:
            out.append(nd)
    return out


def _strict_pertest_ok(f2p, node_outcome):
    """Fix G: every configured FAIL_TO_PASS test must be OBSERVED — via the framework's STRUCTURED
    per-test output (parse_outcomes) — as run AND PASSED. A test with no matching per-test outcome
    (never observed run) or whose matching outcome is not PASSED => reward 0. There is deliberately
    NO "name visible on a non-failure line" fallback: a bare grep-visible name is not proof the
    framework executed that test and reported it PASSED."""
    for name in f2p:
        cands = _f2p_candidates(name, node_outcome)
        if not cands or not any(node_outcome[c] == "PASSED" for c in cands):
            return False
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stdout", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--exit-code", type=int, required=True)
    p.add_argument("--reward-out", required=True)
    args = p.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    f2p = config.get("FAIL_TO_PASS", []) or []
    with open(args.stdout, errors="replace") as f:
        output = _ANSI.sub("", f.read())
    lines = output.splitlines()

    reward = 1 if args.exit_code == 0 else 0

    if reward == 1 and _ZERO_RUN.search(output):
        reward = 0

    if reward == 1 and f2p:
        # Fix G (rewardhack/grader verdicts): reward ONLY when EVERY configured FAIL_TO_PASS test is
        # individually OBSERVED, in the framework's STRUCTURED per-test output, as run AND PASSED.
        # parse_outcomes() extracts per-test verdicts from every framework whose output carries a
        # structured per-test signal — pytest/unittest -v, `go test -v`/`-json`, cargo libtest/nextest,
        # ctest, `dotnet test` detailed (`Passed <name>`), gradle testLogging, and JUnit/xUnit/trx XML
        # (jest-junit, mocha-junit, phpunit --log-junit, gradle TEST-*.xml). The converter side
        # (force_perframework_verbose) forces each runner to emit that per-test signal.
        #
        # There is deliberately NO fallback:
        #   * NO aggregate pass-count (old _js_aggregate / _jvm_aggregate) — a forged "N passing" /
        #     "Tests run: N, Failures: 0" / "Passed! - Failed: 0" summary no longer scores 1;
        #   * NO synthetic-id fallback (old f2p_synthetic) — a converter placeholder id that carries
        #     no observable per-test signal cannot be enforced, so it must fail closed, not aggregate;
        #   * NO "name visible on a non-failure line" fallback (old _names_observed_ok / _lenient_ok) —
        #     a grep-visible name is not proof the framework ran that test and reported it PASSED.
        # If a task's real suite genuinely cannot emit a structured per-test signal offline, the task
        # must be DROPPED at convert time, never graded by a forgeable aggregate.
        node_outcome = parse_outcomes(output, lines)
        if not node_outcome or not _strict_pertest_ok(f2p, node_outcome):
            reward = 0

    # COLLECTED-BUT-NOT-EXECUTED guard (pytest): "collected N items" but zero tests actually ran.
    # Gate strictly on the pytest collection marker so it never misfires on another framework whose
    # node ids merely contain "::" (e.g. cargo-nextest emits `PASS [t] crate mod::test`, not PASSED).
    # Any parsed per-test outcome (pytest/go/rust/ctest) counts as executed.
    if reward == 1 and f2p:
        pytest_collected = bool(re.search(r"collected\s+\d+\s+item", output))
        executed = bool(parse_outcomes(output, lines)) or any(_VERBOSE_MARK.search(ln) for ln in lines)
        if pytest_collected and not executed:
            reward = 0

    with open(args.reward_out, "w") as f:
        f.write(str(reward) + "\n")


if __name__ == "__main__":
    main()
