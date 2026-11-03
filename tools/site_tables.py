"""Export the display tables of the Bull Case 2.0 workbook for the site, as Markdown and as PNG images.

Reads docs/files/SpaceX_Bull_Case_2.0.xlsx (cached values, so the file must have been saved after a
recalculation) and writes
  docs/model/tables/*.md   — Markdown tables the Models page includes with the snippets syntax
  docs/model/images/*.png  — the same tables rendered as images (linkable, copy-pasteable), via Playwright/Chromium
Run by the site workflow before `mkdocs build`; safe to run locally (pip install openpyxl playwright;
python -m playwright install chromium). Without Playwright the Markdown is still written and the images are skipped.
"""
import html, pathlib, sys
from openpyxl import load_workbook

ROOT = pathlib.Path(__file__).resolve().parents[1]
XLSX = ROOT / "docs" / "files" / "SpaceX_Bull_Case_2.0.xlsx"
OUT = ROOT / "docs" / "model" / "tables"
IMG = ROOT / "docs" / "model" / "images"
SNAPSHOT = "Nov 2, 2026 snapshot"
SITE = "tyrel-beede.github.io/macrodials"

TITLES = {
    "summary": "SpaceX Bull Case 2.0 — the active scenario (Bull 2.0 base) against Maguire 1.0 and management",
    "snapshot": "SpaceX Bull Case 2.0 — four scenarios at the default inputs",
    "valuation": "SpaceX Bull Case 2.0 — the projection priced in shares",
}
SUBTITLES = {
    "summary": "$ billions unless noted · Nov 2, 2026 snapshot · scenario weights and readings from the macro-dials run of Nov 2",
    "snapshot": "$ billions unless noted · static values at the workbook's default inputs · weighted column uses the dashboard's H3 weights (A 66 / B 31 / C 3)",
    "valuation": "Method 1: a multiple on 2028 EBITDA, diluted for the bridge (end-2028, undiscounted). Method 2: DCF of the model's cash flows plus a steady-state terminal value at 10% / 4%",
}

CSS = """
body { margin: 0; background: #ffffff; font-family: -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2933; }
.card { display: inline-block; padding: 28px 32px 22px 32px; }
h1 { font-size: 20px; font-weight: 600; margin: 0 0 4px 0; letter-spacing: -0.01em; }
.sub { font-size: 12.5px; color: #5f6b7a; margin: 0 0 16px 0; max-width: 1100px; }
table { border-collapse: collapse; font-size: 14px; }
th { text-align: left; font-weight: 600; padding: 9px 14px; border-bottom: 2px solid #1f3864; background: #f3f5f8; vertical-align: bottom; }
th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
td { padding: 8px 14px; border-bottom: 1px solid #e3e7ec; vertical-align: top; }
td.txt { max-width: 340px; }
tr:nth-child(even) td { background: #fafbfc; }
td.unit, th.unit { color: #5f6b7a; white-space: nowrap; }
.foot { font-size: 11.5px; color: #7a8591; margin-top: 12px; display: flex; justify-content: space-between; gap: 40px; }
"""


def is_num(s):
    t = s.replace(",", "").replace("%", "").replace("x", "").replace("$", "").replace("(", "-").replace(")", "").strip()
    try:
        float(t); return True
    except ValueError:
        return False


def render_png(name, rows):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed — skipping", name + ".png"); return
    IMG.mkdir(parents=True, exist_ok=True)
    head, body = rows[0], rows[1:]
    ths = "".join(f'<th class="{"unit" if i == 1 else ("num" if i >= 2 else "")}">{html.escape(h)}</th>' for i, h in enumerate(head))
    trs = []
    for r in body:
        tds = []
        for i, v in enumerate(r):
            cls = "unit" if i == 1 else ("num" if (i >= 2 and (is_num(v) or v == "")) else "txt")
            tds.append(f'<td class="{cls}">{html.escape(v)}</td>')
        trs.append("<tr>" + "".join(tds) + "</tr>")
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="card" id="card"><h1>{html.escape(TITLES[name])}</h1><p class="sub">{html.escape(SUBTITLES[name])}</p>
<table><thead><tr>{ths}</tr></thead><tbody>{''.join(trs)}</tbody></table>
<div class="foot"><span>Source: SpaceX Bull Case 2.0 workbook ({SNAPSHOT}) — every number is an input or the arithmetic of inputs; not advice.</span><span>{SITE}</span></div></div>
</body></html>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=2)
        pg.set_content(doc)
        pg.locator("#card").screenshot(path=str(IMG / f"{name}.png"))
        b.close()


def fmt(cell):
    v = cell.value
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        nf = cell.number_format or ""
        if "%" in nf:
            return f"{v * 100:,.1f}%"
        if '"x"' in nf:
            return f"{v:,.1f}x"
        if "0.00" in nf:
            return f"{v:,.2f}"
        return f"{v:,.1f}"
    return str(v)


def find_row(ws, first_cell_text, after=1):
    for row in ws.iter_rows(min_row=after, max_row=ws.max_row, max_col=1):
        if row[0].value is not None and str(row[0].value).strip() == first_cell_text:
            return row[0].row
    raise SystemExit(f"row starting with {first_cell_text!r} not found in {ws.title}")


def dump(ws, header_row, n_rows, cols, name):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in range(header_row, header_row + n_rows + 1):
        vals = [fmt(ws.cell(row=r, column=c)).replace("|", "\\|") for c in cols]
        if r > header_row and all(v == "" for v in vals):
            continue
        rows.append(vals)
    with open(OUT / name, "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(rows[0]) + " |\n")
        f.write("| " + " | ".join("---" if i < 2 else "---:" for i in range(len(cols))) + " |\n")
        for vals in rows[1:]:
            f.write("| " + " | ".join(vals) + " |\n")
    render_png(name.replace(".md", ""), [[v.replace("\\|", "|") for v in r] for r in rows])


def main():
    if not XLSX.exists():
        sys.exit(f"missing {XLSX}")
    wb = load_workbook(XLSX, data_only=True)
    s = wb["Summary"]
    h = find_row(s, "Metric")
    dump(s, h, 13, range(1, 8), "summary.md")
    h2 = find_row(s, "Metric", after=h + 1)
    dump(s, h2, 19, range(1, 9), "snapshot.md")
    v = wb["Valuation"]
    hv = find_row(v, "Metric")
    dump(v, hv, 5, range(1, 9), "valuation.md")
    print("wrote", sorted(p.name for p in OUT.glob("*.md")), sorted(p.name for p in IMG.glob("*.png")) if IMG.exists() else [])


if __name__ == "__main__":
    main()
