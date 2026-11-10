"""Actual frozen-app CLI and HTTP smoke by Jason Stys.

Function: main, read_output. Variables: process, queue, temp report and actual HTTP replies.
Only the explicitly supplied owned bundle is started/stopped. Index: docs/CODE_INDEX.md.
Preserved domain acceptance; canonical process/version/browser proof is in smoke_app.py."""

import json
import queue
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

if __package__:
    from .release_contract import require
else:
    from release_contract import require


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A local application check never follows an HTTP redirect to another listener or origin."""

    def redirect_request(self, *args, **kwargs):
        """Abort before urllib can issue the redirected request."""
        raise ValueError("Local native acceptance refuses redirects")


OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), RefuseRedirects())


def main(executable: Path) -> None:
    """Verify bundled snapshot/resource exports and the real UI/health/synthetic-analysis routes."""
    executable = executable.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="weather-smoke-") as directory:
        output = Path(directory) / "report.json"
        subprocess.run([str(executable), "export", "--output", str(output)], check=True, timeout=30)
        run = json.loads(output.read_bytes())
        require(
            bool(
                run["totals"]["estimated"] == 56
                and run["scores"]["statuses"] == {"unknown-issuance": 17}
            ),
            "Preserved native acceptance check failed",
        )
    process = subprocess.Popen(
        [str(executable), "serve", "--no-browser"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines: queue.Queue[str] = queue.Queue()

    def read_output() -> None:
        """Collect stdout without a blocking main-thread readline."""
        require(bool(process.stdout is not None), "Preserved native acceptance check failed")
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
        require(bool(url), "Preserved native acceptance check failed")
        for path in ("api/health", "", "api/run?scenario=synthetic-storm"):
            with OPENER.open(url + path, timeout=5) as response:
                body = response.read()
                if path == "":
                    require(
                        bool(b"Space Weather Impact Observatory" in body and b"/assets/" in body),
                        "Preserved native acceptance check failed",
                    )
                elif path.startswith("api/run"):
                    require(
                        bool(json.loads(body)["scores"]["mae"] == 1.0),
                        "Preserved native acceptance check failed",
                    )
                else:
                    require(
                        bool(json.loads(body)["status"] == "ok"),
                        "Preserved native acceptance check failed",
                    )
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
