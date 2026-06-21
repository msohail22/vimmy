# Characters

This package contains 3D character assets for the game, organized by category.

## Categories

- `assets/bosses/` — Large boss/demon characters (5 models)
- `assets/beasts/` — Monster/beast characters (2 models)
- `assets/minions/` — Smaller minion/mook characters (2 models)
- `assets/characters/` — Game-ready characters across genres (19 models)
- `assets/base/` — Base test models (CesiumMan, etc.)
- `assets/generated/` — Blender-generated test models (spherehead variants)

## Preview

Start a local server from this directory:

```bash
python3 -m http.server 8080 --directory /packages/characters
```

Then open `http://localhost:8080/preview/` in a browser.

The preview page loads models from `assets/manifest.json` and lets you browse by category.

## Sources

All models are free CC Attribution downloads from [getglb.com](https://www.getglb.com/). See each category's README for source URLs.
