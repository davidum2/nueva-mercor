"""Compare the printed friction quantities with the reference values and fail the matching subtests in new.xml.

Usage: check_values.py cases <cases file> <source file>...
       check_values.py <new.xml> <values output> <reference json> <cases file>
Reference entries: "<subtest>.<name>": [[values...], relative tolerance].
The cases file holds two-sphere configurations from a fixed seed, offset slightly by a digest of the submitted
sources with comments and whitespace removed; their quantities are compared with the capstan solution on the solved path, and a mismatch fails every friction subtest.
"""
import hashlib
import json
import math
import os
import random
import re
import sys
import xml.etree.ElementTree as ET


def read_values(path):
    seen, values = set(), {}
    try:
        with open(path, errors="replace") as f:
            lines = f.read(1 << 20).splitlines()
    except OSError:
        lines = []
    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            continue
        name = parts[0]
        try:
            nums = [float(p) for p in parts[1:]]
        except ValueError:
            continue
        if name in seen:
            values.pop(name, None)
            continue
        seen.add(name)
        values[name] = nums
    return values


def mismatch(got, want, tol):
    if got is None:
        return "missing"
    if len(got) != len(want):
        return f"got {len(got)} numbers, expected {len(want)}"
    scale = max(1.0, max(abs(w) for w in want))
    for g, w in zip(got, want):
        if not math.isfinite(g) or abs(g - w) > tol * scale:
            return f"got {got}, expected {want}"
    return None


CASE_TOL = 2e-5
# Sphere centres, origin and termination in a case line.
OFFSET_INDICES = (1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13)
CODE_TOKENS = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|//[^\n]*|/\*.*?\*/', re.S)


def write_cases(path, sources):
    digest = hashlib.sha256()
    for src in sources:
        if os.path.isfile(src) and not os.path.islink(src):
            with open(src, "rb") as f:
                code = f.read(1 << 24).decode("utf-8", "replace")
            code = CODE_TOKENS.sub(lambda m: m.group(0) if m.group(0)[0] in "\"'" else " ", code)
            digest.update("".join(code.split()).encode())
    rng = random.Random("two-sphere cases")
    jitter = random.Random(digest.hexdigest())
    print(f"sphere case offset seed: {digest.hexdigest()}")
    lines = []
    for name, speed in (("spheres_lengthening", 10 ** rng.uniform(1.0, 3.0)),
                        ("spheres_shortening", -(10 ** rng.uniform(-3.0, -1.0))),
                        ("spheres_static", 0.0)):
        while True:
            base = []
            for cx in (rng.uniform(0.8, 1.2), rng.uniform(3.0, 3.5)):
                r = rng.uniform(0.6, 0.85)
                base += [r, cx, -r * rng.uniform(0.3, 0.6), rng.uniform(-0.3, 0.3)]
            base += [rng.uniform(-1.6, -1.0), rng.uniform(-0.1, 0.2), rng.uniform(-0.4, 0.4)]
            base += [rng.uniform(5.2, 6.0), rng.uniform(-0.1, 0.2), rng.uniform(-0.4, 0.4)]
            base += [rng.uniform(0.1, 0.9), rng.uniform(0.1, 0.9), speed, 0.0, 0.0, 0.0, rng.uniform(2.0, 12.0)]
            sol = spheres_solution(base)
            if sol and min(sol["theta0"][0], sol["theta1"][0]) > 0.15:
                break
        for _ in range(100):
            case = [v + (jitter.uniform(-0.02, 0.02) if i in OFFSET_INDICES else 0.0) for i, v in enumerate(base)]
            case[20] *= jitter.uniform(0.98, 1.02)
            sol = spheres_solution(case)
            if sol and min(sol["theta0"][0], sol["theta1"][0]) > 0.1:
                break
        else:
            case, sol = base, spheres_solution(base)
        case[17:20] = sol["t_exit"]
        lines.append(" ".join([name] + [repr(v) for v in case]))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def read_cases(path):
    cases = {}
    try:
        with open(path) as f:
            for line in f:
                parts = line.split()
                cases[parts[0]] = [float(p) for p in parts[1:]]
    except (OSError, ValueError, IndexError):
        return {}
    return cases


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def unit(a):
    n = math.sqrt(dot(a, a))
    return [x / n for x in a]


def solve(m, v):
    """Gaussian elimination with partial pivoting."""
    n = len(v)
    a = [row[:] + [v[i]] for i, row in enumerate(m)]
    for i in range(n):
        p = max(range(i, n), key=lambda k: abs(a[k][i]))
        a[i], a[p] = a[p], a[i]
        for k in range(i + 1, n):
            f = a[k][i] / a[i][i]
            a[k] = [x - f * y for x, y in zip(a[k], a[i])]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (a[i][n] - sum(a[i][k] * x[k] for k in range(i + 1, n))) / a[i][i]
    return x


def wrap(center, r, axis, point, toward):
    """Contact point where the line from point touches the great circle about axis, travelling in the axis sense."""
    e = unit(sub(point, center))
    g = math.acos(r / math.sqrt(dot(sub(point, center), sub(point, center))))
    side = cross(axis, e)
    for sgn in (1.0, -1.0):
        ec = [math.cos(g) * x + sgn * math.sin(g) * y for x, y in zip(e, side)]
        k = [c + r * x for c, x in zip(center, ec)]
        if dot(cross(axis, ec), sub(k, point) if toward else sub(point, k)) > 0:
            return k, ec


def spheres_solution(case):
    """Path from origin over two spheres to termination (great-circle arcs joined by tangent lines), and its friction quantities."""
    try:
        return solve_spheres(case)
    except (ArithmeticError, ValueError, TypeError, IndexError):
        return None


def solve_spheres(case):
    r1, c1, r2, c2 = case[0], case[1:4], case[4], case[5:8]
    p, q, mu1, mu2, speed, t0 = case[8:11], case[11:14], case[14], case[15], case[16], case[20]

    def points(x):
        return ([c + r1 * u for c, u in zip(c1, (math.cos(x[1]) * math.cos(x[0]), math.cos(x[1]) * math.sin(x[0]), math.sin(x[1])))],
                [c + r2 * u for c, u in zip(c2, (math.cos(x[3]) * math.cos(x[2]), math.cos(x[3]) * math.sin(x[2]), math.sin(x[3])))])

    def residual(x):
        b, c = points(x)
        bc = unit(sub(c, b))
        return [dot(bc, sub(b, c1)) / r1, dot(bc, sub(c, c2)) / r2,
                dot(cross(unit(sub(p, c1)), sub(b, c1)), bc) / r1, dot(cross(unit(sub(q, c2)), sub(c, c2)), bc) / r2]

    x = [math.pi / 2, 0.0, math.pi / 2, 0.0]
    for _ in range(60):
        f = residual(x)
        if max(abs(v) for v in f) < 1e-14:
            break
        jac = []
        for j in range(4):
            xh = x[:]
            xh[j] += 1e-7
            jac.append([(a - b) / 1e-7 for a, b in zip(residual(xh), f)])
        dx = solve([[jac[j][i] for j in range(4)] for i in range(4)], [-v for v in f])
        x = [a + b for a, b in zip(x, dx)]
    if max(abs(v) for v in residual(x)) > 1e-12:
        return None
    b, c = points(x)
    t_bc = unit(sub(c, b))
    e_b, e_c = unit(sub(b, c1)), unit(sub(c, c2))
    if min(e_b[1], e_c[1]) < 0.2:
        return None
    w1, w2 = cross(e_b, t_bc), cross(e_c, t_bc)
    a, e_a = wrap(c1, r1, w1, p, True)
    d, e_d = wrap(c2, r2, w2, q, False)
    theta1 = math.atan2(dot(cross(e_a, e_b), w1), dot(e_a, e_b))
    theta2 = math.atan2(dot(cross(e_c, e_d), w2), dot(e_c, e_d))
    t_in, t_out = unit(sub(a, p)), unit(sub(q, d))
    gain = (lambda mu, th: math.exp(math.copysign(mu * th, speed))) if speed != 0 else (lambda mu, th: 1.0)
    t1 = t0 * gain(mu1, theta1)
    t2 = t1 * gain(mu2, theta2)

    def wrench(r_in, f_in, r_out, f_out):
        return sub(cross(r_out, f_out), cross(r_in, f_in)) + sub(f_out, f_in)

    return {
        "theta0": [theta1],
        "theta1": [theta2],
        "Tterm": [t2],
        "power": [speed * (t2 - t0)],
        "origin": [0.0, 0.0, 0.0] + [t0 * v for v in t_in],
        "obstacle0": wrench(a, [t0 * v for v in t_in], b, [t1 * v for v in t_bc]),
        "obstacle1": wrench(c, [t1 * v for v in t_bc], d, [t2 * v for v in t_out]),
        "termination": [0.0, 0.0, 0.0] + [-t2 * v for v in t_out],
        "t_exit": t_out,
    }


def main(junit, output, reference, cases_path):
    with open(reference) as f:
        ref = json.load(f)
    values = read_values(output)
    failed = {}
    for name, (want, tol) in ref.items():
        why = mismatch(values.get(name), want, tol)
        if why:
            failed.setdefault(name.split(".", 1)[0], f"{name}: {why}")
    cases = read_cases(cases_path)
    case_failure = None if cases else "no two-sphere cases"
    for case, params in cases.items():
        print(f"{case}: {' '.join(repr(v) for v in params)}")
        for name, want in (spheres_solution(params) or {"path": [math.nan]}).items():
            if name == "t_exit":
                continue
            why = mismatch(values.get(f"{case}.{name}"), want, CASE_TOL)
            if why and case_failure is None:
                case_failure = f"{case}.{name}: {why}"
    tree = ET.parse(junit)
    for tc in tree.iter("testcase"):
        msg = failed.get(tc.attrib.get("name", ""), case_failure)
        if msg is None:
            continue
        print(f"value check failed for {tc.attrib['name']}: {msg}")
        if tc.find("failure") is None and tc.find("error") is None:
            ET.SubElement(tc, "failure", {"message": f"value check: {msg}"})
    tree.write(junit)


if __name__ == "__main__":
    if sys.argv[1] == "cases":
        write_cases(sys.argv[2], sys.argv[3:])
    else:
        main(*sys.argv[1:5])
