"""CLI narrator for the demo. Run `python -m demo.run` to print the story.

Use this live on stage if you want a terminal-only version, or as a smoke test
before the workshop.
"""

from __future__ import annotations

import sys

from .scenario import run

RED = "\033[91m"
GREEN = "\033[92m"
YEL = "\033[93m"
DIM = "\033[2m"
BOLD = "\033[1m"
END = "\033[0m"


def _sev(sev: str, allowed: bool) -> str:
    if allowed and sev == "info":
        return f"{GREEN}ALLOWED{END}"
    return f"{RED}BLOCKED{END}"


def narrate(mode_enabled: bool) -> None:
    title = "CONTROLS ON  (IBM Verify + ARS-style enforcement)" if mode_enabled else "CONTROLS OFF  (no runtime identity fabric)"
    color = GREEN if mode_enabled else RED
    print(f"\n{color}{BOLD}{'='*68}{END}")
    print(f"{color}{BOLD}  {title}{END}")
    print(f"{color}{BOLD}{'='*68}{END}\n")

    result = run(mode_enabled)
    for i, s in enumerate(result["steps"], 1):
        print(f"{BOLD}[{i}] {s['agent']}{END}")
        print(f"    {DIM}{s['narration']}{END}")
        verdict = _sev(s["severity"], s["allowed"])
        print(f"    -> {verdict}  {DIM}({s['control']}){END}")
        print(f"       {s['reason']}")
        print()

    snap = result["snapshot"]
    print(f"{BOLD}Outcome:{END}")
    print(f"    Customer records exposed : {snap['records_exposed']}")
    print(f"    Money moved to ACC-7777  : ${snap['moved']:,.2f}")
    print(f"    Actions blocked          : {result['blocked']} / {result['blocked'] + result['allowed']}")
    mule = next(a for a in snap["accounts"] if a["id"] == "ACC-7777")
    print(f"    Mule account balance     : ${mule['balance']:,.2f}")
    print()


def main() -> int:
    narrate(False)
    narrate(True)
    print(f"{BOLD}The same three agents. The same instructions. One control plane between them and the money.{END}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
