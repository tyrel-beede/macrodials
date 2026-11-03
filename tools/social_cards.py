"""Render Open Graph / Twitter card images (1200×630 PNG) for pages that declare `card: <name>` in their
front matter, plus a default card for every other page, into docs/assets/cards/. The page template
(overrides/main.html) points og:image / twitter:image at these. Run by the site workflow before
`mkdocs build`; needs Playwright with Chromium (python -m playwright install chromium).
"""
import html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "assets" / "cards"
SITE_NAME = "Macro Dials"
SITE_URL = "tyrel-beede.github.io/macrodials"
LOGO = (DOCS / "assets" / "logo.svg").read_text(encoding="utf-8")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
html, body { margin: 0; }
.card { width: 1200px; height: 630px; box-sizing: border-box; padding: 64px 72px 56px 72px; background: #0b1020;
        color: #e6e8ee; font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden; }
.card::after { content: ""; position: absolute; right: -140px; top: -140px; width: 520px; height: 520px; border-radius: 50%;
               border: 56px solid rgba(61, 214, 195, 0.06); }
.brand { display: flex; align-items: center; gap: 16px; font-size: 26px; font-weight: 600; letter-spacing: -0.01em; color: #c3c9d6; }
.brand svg { width: 40px; height: 40px; }
.kicker { font-size: 22px; color: #3dd6c3; font-weight: 500; margin-bottom: 14px; letter-spacing: 0.02em; text-transform: uppercase; }
.title { font-size: 60px; line-height: 1.12; font-weight: 700; letter-spacing: -0.02em; color: #ffffff; max-width: 1000px; }
.title.small { font-size: 48px; }
.rule { width: 96px; height: 6px; background: #f2b544; border-radius: 3px; margin: 26px 0 22px 0; }
.desc { font-size: 26px; line-height: 1.35; color: #aeb6c7; max-width: 980px; }
.foot { display: flex; justify-content: space-between; font-size: 20px; color: #8b94a7; }
"""


def render(name, kicker, title, desc, foot_right, pg):
    small = " small" if len(title) > 44 else ""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="card" id="card">
  <div class="brand">{LOGO}<span>{html.escape(SITE_NAME)}</span></div>
  <div>
    <div class="kicker">{html.escape(kicker)}</div>
    <div class="title{small}">{html.escape(title)}</div>
    <div class="rule"></div>
    <div class="desc">{html.escape(desc)}</div>
  </div>
  <div class="foot"><span>{html.escape(SITE_URL)}</span><span>{html.escape(foot_right)}</span></div>
</div></body></html>"""
    pg.set_content(doc)
    pg.wait_for_timeout(400)
    pg.locator("#card").screenshot(path=str(OUT / f"{name}.png"))


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    return meta


def page_title(text):
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed — skipping social cards"); return
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [p for p in DOCS.rglob("*.md") if "model/tables" not in str(p)]
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        render("default", "Articles · Models · The data feed", "Macro Dials",
               "Long-form articles, the models behind them, and the data feed both are built from — a three-cycle read of where the debt, capital-spending and business cycles stand, written to be checkable.",
               "Not advice", pg)
        for path in pages:
            text = path.read_text(encoding="utf-8"); meta = front_matter(text)
            if "card" not in meta:
                continue
            title = meta.get("title") or page_title(text)
            desc = meta.get("description", "")
            kicker = meta.get("kicker") or ("Article" if "blog/posts" in str(path) else "Models")
            foot = meta.get("card_foot") or ""
            render(meta["card"], kicker, title, desc, foot, pg)
            print("card", meta["card"], "<-", path.relative_to(DOCS))
        b.close()


if __name__ == "__main__":
    main()
