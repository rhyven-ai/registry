# Rhyven app registry

Public app listings and installable packages published by Rhyven. The platform
source is available under Apache-2.0 in
[rhyven-ai/rhyven](https://github.com/rhyven-ai/rhyven). This registry contains
distribution metadata and app packages; it does not host customer data or workloads.

## App source and licenses

The source for Rhyven apps, their examples, tests and authoring guides
is available in [rhyven-ai/apps](https://github.com/rhyven-ai/apps) under
[Apache-2.0](https://github.com/rhyven-ai/apps/blob/main/LICENSE).
You may use, modify and redistribute those app materials under that license.
Third-party dependencies retain their own licenses and notices.

The engine source is also Apache-2.0; see its
[license](https://github.com/rhyven-ai/rhyven/blob/main/LICENSE) and dependency notices.
The current runtime and registry validator are 0.5.5. Install the signed
binary from the website:

```sh
curl -fsSL https://rhyvenai.com/install.sh | bash -s -- --containers
```
Source candidates can be newer than installable releases; `index.json` remains
the list of published package versions. Existing package bytes are unchanged.

## Browse and install

Use Rhyven 0.4.0-rc.6 or later. No GitHub account is needed to browse or download
public apps:

```sh
rhyven registry-sync rhyven-ai/registry --anonymous
rhyven search
rhyven inspect rhyven/work-management
rhyven install rhyven/work-management
```

`registry-sync` explicitly downloads and validates app manifests for CLI/TUI
browsing. It does not install apps or pull container images. Review permissions,
then add `--accept-permissions` to approve installation.

For agent-only discovery, use `rhyven registry-refresh rhyven-ai/registry
--anonymous` instead; it downloads metadata only.
Connected agents use `rhyven_categories()`, `rhyven_describe(category)` and
`rhyven_call(category, function, args)` to browse `rhyven/marketplace`, request
human approval, install and operate apps. Every app runs in your environment.

## Rhyven apps

The publisher namespace is `rhyven`, owned by the GitHub account `rhyven-ai`.
App IDs, versions, descriptions, permissions, package locations and hashes are
recorded in `index.json`. Repository stars describe popularity. `Unverified`
means no independent certification; it does not mean the app has a different
publisher. Older Rhyven installations with `official/...` or
`community/inventory` IDs retain their state and are not renamed automatically.

| App | App ID | Execution |
| --- | --- | --- |
| Work Management | `rhyven/work-management` | Declarative |
| Project Knowledge | `rhyven/project-knowledge` | Declarative |
| Error Management | `rhyven/error-management` | Declarative |
| CI Management | `rhyven/ci-management` | Declarative |
| Inventory | `rhyven/inventory` | Declarative |
| Rhyven Repo Documentation Tool | `rhyven/repo-documentation-tool` | On-demand container |
| Messaging | `rhyven/messaging` | Persistent service |

Container images are public, pinned to immutable digests, and pulled only after
installation consent. They require a compatible Docker engine; installation
and execution are tested on Linux x86-64. The documentation tool analyzes
imported repository snapshots. Messaging runs under the local supervisor:
start it with `rhyven daemon start` after installation. The registry index is the
current list of available versions.

## Submit an app

1. Define your app contract and behavior. Use `rhyven app init` to scaffold it.
2. Run `rhyven app validate`, `rhyven app test` and `rhyven app package`.
3. Upload the package to a public release in your GitHub repository. Container
   images must be available to users and pinned by immutable digest.
4. Generate the entry with `rhyven registry-entry PACKAGE --repository OWNER/REPO
   --asset-id ASSET_ID`.
5. Submit a pull request adding the entry to `index.json`. A new publisher
   namespace needs registration by the registry maintainer first.

Published entries and namespace ownership are immutable. Publish a new version
when changing a package. All permissions and execution details must match the
package exactly. Do not upload credentials, customer data or platform source.

Registry validation uses a pinned prebuilt runtime, executes no code from the
pull request, and does not run container app code. Hashes, schemas, publisher
ownership and declarative behavior are checked. The validator binary release
contains executable software. Engine source is maintained in the engine repository.
