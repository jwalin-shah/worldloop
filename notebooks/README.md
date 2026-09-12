# WorldLoop marimo lab

The notebook is a reactive experiment/control surface over the public WorldLoop fixtures and experiment registry. It is not a canonical state store and it does not automatically query private LifeOps data.

Edit interactively:

```bash
uv run marimo edit notebooks/worldloop_lab.py
```

Run it as an app:

```bash
uv run marimo run notebooks/worldloop_lab.py
```

Export a static validation artifact:

```bash
uv run marimo export html notebooks/worldloop_lab.py -o /tmp/worldloop_lab.html
```

Use the case selector to inspect pass-by-pass recipe, evidence, diagnosis, and score changes. The lower tables show the aggregate benchmark and the experiment registry.
