# Rhyven app registry

Public app listings and installable packages published by Rhyven. The platform
source is maintained separately in a private repository. This registry contains
no platform source archives and does not host customer data or workloads.

## Browse and install

Use Rhyven 0.4.0-rc.6 or later. No GitHub account is needed to browse or download
public apps:

```sh
rhyven registry-refresh rhyven-ai/registry --anonymous
rhyven search
rhyven inspect rhyven/work-management
rhyven install rhyven/work-management
```

Review permissions, then add `--accept-permissions` to approve installation.
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

Rhyven Repo Documentation Tool uses `rhyven/repo-documentation-tool`.
Container apps are listed only after their required images are anonymously
pullable. The registry index is the current list of available versions.

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
contains executable software, not the private platform source.
