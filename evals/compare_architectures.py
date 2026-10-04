from __future__ import annotations

import csv
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(architecture: str) -> list[dict]:
    cmd = [sys.executable, str(ROOT / "evals" / "run_public_evals.py"), "--architecture", architecture]
    subprocess.run(cmd, cwd=ROOT, check=True)
    path = ROOT / "evals" / f"results_{architecture}.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    all_rows = {a: run(a) for a in ("single", "staged")}
    print("\nArchitecture comparison\n")
    print("| Metric | Single | Staged |")
    print("|---|---:|---:|")
    for metric, fn in [
        ("Cases passing", lambda rows: sum(r["passed_minimum_checks"] == "True" for r in rows)),
        ("Avg latency (ms)", lambda rows: round(statistics.mean(float(r["latency_ms"]) for r in rows), 1)),
        ("Avg LLM calls", lambda rows: round(statistics.mean(float(r["llm_calls"] or 0) for r in rows), 2)),
        ("Avg tool calls", lambda rows: round(statistics.mean(float(r["tool_calls"] or 0) for r in rows), 2)),
    ]:
        print(f"| {metric} | {fn(all_rows['single'])} | {fn(all_rows['staged'])} |")

    out = ROOT / "evals" / "architecture_comparison.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "single", "staged"])
        writer.writerow(["cases_passing", sum(r["passed_minimum_checks"] == "True" for r in all_rows["single"]), sum(r["passed_minimum_checks"] == "True" for r in all_rows["staged"])])
        writer.writerow(["avg_latency_ms", statistics.mean(float(r["latency_ms"]) for r in all_rows["single"]), statistics.mean(float(r["latency_ms"]) for r in all_rows["staged"])])
        writer.writerow(["avg_llm_calls", statistics.mean(float(r["llm_calls"] or 0) for r in all_rows["single"]), statistics.mean(float(r["llm_calls"] or 0) for r in all_rows["staged"])])
        writer.writerow(["avg_tool_calls", statistics.mean(float(r["tool_calls"] or 0) for r in all_rows["single"]), statistics.mean(float(r["tool_calls"] or 0) for r in all_rows["staged"])])
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
