import unittest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from validate import authorize, main, attach_pallets


class AuthorizationTests(unittest.TestCase):
    def test_only_owner_or_maintainer_may_submit(self):
        base = {"publishers": {"alice": "alice"}, "apps": []}
        new = {**base, "apps": [{"name": "alice/app", "version": "0.1.0", "publisher": "alice"}]}
        authorize(base, new, "alice", "maintainer")
        authorize(base, new, "maintainer", "maintainer")
        with self.assertRaises(ValueError):
            authorize(base, new, "attacker", "maintainer")

    def test_sidecar_does_not_change_legacy_app_index(self):
        base = {"format": 1, "publishers": {}, "apps": []}
        merged = attach_pallets(base, {"format": 1, "pallets": []})
        self.assertNotIn("pallets", base)
        self.assertEqual(merged["apps"], base["apps"])
        with self.assertRaises(ValueError):
            attach_pallets(base, {"format": 2, "pallets": []})

    def test_retired_pallets_are_preserved_but_not_submitted(self):
        entry = {"name": "alice/text-kit", "version": "0.1.0"}
        base = {"publishers": {"alice": "alice"}, "apps": [], "pallets": [entry]}
        authorize(base, dict(base), "alice", "maintainer")
        for actor in ("alice", "maintainer", "attacker"):
            for entries in ([], [entry, {**entry, "version": "0.2.0"}], [{**entry, "description": "changed"}]):
                with self.assertRaises(ValueError):
                    authorize(base, {**base, "pallets": entries}, actor, "maintainer")

    def test_namespace_registration_needs_maintainer(self):
        base = {"publishers": {}, "apps": []}
        new = {"publishers": {"official": "attacker"}, "apps": []}
        with self.assertRaises(ValueError):
            authorize(base, new, "attacker", "maintainer")
        authorize(base, new, "maintainer", "maintainer")


    def test_transfer_uses_repository_owner_for_namespace_registration(self):
        base = {"publishers": {}, "apps": []}
        proposed = {"publishers": {"company": "rhyven-ai"}, "apps": []}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "index.json").write_text(json.dumps(base))
            event = path / "event.json"
            previous = Path.cwd()
            try:
                os.chdir(path)
                with patch.dict(os.environ, {"GITHUB_EVENT_PATH": str(event), "GITHUB_REPOSITORY_OWNER": "rhyven-ai"}), patch("validate.contents", return_value=proposed), patch("validate.optional_pallets", return_value=None), patch("validate.subprocess.run") as validate:
                    for actor in ("scornsaber", "attacker"):
                        event.write_text(json.dumps({"pull_request": {"user": {"login": actor}, "head": {"repo": {"full_name": "company/contribution"}, "sha": "abc"}}}))
                        with self.assertRaises(ValueError):
                            main()
                        validate.assert_not_called()
                    event.write_text(json.dumps({"pull_request": {"user": {"login": "rhyven-ai"}, "head": {"repo": {"full_name": "company/contribution"}, "sha": "abc"}}}))
                    main()
                    validate.assert_called_once()
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
