# Buildenv contributions

The **`nmk-base`** plugin extends the [buildenv tool](https://pypi.org/search/?q=buildenv) with following features:
* it registers the **nmk** command for completion (i.e. makes **nmk** command completion working when the venv/buildenv is activated)
* on `buildenv init` command, it triggers an `nmk setup` build if the project contains an **`nmk.yml`** project file
