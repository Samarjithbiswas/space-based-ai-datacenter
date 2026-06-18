"""
One-command reproduction of every result in this repository.

    python reproduce_all.py

Runs, in order:
  1. systems-model  : validate.py  ->  pytest  ->  run_study.py (figures)
  2. survivability  : validate.py  ->  survivability.py (figures)
  3. report         : sim_survivability.py (report figures) + equation images

Prints a PASS/FAIL summary and exits non-zero if anything fails. Requires only
numpy + matplotlib (pytest optional). No network, no data files, no GPU.
"""
import subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
STEPS = [
    ("systems-model: validation", "systems-model", [PY, "validate.py"]),
    ("systems-model: pytest",      "systems-model", [PY, "-m", "pytest", "-q"]),
    ("systems-model: full study",  "systems-model", [PY, "run_study.py"]),
    ("survivability: validation",  "survivability-model", [PY, "validate.py"]),
    ("survivability: figures",     "survivability-model", [PY, "survivability.py"]),
    ("report: figures",            "report", [PY, "sim_survivability.py"]),
    ("report: equation images",    "report", [PY, "make_equation_images.py"]),
]


def main():
    results = []
    for label, cwd, cmd in STEPS:
        path = ROOT / cwd
        print(f"\n=== {label}  ({cwd}) ===")
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=path, capture_output=True, text=True, timeout=900)
            ok = r.returncode == 0
            tail = (r.stdout or r.stderr).strip().splitlines()[-3:]
            for ln in tail:
                print("   " + ln)
        except Exception as e:                       # noqa
            ok = False
            print("   ERROR:", e)
        results.append((label, ok, time.time() - t0))

    print("\n" + "=" * 64)
    print(" REPRODUCTION SUMMARY")
    print("=" * 64)
    for label, ok, dt in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:34s} {dt:5.1f}s")
    n_ok = sum(1 for _, ok, _ in results if ok)
    print("=" * 64)
    print(f"  {n_ok}/{len(results)} steps passed.")
    sys.exit(0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    main()
