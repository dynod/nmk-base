# Changelog

Here are listed all the meaningfull changes done on **`nmk-base`** since version 1.0

```{note}
Only interface and important behavior changes are listed here.

The fully detailed changelog is also available on [Github](https://github.com/dynod/nmk-base/releases)
```

## Release 1.4.0

- Change documentation theme
- Add preliminary support for buildenv 2.0 install templates

## Release 1.3.0

- Config items update:
  - added {ref}`${requestFunction}<requestFunction>`: name of request function used for download tasks
  - added {ref}`${javaRuntime}<javaRuntime>` and {ref}`${javaRuntimeCustomPath}<javaRuntimeCustomPath>`: used to resolve **java** command
- API update:
  - updated {py:class}`nmk_base.resolvers.FilesResolver` to make it a "ready to use" resolver, with parameters
  - moved {py:class}`nmk_base.resolvers.MultiChoiceResolver` (and sub-classes) from `nmk_base.common` module, for more consistency
  - added {py:class}`nmk_base.common.DownloadBuilder` builder to handle download tasks (with progress bar + extraction option)
  - added {py:class}`nmk_base.resolvers.CommandResolver` resolver, to resolve a given command from a provided custom path or from system path

## Release 1.2.0

- Config items changes:
  - Update {ref}`${venvName}<venvName>`: make it dynamic WRT. current environment backend.
  - Add {ref}`${venvRoot}<venvRoot>`: get the venv root folder.
  - Add {ref}`${venvUpdateInput}<venvUpdateInput>`: overridable input file for {ref}`py.venv<py.venv>` task.
  - Add {ref}`${backendUseRequirements}<backendUseRequirements>`: state if the environment backend uses a requirements file.
  - Add {ref}`${backendLegacy}<backendLegacy>`: state if the environment backend implementation is a legacy one.
  - Add {ref}`${buildenvFolder}<buildenvFolder>`: legacy buildenv folder.
  - Update {ref}`${buildenvRefresh}<buildenvRefresh>`: disable buildenv loading scripts generation for buildenv version >= 2.
- {ref}`py.venv<py.venv>` and {ref}`py.req<py.req>` tasks inputs/outputs + behavior update to adapt to different environment backends.
- API update: added {py:class}`nmk_base.common.MultiChoiceResolver` (+ subclasses) resolvers for factorized config item multi-choice resolution.

## Release 1.1.0

- Add {ref}`${isLocalBuild}<isLocalBuild>` and {ref}`${isCIBuild}<isCIBuild>` config items to detect build context

## Release 1.0.1

- {ref}`${venvPkgDeps}<venvPkgDeps>` default value changed to **[${PACKAGESREFS}](https://nmk.readthedocs.io/en/stable/file.html#built-in-config-items)**
