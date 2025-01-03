# nmk-base
Base plugin for nmk build system

<!-- NMK-BADGES-BEGIN -->
[![License: MIT License](https://img.shields.io/github/license/dynod/nmk-base)](https://github.com/dynod/nmk-base/blob/main/LICENSE)
[![Checks](https://img.shields.io/github/actions/workflow/status/dynod/nmk-base/build.yml?branch=main&label=build%20%26%20u.t.)](https://github.com/dynod/nmk-base/actions?query=branch%3Amain)
[![Issues](https://img.shields.io/github/issues-search/dynod/nmk?label=issues&query=is%3Aopen+is%3Aissue+label%3Aplugin%3Abase)](https://github.com/dynod/nmk/issues?q=is%3Aopen+is%3Aissue+label%3Aplugin%3Abase)
[![Supported python versions](https://img.shields.io/badge/python-3.9%20--%203.13-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/nmk-base)](https://pypi.org/project/nmk-base/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://astral.sh/ruff)
[![Code coverage](https://img.shields.io/codecov/c/github/dynod/nmk-base)](https://app.codecov.io/gh/dynod/nmk-base)
[![Documentation Status](https://readthedocs.org/projects/nmk-base/badge/?version=stable)](https://nmk-base.readthedocs.io/)
<!-- NMK-BADGES-END -->

This plugin provides base features for **`nmk`** build, which by design don't need to be part of the **`nmk`** core implementation.

## Usage

To use this plugin in your **`nmk`** project, insert this reference:
```yaml
refs:
    - pip://nmk-base!plugin.yml
```

## Documentation

This plugin documentation is available [here](https://nmk-base.readthedocs.io/)

## Issues

Issues for this plugin shall be reported on the [main  **`nmk`** project](https://github.com/dynod/nmk/issues), using the **plugin:base** label.
