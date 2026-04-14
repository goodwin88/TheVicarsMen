# The Vicar's Men

~ fiction and illustrations by Chris Goodwin


---

## Website

The collection is published as a static site via [GitHub Pages](https://goodwin88.github.io/TheVicarsMen/).

### Building and serving the site locally

**Prerequisites:** Python 3.9+

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Stage the source files into `docs/`:

   ```bash
   python scripts/stage_docs.py
   ```

3. Serve the site locally (live-reload):

   ```bash
   mkdocs serve
   ```

   Then open <http://127.0.0.1:8000> in your browser.

4. (Optional) Build a static copy of the site to `site/`:

   ```bash
   mkdocs build
   ```

> **Note:** The `docs/` and `site/` directories are generated and are excluded from version control (see `.gitignore`).
> Always run `scripts/stage_docs.py` before `mkdocs serve` or `mkdocs build`.

