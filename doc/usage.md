# Usage

To use this plugin in your **`nmk`** project, insert this reference in your **nmk.yml** main file:

```yaml
refs:
  - pip://nmk-base!plugin.yml
```

Note that all **`nmk`** plugins already reference this base plugin dependency, so you shouldn't need to explicitely declare it.

## Tasks

This plugin defines a set of basic and miscellaneous [nmk tasks](tasks), ready to use in all of you **`nmk`** projects.

## Configuration

All configuration items defined by this plugin are described in the following chapters:

- items that you can override to customize your project are summarized in the [Configuration Extension](extend) chapter
- if you look for an exhaustive list off all items handled by this plugin, please see [Configuration Reference](config) chapter
