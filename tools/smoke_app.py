"""Actual frozen-app CLI and HTTP smoke by Jason Stys.

Function: main, read_output. Variables: process, queue, temp report and actual HTTP replies.
Only the explicitly supplied owned bundle is started/stopped. Index: docs/CODE_INDEX.md.
"""

import json
import queue
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path


def main(executable: Path) -> None:
    """Verify bundled snapshot/resource exports and the real UI/health/synthetic-analysis routes."""
    executable = executable.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="weather-smoke-") as directory:
        output = Path(directory) / "report.json"
        subprocess.run([str(executable), "export", "--output", str(output)], check=True, timeout=30)
        run = json.loads(output.read_bytes())
        assert run["totals"]["estimated"] == 56 and run["scores"]["statuses"] == {
            "unknown-issuance": 17
        }
    process = subprocess.Popen(
        [str(executable), "serve", "--no-browser"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines: queue.Queue[str] = queue.Queue()

    def read_output() -> None:
        """Collect stdout without a blocking main-thread readline."""
        assert process.stdout is not None
        for line in process.stdout:
            lines.put(line.strip())

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    try:
        url = ""
        for _ in range(5):
            line = lines.get(timeout=15)
            if line.startswith("http://127.0.0.1:"):
                url = line
                break
        assert url
        for path in ("api/health", "", "api/run?scenario=synthetic-storm"):
            with urllib.request.urlopen(url + path, timeout=5) as response:
                body = response.read()
                if path == "":
                    assert b"Space Weather Impact Observatory" in body and b"/assets/" in body
                elif path.startswith("api/run"):
                    assert json.loads(body)["scores"]["mae"] == 1.0
                else:
                    assert json.loads(body)["status"] == "ok"
        print(
            "Frozen app: verified NOAA resources, JSON, production HTML/assets and synthetic forecast API passed"
        )
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        reader.join(timeout=3)
        if process.stdout:
            process.stdout.close()


if __name__ == "__main__":
    main(Path(sys.argv[1]))
