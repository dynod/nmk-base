# Configuration Extension

As for all **`nmk`** projects config items, [**`nmk-base`** ones](config.md) are all overridable by other plug-ins and project files. But the ones described on this page are specifically designed to be extended.

## Dependencies handling

The **`nmk-base`** plugin allows to declare and install different kind of dependencies in an **`nmk`** project.

### Python modules dependencies

The **`nmk-base`** plugin handles a Python virtual environment ("**venv**") for **`nmk`** projects.
It generates a requirements file (typically a **requirements.txt** file in the project root folder), and handles the **venv** lifecycle:
* The **`buildenv`** tool creates the **venv** if it doesn't exist yet
* The **{ref}`py.venv<py.venv>`** task maintains it up to date by adding new requirements when project files are updated.

**`nmk`** projects or plugins can extend the following config items to declare Python modules dependencies to be installed in the **venv**:
* **{ref}`venvPkgDeps<venvPkgDeps>`**: list of Python modules names to be installed.
  Example:
  ```yaml
  venvPkgDeps:
      - numpy
  ```

* **{ref}`venvArchiveDeps<venvArchiveDeps>`**: list of local Python module archives installed.
  Example:
  ```yaml
  venvArchiveDeps:
      - /some/local/path/to/my-module.wheel
      - /some/other/module.tar.gz
  ```

* **{ref}`venvFileDeps<venvFileDeps>`**: list of requirements files to be merged in the generated requirements file.
  Example:
  ```yaml
  venvFileDeps:
      - ${PROJECTDIR}/test-requirements.txt
  ```

## Project information

**`nmk`** plugins or project can override to the following items to give information about the project:

* **{ref}`projectName<projectName>`**: string giving the name of the project
  Example:
  ```yaml
  projectName: MyAwesomeProject
  ```

* **{ref}`projectAuthor<projectAuthor>`**: string giving the author of the project
  Example:
  ```yaml
  projectAuthor: The project team name
  ```

## Plugin information

**`nmk`** plugins can contribute to the following items to give version/doc information:

* **{ref}`nmkPluginsVersions<nmkPluginsVersions>`**: object giving the plugin version.
  Example:
  ```yaml
  nmkPluginsVersions:
      my-plugin-name: 1.0.0
  ```

* **{ref}`nmkPluginsDocs<nmkPluginsDocs>`**: object giving the URL to the plugin documentation.
  Example:
  ```yaml
  nmkPluginsDocs:
      my-plugin-name: https://someurl/to/my/doc
  ```

## Git ignored files

**`nmk`** projects or plugins that want to ignore some specific files/folders can contribute to the following items:

* **{ref}`gitIgnoredFiles<gitIgnoredFiles>`**: list of files to be ignored by git.
  Example:
  ```yaml
  gitIgnoredFiles:
      - some-generated-folder/
      - some-generated-files.*
  ```

## Line endings handling

**`nmk`** projects or plugins that want to identify some file types for which the line endings must be kept can contribute to the following items:

* **{ref}`linuxLineEndings<linuxLineEndings>`**: list of file extensions which must be kept with Linux line endings.
  Example:
  ```yaml
  linuxLineEndings:
      - .csh
  ```
* **{ref}`windowsLineEndings<windowsLineEndings>`**: list of file extensions which must be kept with Windows line endings.
  Example:
  ```yaml
  windowsLineEndings:
      - .ps
  ```

## Dirty check enablement

By default, the **{ref}`git.dirty<git.dirty>`** task is disabled. **`nmk`** projects or plugins may override the **{ref}`gitEnableDirtyCheck<gitEnableDirtyCheck>`** item to implement a logic able to toggle this check in certain conditions (e.g. in automated builds).

Example:
```yaml
gitEnableDirtyCheck:
    __resolver__: path.to.my.resolver
```
