# 🚀 Usage

To use this plugin in your **`nmk`** project, insert this reference in your **nmk.yml** main file:

```yaml
refs:
  - pip://nmk-base!plugin.yml
```

```{note}
Since all **`nmk`** plugins already reference this base plugin dependency, so you shouldn't need to explicitely declare it.
```

Then, all [features](features) from **`nmk-base`** plugin are automatically enabled in your project.
