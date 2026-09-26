"""Trusted base-branch submission checks; never execute code from a PR."""
import json
import os
from pathlib import Path
import subprocess
import tempfile


def contents(repository, path, ref):
    # Arguments are passed directly, not interpolated into a shell.
    result = subprocess.run(
        ["gh", "api", f"repos/{repository}/contents/{path}", "--method", "GET",
         "-f", f"ref={ref}", "-H", "Accept: application/vnd.github.raw+json"],
        check=True, capture_output=True,
    ).stdout
    if len(result) > 1_048_576:
        raise ValueError("File exceeds 1 MiB")
    return json.loads(result)


def authorize(base, proposed, actor, maintainer):
    if proposed.get("publishers") != base.get("publishers") and actor != maintainer:
        raise ValueError("Only the registry maintainer can register publisher namespaces")
    old = {(e["name"], e["version"]): e for e in base["apps"]}
    for entry in proposed["apps"]:
        if old.get((entry["name"], entry["version"])) == entry:
            continue
        owner = base["publishers"].get(entry["publisher"])
        if actor != maintainer and actor != owner:
            raise ValueError("Submission must come from the registered owner or registry maintainer")


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    base = json.loads(Path("index.json").read_text())
    runtime = str(Path("validator/rhyven-linux-x86_64").resolve())
    with tempfile.TemporaryDirectory(prefix="registry-check-") as temp:
        proposed = base
        if "pull_request" in event:
            pr = event["pull_request"]
            proposed = contents(pr["head"]["repo"]["full_name"], "index.json", pr["head"]["sha"])
            authorize(base, proposed, pr["user"]["login"], os.environ["GITHUB_REPOSITORY_OWNER"])
        path = Path(temp) / "index.json"
        path.write_text(json.dumps(proposed))
        subprocess.run([runtime, "registry-validate", str(path), "--base", "index.json"], check=True)


if __name__ == "__main__":
    main()
