from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import subprocess
import traceback
from .config import load_config
from .io import RoundLock, write_json


def main():
    parser = argparse.ArgumentParser(description="SynAP development search and separately frozen final evaluation")
    parser.add_argument("command", choices=["audit", "smoke", "search", "confirm", "freeze", "final-test", "report", "run-all"])
    parser.add_argument("--config")
    parser.add_argument("--manifest")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.command == "final-test" and not args.manifest:
        parser.error("final-test requires --manifest from a successful freeze")
    if args.command not in {"final-test", "report"} and not args.config:
        parser.error("--config is required")
    if args.command == "report" and not (args.manifest or args.config):
        parser.error("report requires --manifest or --config for pending status")
    config = load_config(args.config) if args.config else None
    output = Path(config["data"]["output"]) if config else Path(args.manifest).resolve().parent
    if args.command == "run-all":
        # Each stage is a separate process. Audit/test rows never enter search memory.
        frozen=output / "FINAL_MANIFEST.json"
        stages=[]
        if not frozen.exists():
            if not (output / "DATA_AUDIT.json").exists():
                stages.append(["audit","--config",args.config])
            if not (output / "ROUND_LOCK.json").exists():
                stages.append(["smoke","--config",args.config])
            stages += [["search","--config",args.config]+(["--resume"] if args.resume else []),
                       ["confirm","--config",args.config],["freeze","--config",args.config]]
        for stage in stages:
            completed=subprocess.run([sys.executable,"-u","-m","synap_search",*stage],check=False)
            if completed.returncode:
                return completed.returncode
        if not frozen.is_file():
            raise RuntimeError("Freeze returned without a manifest")
        for stage in ("final-test","report"):
            completed=subprocess.run([sys.executable,"-u","-m","synap_search",stage,"--manifest",str(frozen)],check=False)
            if completed.returncode:
                return completed.returncode
        return 0
    with RoundLock(output):
        try:
            if args.command == "audit":
                from .audit import audit
                result = audit(config)
            elif args.command == "smoke":
                from .smoke import smoke
                result = smoke(config)
            elif args.command in {"search", "confirm"}:
                from .search import search, confirm
                result = search(config, args.resume) if args.command == "search" else confirm(config)
            elif args.command == "freeze":
                from .finalize import freeze
                result = freeze(config)
            elif args.command == "final-test":
                from .finalize import final_test
                result = final_test(args.manifest)
            elif args.command == "report":
                from .finalize import report
                result = report(args.manifest, config)
            write_json(output / "LAST_COMMAND.json", {"command": args.command, "status": "RETURNED", "result": result})
            print(json.dumps(result, ensure_ascii=True, indent=2))
            return 0 if result.get("status") not in {"BLOCKED", "NO_FEASIBLE_CANDIDATE"} else 2
        except Exception as exc:
            write_json(output / "LAST_COMMAND.json", {"command": args.command, "status": "FAILED", "type": type(exc).__name__, "error": str(exc)})
            traceback.print_exc()
            return 2


if __name__ == "__main__":
    sys.exit(main())
