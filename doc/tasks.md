(allTasks)=
# Tasks

The **`nmk-base`** plugin defines the tasks described below.

## Meta tasks

This plugin defines some meta tasks that can be used by other plugins as kind of build "phases"

(setup)=
### **`setup`** task

The **`setup`** task aims to be the first phase of the build, allowing to perform prebuild operations like code generation, code formatting, dependencies checking, etc...

(build)=
### **`build`** task

The **`build`** task shall be used to perform all operation that build temporary and/or artifact files for the current project.

It is the **default** build task (i.e. this is the built task when **`nmk`** is invoked without argument).

It depends on the **{ref}`setup<setup>`** task.

(tests)=
### **`tests`** task

The **`tests`** task shall be used to perform all automated testing operations on generated software.

It depends on the **{ref}`build<build>`** task.

## Cleaning tasks

### **`clean`** -- output cleaning

The **`clean`** task will simply remove the {ref}`${outputDir}<outputDir>` folder and its entire content.

> Usage example:
> ```
> $ nmk clean
> 2022-02-20 14:37:54 (I) [clean] 🧹 - Clean build output
> 2022-02-20 14:37:54 (I) nmk 🏁 - Done
> ```

### **`git.clean`** -- full clean

The **`git.clean`** task will use git to clean the project folder, i.e. by removing all git ignored files.

**Warning:** this will remove (at least) both the **`venv`** and **`.nmk`** folders. Consequently, the build will immediately stop after this task, ignoring other tasks eventually specified on the command line. After this task is executed, the **`loadme.sh`** script will have to be used again to setup the project and reinstall **`nmk`**

## Helper tasks

(version)=
### **`version`** -- display version

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.helpers.VersionBuilder`

The **`version`** task will list the versions of **`nmk`** itself, plus all plugin versions contributed to {ref}`${nmkPluginsVersions}<nmkPluginsVersions>` object.

> Example:
> ```
> $ nmk version
> 2022-02-20 14:37:02 (I) [version] 🏷  - Display used nmk + plugins versions
> 2022-02-20 14:37:02 (I) [version] 🏷  -  👉 nmk: 0.0.0.post37+gf907587
> 2022-02-20 14:37:02 (I) [version] 🏷  -  👉 base: 1.0.0
> 2022-02-20 14:37:02 (I) nmk 🏁 - Done
> ```

(help)=
### **`help`** -- display help links

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.helpers.HelpBuilder`

The **`help`** task will list the help page URL of **`nmk`** itself, plus all plugin pages URLs contributed to {ref}`${nmkPluginsDocs}<nmkPluginsDocs>` object.

> Example:
> ```
> $ nmk help
> 2022-02-20 14:42:24 (I) [help] 🆘 - Display online help links
> 2022-02-20 14:42:24 (I) [help] 🆘 -  👉 nmk: https://github.com/dynod/nmk/wiki
> 2022-02-20 14:42:24 (I) [help] 🆘 -  👉 base: https://github.com/dynod/nmk/wiki/nmk-base-plugin
> 2022-02-20 14:42:24 (I) nmk 🏁 - Done
> ```

(tasks)=
### **`tasks`** -- list known tasks

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.helpers.TaskListBuilder`

The **`tasks`** task will list all the known tasks for the built project.

> Example:
> ```
> $ nmk tasks
> 2022-02-20 14:43:18 (I) [tasks] 🗃 - List all available tasks
> 2022-02-20 14:43:18 (I) [tasks] 🧹 -  👉 clean: Clean build output
> 2022-02-20 14:43:18 (I) [tasks] 🛫 -  👉 setup: Setup project configuration
> 2022-02-20 14:43:18 (I) [tasks] 🛠 -  👉 build: Build project artifacts
> 2022-02-20 14:43:18 (I) [tasks] 🤞 -  👉 tests: Run automated tests
> 2022-02-20 14:43:18 (I) [tasks] 🚀 -  👉 loadme: Generate "loadme" scripts
> 2022-02-20 14:43:18 (I) [tasks] 🏷 -  👉 version: Display used nmk + plugins versions
> 2022-02-20 14:43:18 (I) [tasks] 🆘 -  👉 help: Display online help links
> 2022-02-20 14:43:18 (I) [tasks] 🗃 -  👉 tasks: List all available tasks
> 
> ...
> 
> 2022-02-20 14:42:24 (I) nmk 🏁 - Done
> ```

## Setup tasks

All tasks in this chapter are dependencies of the main **{ref}`setup<setup>`** task.

(loadme)=
### **`loadme`** -- load scripts generation

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.loadme.BuildLoadMe`
| input    | {ref}`${loadMeTemplates}<loadMeTemplates>` files
| output   | {ref}`${loadMeTargets}<loadMeTargets>` files

The **`loadme`** task generates "loadme" scripts, aiming to be persisted in project repository, and allowing to:
* create a local python venv where **`nmk`** (and all python dependencies of the project) will be installed
* enable this venv

This task can handle several scripts (for different OS; Linux is supported by default), by defining the different configuration items below:
* {ref}`${loadMeTargets}<loadMeTargets>`: list of target scrips to be generated
* {ref}`${loadMeTemplates}<loadMeTemplates>`: list of source script templates
* {ref}`${loadMeVenvPython}<loadMeVenvPython>`: list of python commands to be used in script to create the venv

Note that the generated **`.sh`** script for Linux support is compatible with **git-bash.exe** on Windows, making useless to generate a specific **`.bat`** script.

The task execution will zip these lists together to generate the scripts. This supposes that all the lists have the same elements count. If a list is shorter, extra elements in the other lists will be simply ignored.

The generated script will also verify system dependencies before creating the python venv. The dependencies to be verified are set in the **{ref}`${loadMeSysDeps}<loadMeSysDeps>`** config item. This item is an object, indexed by commands to be checked. Each command defines another object, providing instructions on how to install the command if it's not found. Supported keys are:
* **`apt`**: provides a string or a list of string, all being apt package names to be installed (used on Linux)
* **`url`**: provides an URL string, pointing to instructions on how to install the command (used on Windows)

> Example:
> ```yaml
> config:
>     loadMeSysDeps:
>         python3:
>             apt: ["python3", "python3-venv"]        # Will install these packages through apt on Linux, if "python3" command is missing
>         python:
>             url: https://www.python.org/downloads/  # Will display this URL on Windows, if "python" command is missing
> ```

(git.version)=
### **`git.version`** -- git version update

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.git.GitVersionRefresh`
| output   | {ref}`${gitVersionStamp}<gitVersionStamp>` file
| deps     | {ref}`out<out>` task

This task is used to update the {ref}`${gitVersionStamp}<gitVersionStamp>` file, each time the {ref}`${gitVersion}<gitVersion>` value is updated (new commit, new tag...)

(git.ignore)=
### **`git.ignore`** -- generate .gitignore file

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.git.GitIgnore`
| input    | {ref}`${gitIgnore}<gitIgnore>` & {ref}`${gitIgnoreTemplate}<gitIgnoreTemplate>` files
| output   | {ref}`${gitIgnore}<gitIgnore>` & {ref}`${gitIgnoreStamp}<gitIgnoreStamp>` files
| deps     | {ref}`out<out>` task

This task is used to update the {ref}`${gitIgnore}<gitIgnore>` file with a fragment generated from the list of ignored files configured in {ref}`${gitIgnoredFiles}<gitIgnoredFiles>` item. 

Notes:
* Project-relative paths are automatically made relative to project root.
* Non project-relative absolute paths are ignored when generating the fragment.

(git.attributes)=
### **`git.attributes`** -- generate .gitattributes file

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.git.GitAttributes`
| output   | {ref}`${gitAttributes}<gitAttributes>` & {ref}`${gitAttributesStamp}<gitAttributesStamp>` files
| deps     | {ref}`out<out>` task

This task is used to update the {ref}`${gitAttributes}<gitAttributes>` file with a fragment generated from the following config items:
* {ref}`${linuxLineEndings}<linuxLineEndings>`: list of file extensions (".xxx" format) requiring to be systematically handled with Linux line endings
* {ref}`${windowsLineEndings}<windowsLineEndings>`: list of file extensions (".xxx" format) requiring to be systematically handled with Windows line endings

(py.req)=
### **`py.req`** -- generate python venv requirements file

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.common.TemplateBuilder`
| input    | {ref}`${venvArchiveDeps}<venvArchiveDeps>` & {ref}`${venvFileDeps}<venvFileDeps>` & {ref}`${venvRequirementsTemplate}<venvRequirementsTemplate>` files
| output   | ${PROJECTDIR}/{ref}`${venvRequirements}<venvRequirements>` file

This task merges all python venv requirements in one single generated file ({ref}`${venvRequirements}<venvRequirements>`). This file is used:
* by "loadme" scripts (generated by {ref}`loadme<loadme>` task) to bootstrap the project just after the clone
* by {ref}`py.venv<py.venv>` task to update the venv when requirements change during the project lifecycle

It is triggered only if:
* one of referenced requirement files (from {ref}`${venvFileDeps}<venvFileDeps>` config list) is updated
* one of referenced archive files (from {ref}`${venvArchiveDeps}<venvArchiveDeps>` config list) is updated
* the requirements template (from {ref}`${venvRequirementsTemplate}<venvRequirementsTemplate>` config list) is updated
* project files are updated

(py.venv)=
### **`py.venv`** -- update python venv

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.venv.VenvUpdateBuilder`
| input    | ${PROJECTDIR}/{ref}`${venvRequirements}<venvRequirements>` file
| output   | ${ROOTDIR}/{ref}`${venvName}<venvName>` & {ref}`${venvState}<venvState>` files
| deps     | {ref}`out<out>` & {ref}`py.req<py.req>` tasks

This task updates the Python venv from the expected requirements, as soon as they are updated (i.e. when {ref}`${venvRequirements}<venvRequirements>` file changes).

It also generates a dump ({ref}`${venvState}<venvState>`) of all installed packages (using the [pip requirement specifiers syntax](https://pip.pypa.io/en/stable/reference/requirement-specifiers/)); this dump can be used to compare builds, and/or to restore a previous build exact venv environment (from troubleshooting or others...)


(out)=
### **`out`** -- output folder creation

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.common.MkdirBuilder`
| output   | {ref}`${outputDir}<outputDir>` folder

This task simply silently creates the {ref}`${outputDir}<outputDir>` folder. All tasks aiming to create files in this folder should reference this task.

## Test tasks

All tasks in this chapter are dependencies of the main **{ref}`tests<tests>`** task.

(git.dirty)=
### **`git.dirty`** -- check for dirty project folder

| Property | Value/description |
|-         |-
| builder  | {py:class}`nmk_base.git.GitIsDirty`
| if       | {ref}`${gitEnableDirtyCheck}<gitEnableDirtyCheck>` folder

This task verifies if project folder is dirty (e.g. contains not committed files). In this case, it makes the build failing.
