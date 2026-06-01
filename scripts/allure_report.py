"""
Generate and open Allure HTML reports.

Prerequisites: Java 17+ and Allure CLI on PATH, or run once with --setup-tools
(downloads portable Java + Allure into tools/).

Examples:
  python scripts/allure_report.py test          # pytest -> allure-results
  python scripts/allure_report.py generate      # allure-results -> allure-report
  python scripts/allure_report.py serve         # local server from allure-results
  python scripts/allure_report.py all           # test + serve (typical end-to-end)
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
RESULTS_DIR = PROJECT_ROOT / "allure-results"
REPORT_DIR = PROJECT_ROOT / "allure-report"

ALLURE_VERSION = "2.34.0"
ALLURE_ZIP_URL = (
    f"https://github.com/allure-framework/allure2/releases/download/"
    f"{ALLURE_VERSION}/allure-{ALLURE_VERSION}.zip"
)
JAVA_WIN_ZIP_URL = (
    "https://github.com/adoptium/temurin17-binaries/releases/download/"
    "jdk-17.0.15%2B6/OpenJDK17U-jre_x64_windows_hotspot_17.0.15_6.zip"
)


def _find_java_home() -> Path | None:
    env = os.environ.get("JAVA_HOME")
    if env:
        java_home = Path(env)
        if (java_home / "bin" / "java.exe").exists() or (java_home / "bin" / "java").exists():
            return java_home

    if TOOLS_DIR.is_dir():
        for candidate in sorted(TOOLS_DIR.glob("jdk*")):
            if (candidate / "bin" / "java.exe").exists() or (candidate / "bin" / "java").exists():
                return candidate
    return None


def _find_allure_executable() -> Path | None:
    found = shutil.which("allure")
    if found:
        return Path(found)

    if not TOOLS_DIR.is_dir():
        return None

    for folder in sorted(TOOLS_DIR.glob("allure-*")):
        for name in ("allure.bat", "allure"):
            candidate = folder / "bin" / name
            if candidate.is_file():
                return candidate
    return None


def _run_env() -> dict[str, str]:
    env = os.environ.copy()
    java_home = _find_java_home()
    if java_home:
        env["JAVA_HOME"] = str(java_home)
    return env


def _run(cmd: list[str], *, check: bool = True) -> int:
    print(f"+ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=_run_env())
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.returncode


def _require_allure() -> Path:
    allure = _find_allure_executable()
    if allure:
        return allure
    print(
        "Allure CLI not found.\n"
        "  • Install Java 17+ and add Allure to PATH, or\n"
        "  • Run: python scripts/allure_report.py --setup-tools\n"
        "  • Or use scoop: scoop install allure",
        file=sys.stderr,
    )
    raise SystemExit(1)


def setup_tools() -> None:
    """Download portable Java (Windows) and Allure CLI into tools/."""
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    if _find_java_home() is None:
        if platform.system() != "Windows":
            print(
                "No JAVA_HOME and no tools/jdk*. Install Java 17+ manually, then retry.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        print("[setup] Downloading portable Java 17 JRE...")
        zip_path = TOOLS_DIR / "_jdk_download.zip"
        urlretrieve(JAVA_WIN_ZIP_URL, zip_path)  # noqa: S310 — fixed vendor URL
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(TOOLS_DIR)
        zip_path.unlink(missing_ok=True)
        if _find_java_home() is None:
            print("[setup] Java download finished but java.exe was not found.", file=sys.stderr)
            raise SystemExit(1)
        print(f"[setup] Java ready: {_find_java_home()}")

    if _find_allure_executable() is None:
        print(f"[setup] Downloading Allure CLI {ALLURE_VERSION}...")
        zip_path = TOOLS_DIR / "_allure_download.zip"
        urlretrieve(ALLURE_ZIP_URL, zip_path)  # noqa: S310 — fixed vendor URL
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(TOOLS_DIR)
        zip_path.unlink(missing_ok=True)
        if _find_allure_executable() is None:
            print("[setup] Allure download finished but binary was not found.", file=sys.stderr)
            raise SystemExit(1)
        print(f"[setup] Allure ready: {_find_allure_executable()}")

    print("[setup] Done.")


def run_tests() -> int:
    if not _find_java_home():
        print(
            "Warning: JAVA_HOME not set; Allure generate/serve may fail without Java.",
            file=sys.stderr,
        )
    return _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_recap_allure.py",
            "-v",
            f"--alluredir={RESULTS_DIR}",
        ],
        check=False,
    )


def generate_report() -> None:
    allure = _require_allure()
    if not RESULTS_DIR.is_dir() or not any(RESULTS_DIR.iterdir()):
        print(f"No results in {RESULTS_DIR}. Run: python scripts/allure_report.py test", file=sys.stderr)
        raise SystemExit(1)
    _run([str(allure), "generate", str(RESULTS_DIR), "-o", str(REPORT_DIR), "--clean"])


def serve_report() -> None:
    """Start Allure server from raw results (generates on the fly)."""
    allure = _require_allure()
    if not RESULTS_DIR.is_dir() or not any(RESULTS_DIR.iterdir()):
        print(f"No results in {RESULTS_DIR}. Run: python scripts/allure_report.py test", file=sys.stderr)
        raise SystemExit(1)
    print("[serve] Press Ctrl+C to stop the server.")
    _run([str(allure), "serve", str(RESULTS_DIR)])


def open_report() -> None:
    """Open a previously generated HTML report (requires generate first)."""
    allure = _require_allure()
    index = REPORT_DIR / "index.html"
    if not index.is_file():
        print(f"Report missing at {index}. Run: python scripts/allure_report.py generate", file=sys.stderr)
        raise SystemExit(1)
    print("[open] Press Ctrl+C to stop the server.")
    _run([str(allure), "open", str(REPORT_DIR)])


def main() -> None:
    parser = argparse.ArgumentParser(description="Allure report helper")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("test", "generate", "serve", "open", "all"),
        default="all",
        help="test=run pytest; generate=HTML folder; serve=server from results; open=server from HTML; all=test+serve (default)",
    )
    parser.add_argument(
        "--setup-tools",
        action="store_true",
        help="Download portable Java + Allure into tools/ (Windows Java bundle)",
    )
    args = parser.parse_args()

    if args.setup_tools:
        setup_tools()
        if args.command == "all" and len(sys.argv) == 2:
            return

    if args.command == "test":
        raise SystemExit(run_tests())
    if args.command == "generate":
        generate_report()
    elif args.command == "serve":
        serve_report()
    elif args.command == "open":
        open_report()
    elif args.command == "all":
        code = run_tests()
        if code != 0:
            print(f"[all] Tests exited with code {code}; generating report anyway.")
        serve_report()


if __name__ == "__main__":
    main()
