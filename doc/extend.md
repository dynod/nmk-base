# Configuration Extension

As for all **`nmk`** projects config items, [**`nmk-base`** ones](config.md) are all overridable by other plug-ins and project files. But the ones described on this page are specifically designed to be extended.

## Dependencies handling

The **`nmk-base`** plugin allows to declare and install different kind of dependencies in an **`nmk`** project.

### System dependencies

The **`nmk-base`** plugin generates a **`loadme.sh`** script in the root folder of an **`nmk`** project (see the {ref}`loadme<loadme>` task).

This shell script verifies if required system dependencies are installed. Depending on the current OS, if a dependency is not found :
* on Linux (Debian-like distributions), the script will trigger the corresponding package install using **`apt install`** command.
* on Windows, the script will display the URL from which this dependency can be manually installed and stop.

In order to add system dependencies to be verified by this script, the **{ref}`loadMeSysDeps<loadMeSysDeps>`** config item can be extended by **`nmk`** projects or plugins. This item syntax is described below:
```yaml
    loadMeSysDeps:
        COMMAND:
            apt: ["PACKAGE"]
            url: https://someurl.org/
```

With:
* **COMMAND** being the dependency command that is expected on the system path (e.g. by checking **`which COMMAND`** command return)
* **apt** being a list of Linux packages to be installed with **`apt install`** command
* **url** being the URL of the download page for this system dependency

### Python modules dependencies

The **`nmk-base`** plugin handles a Python virtual environment ("**venv**") for **`nmk`** projects.
It generates a requirements file (typically a **requirements.txt** file in the project root folder), and handles the **venv** lifecycle:
* The **`loadme.sh`** script creates the **venv** if it doesn't exist yet
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
