# macrodials

The site: articles, models and notes on the data feed, built with MkDocs Material and published to GitHub Pages at https://tyrel-beede.github.io/macrodials/ on every push to `main`.

- `docs/` — the pages; `docs/blog/posts/` — articles (a Markdown file with a `date:` front matter); `docs/model/` — model pages; `docs/files/` — workbooks
- `tools/site_tables.py` — exports the Bull Case 2.0 workbook's display tables to Markdown for the Models page (the site build runs it)
- `.github/workflows/site.yml` — `mkdocs build --strict` and deploy to Pages

The data behind the dashboard is in [fred_data_feed](https://github.com/tyrel-beede/fred_data_feed).

Preview locally: `pip install "mkdocs-material>=9.7,<10" openpyxl && python tools/site_tables.py && mkdocs serve`.
