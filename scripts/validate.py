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


def attach_pallets(index, sidecar):
    if sidecar is None:
        return index
    if set(sidecar) != {"format", "pallets"} or sidecar["format"] != 1 or index.get("pallets"):
        raise ValueError("Invalid or duplicate pallet index")
    return {**index, "pallets": sidecar["pallets"]}


def optional_pallets(repository, ref):
    try:
        return contents(repository, "pallets.json", ref)
    except subprocess.CalledProcessError as error:
        if b"HTTP 404" in (error.stderr or b""):
            return None
        raise


def authorize(base, proposed, actor, maintainer):
    if proposed.get("publishers") != base.get("publishers") and actor != maintainer:
        raise ValueError("Only the registry maintainer can register publisher namespaces")
    for kind in ("apps", "pallets"):
        old = {(e["name"], e["version"]): e for e in base.get(kind, [])}
        for entry in proposed.get(kind, []):
            if old.get((entry["name"], entry["version"])) == entry:
                continue
            namespace = entry["name"].split("/", 1)[0]
            owner = base["publishers"].get(namespace)
            if actor != maintainer and actor != owner:
                raise ValueError("Submission must come from the registered owner or registry maintainer")


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    base = attach_pallets(json.loads(Path("index.json").read_text()),
                          json.loads(Path("pallets.json").read_text()) if Path("pallets.json").exists() else None)
    runtime = str(Path("validator/rhyven-linux-x86_64").resolve())
    with tempfile.TemporaryDirectory(prefix="registry-check-") as temp:
        proposed = base
        if "pull_request" in event:
            pr = event["pull_request"]
            proposed = contents(pr["head"]["repo"]["full_name"], "index.json", pr["head"]["sha"])
            proposed = attach_pallets(proposed, optional_pallets(pr["head"]["repo"]["full_name"], pr["head"]["sha"]))
            authorize(base, proposed, pr["user"]["login"], os.environ["GITHUB_REPOSITORY_OWNER"])
        path = Path(temp) / "index.json"
        path.write_text(json.dumps(proposed))
        subprocess.run([runtime, "registry-validate", str(path), "--base", "index.json"], check=True)


if __name__ == "__main__":
    main()
