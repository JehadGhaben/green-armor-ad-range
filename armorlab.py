#!/usr/bin/env python3
"""GREEN ARMOR Directory Range -- dependency-free student/instructor CLI."""
from __future__ import annotations

import argparse
import hmac
import json
import os
import secrets
import shutil
import string
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
STATE_FILE = RUNTIME / "state.json"
SEED_FILE = RUNTIME / "seed" / "scenario.json"
PROGRESS_FILE = RUNTIME / "progress.json"
DOMAIN = "ARMOR.TEST"
NETBIOS = "ARMOR"
STUDENT_NAME = "student01"
STUDENT_PASS = "GreenArmor2026!"
STAGES = (
    ("01", "Network & SMB discovery", 15),
    ("02", "LDAP directory enumeration", 20),
    ("03", "Exposed service credentials", 25),
    ("04", "Unauthorized archive access", 40),
)
HINTS = {
    "01": (
        "Identify the DNS and SMB services offered by the DC.",
        "Try smbclient against dc and enumerate the visible shares.",
        "Read START-HERE.txt in GA-Public with your initial student account.",
    ),
    "02": (
        "Directory users have attributes besides their usernames.",
        "Authenticate to LDAP and inspect descriptive attributes of service accounts.",
        "Look at svc_backup's description in the directory.",
    ),
    "03": (
        "Teams sometimes accidentally archive integration credentials in shared folders.",
        "Explore the IT/ directory within the general share.",
        "Inspect the legacy integration configuration and identify the exposure token.",
    ),
    "04": (
        "Reusing a leaked service credential can broaden access to file shares.",
        "List SMB shares as the discovered service account, then compare access.",
        "Inspect the reports directory of GA-Archive.",
    ),
}


def color(text: str, ansi: str) -> str:
    if os.environ.get("NO_COLOR") is not None or not sys.stdout.isatty():
        return text
    return f"\033[{ansi}m{text}\033[0m"


def banner() -> None:
    print(color("\n  GREEN ARMOR  |  DIRECTORY RANGE", "1;32"))
    print(color("  OPERATIVE ENVIRONMENT: ARMOR.TEST  ·  JEHAD GHABEN", "2"))
    print("  " + "─" * 54)


def password(length: int = 22) -> str:
    alphabet = string.ascii_letters + string.digits
    return "G!a7" + "".join(secrets.choice(alphabet) for _ in range(length - 4))


def new_state() -> dict:
    return {
        "schema": 1,
        "domain": DOMAIN,
        "admin_password": password(26),
        "service_password": password(),
        "flags": {
            stage: f"GA{{{stage}-{secrets.token_hex(8).upper()}}}"
            for stage, _, _ in STAGES
        },
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ValueError(f"Invalid JSON object in {path.name}")
    return value


def ensure_state() -> dict:
    if STATE_FILE.exists():
        state = read_json(STATE_FILE)
    else:
        state = new_state()
        write_json(STATE_FILE, state)
        write_json(PROGRESS_FILE, {"solved": []})
    if not SEED_FILE.exists():
        write_json(SEED_FILE, state)
    return state


def require_docker() -> bool:
    for args in (("docker", "--version"), ("docker", "compose", "version"), ("docker", "info")):
        try:
            result = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except FileNotFoundError:
            print("[!] Docker is not installed or unavailable in PATH.")
            return False
        if result.returncode:
            print("[!] Docker or Compose is unavailable, or the Docker daemon is not running.")
            return False
    return True


def compose(*args: str) -> int:
    return subprocess.call(["docker", "compose", "-f", str(ROOT / "compose.yaml"), *args], cwd=ROOT)


def command_up(_args: argparse.Namespace) -> int:
    if not require_docker():
        return 2
    state = ensure_state()
    print("[+] Building and starting the isolated directory range...")
    code = compose("up", "--build", "-d", "--wait")
    if code:
        print("[!] Startup failed. Run: python3 armorlab.py logs")
        return code
    print(color("[+] Lab started.", "32"))
    print(f"[i] Domain: {state['domain']} | Client: student / DC: dc")
    print(f"[i] Initial user: {NETBIOS}\\{STUDENT_NAME} | Password: {STUDENT_PASS}")
    print("[i] Enter shell: python3 armorlab.py shell")
    return 0


def command_down(_args: argparse.Namespace) -> int:
    if not require_docker():
        return 2
    return compose("down")


def command_reset(args: argparse.Namespace) -> int:
    if not args.yes:
        print("[!] This DESTROYS ALL range data, flags, progress, and the AD volume.")
        print("    Re-run with --yes to confirm.")
        return 2
    if not require_docker():
        return 2
    result = compose("down", "--volumes", "--remove-orphans")
    if result:
        print("[!] Docker teardown failed; not deleting runtime data.")
        return result
    shutil.rmtree(RUNTIME, ignore_errors=True)
    print("[+] Range fully reset. A new deployment will generate new flags.")
    return 0


def command_info(_args: argparse.Namespace) -> int:
    print("[i] Lab: Operation Directory — Entry-Level AD Security Assessment")
    print(f"[i] Domain: {DOMAIN} | NetBIOS: {NETBIOS} | DC hostname: dc")
    print(f"[i] Initial student credential: {NETBIOS}\\{STUDENT_NAME} / {STUDENT_PASS}")
    print("[i] One Samba AD DC, one isolated Linux student toolbox, no published ports.")
    print("[i] Example from client: smbclient -L //dc -U 'ARMOR\\student01'")
    print("[i] Example DNS: dig @dc _ldap._tcp.armor.test SRV")
    print("[i] Example LDAP: ldapsearch -x -H ldap://dc -D 'student01@armor.test' -W -b 'DC=armor,DC=test' '(objectClass=user)' sAMAccountName description")
    for key, title, score in STAGES:
        print(f"    [{key}] {title}: {score} points")
    return 0


def command_status(_args: argparse.Namespace) -> int:
    print("[i] Local state:", "initialized" if STATE_FILE.exists() else "not initialized")
    if not require_docker():
        return 2
    return compose("ps")


def command_shell(_args: argparse.Namespace) -> int:
    if not require_docker():
        return 2
    return compose("exec", "student", "bash")


def command_logs(args: argparse.Namespace) -> int:
    if not require_docker():
        return 2
    return compose("logs", "--tail", str(args.tail), "dc")


def command_submit(args: argparse.Namespace) -> int:
    if not STATE_FILE.exists():
        print("[!] Start the lab first: python3 armorlab.py up")
        return 2
    submitted = args.flag.strip()
    state = read_json(STATE_FILE)
    progress = read_json(PROGRESS_FILE) if PROGRESS_FILE.exists() else {"solved": []}
    solved = set(progress.get("solved", []))
    for key, name, score in STAGES:
        if hmac.compare_digest(submitted, state["flags"][key]):
            if key in solved:
                print(f"[i] Stage {key} already completed ({score} points).")
            else:
                solved.add(key)
                write_json(PROGRESS_FILE, {"solved": sorted(solved)})
                print(color(f"[+] Correct! Stage {key} completed: {name} (+{score} points)", "32"))
            return 0
    print("[-] Invalid flag. Check the exact GA{...} value.")
    return 1


def command_score(args: argparse.Namespace) -> int:
    progress = read_json(PROGRESS_FILE) if PROGRESS_FILE.exists() else {"solved": []}
    solved = set(progress.get("solved", []))
    rows = [{"stage": key, "title": title, "points": score, "solved": key in solved}
            for key, title, score in STAGES]
    total = sum(item["points"] for item in rows if item["solved"])
    if args.json:
        print(json.dumps({"earned": total, "total": 100, "stages": rows}, indent=2))
    else:
        for item in rows:
            check = "PASS" if item["solved"] else "----"
            print(f"  [{check}] {item['stage']}  {item['title']:<36} {item['points']:>2} pts")
        print(f"\n  TOTAL  {total}/100 points")
    return 0


def command_hint(args: argparse.Namespace) -> int:
    if args.stage not in HINTS:
        print("[!] Unknown stage. Available stages: 01 02 03 04")
        return 2
    index = args.level - 1
    print(f"[HINT {args.stage}.{args.level}] {HINTS[args.stage][index]}")
    return 0


def command_doctor(_args: argparse.Namespace) -> int:
    print(f"[+] Python: {sys.version.split()[0]}")
    try:
        engine = subprocess.run(["docker", "--version"], capture_output=True,
                                text=True, check=False).stdout.strip()
        if "podman" in engine.lower():
            print("[!] This 'docker' command is Podman. Docker Engine is recommended; Podman is not CI-verified.")
    except FileNotFoundError:
        pass
    print(f"[+] compose.yaml: {'found' if (ROOT / 'compose.yaml').exists() else 'MISSING'}")
    print(f"[+] DC Dockerfile: {'found' if (ROOT / 'docker/dc/Dockerfile').exists() else 'MISSING'}")
    print(f"[+] Runtime state: {'initialized' if STATE_FILE.exists() else 'will be generated at up'}")
    ok = require_docker()
    print(f"[{'+' if ok else '!'}] Docker Engine and Compose: {'ready' if ok else 'not ready'}")
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GREEN ARMOR ACADEMY · Operation Directory Range")
    commands = parser.add_subparsers(dest="cmd", required=True)
    for cmd, handler, help_text in (
        ("up", command_up, "Build and launch the isolated lab"),
        ("down", command_down, "Stop lab without losing progress"),
        ("info", command_info, "Show targets, tasks and initial credentials"),
        ("status", command_status, "Show container status"),
        ("shell", command_shell, "Enter student's Linux toolbox"),
        ("doctor", command_doctor, "Validate local prerequisites"),
    ):
        child = commands.add_parser(cmd, help=help_text)
        child.set_defaults(handler=handler)
    child = commands.add_parser("reset", help="Delete lab volumes and rotate all flags")
    child.add_argument("--yes", action="store_true", help="Confirm irreversible deletion")
    child.set_defaults(handler=command_reset)
    child = commands.add_parser("logs", help="Show DC startup logs")
    child.add_argument("--tail", type=int, default=80)
    child.set_defaults(handler=command_logs)
    child = commands.add_parser("submit", help="Submit a discovered GA{...} flag")
    child.add_argument("flag")
    child.set_defaults(handler=command_submit)
    child = commands.add_parser("score", help="Display stage completion and total score")
    child.add_argument("--json", action="store_true", help="Machine-readable grading summary")
    child.set_defaults(handler=command_score)
    child = commands.add_parser("hint", help="Progressive hint per stage")
    child.add_argument("stage", choices=tuple(HINTS))
    child.add_argument("level", type=int, choices=(1, 2, 3))
    child.set_defaults(handler=command_hint)
    args = parser.parse_args(argv)
    banner()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
