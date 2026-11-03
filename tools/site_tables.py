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

DEFAULT_FOOTER = f"Source: SpaceX Bull Case 2.0 workbook ({SNAPSHOT}) — every number is an input or the arithmetic of inputs; not advice."
FOOTERS = {
    "balance-sheets": "Sources: SpaceX Q3 2026 release and Oct 20 call; Tesla Form 10-Q for the quarter ended Sept 30, 2026 and Q3 update; Electrek; Nov 2 closes from the data repository. Not advice.",
    "versions": "Sources: the Oct 20 call; Maguire's Oct 30 model as reconstructed in the article; the Bull Case 2.0 workbook; Tesla's Q3 2026 10-Q. Not advice.",
    "three-numbers": "Sources: the Oct 20 call and release; Maguire's Oct 30 model as reconstructed in the article; the Bull Case 2.0 workbook (Nov 2, 2026 snapshot). Not advice.",
    "provenance": "Sources: the Oct 20 call; Maguire's X posts of Oct 30 and Nov 1 as quoted in the article; the Bull Case 2.0 workbook. Not advice.",
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
td.txt { max-width: 360px; }
td.lab { white-space: nowrap; font-weight: 500; }
tr:nth-child(even) td { background: #fafbfc; }
td.unit, th.unit { color: #5f6b7a; white-space: nowrap; }
.foot { font-size: 11.5px; color: #7a8591; margin-top: 12px; display: flex; justify-content: space-between; gap: 40px; }
"""

# ---------------------------------------------------------------------------------------------
# Static tables for the orientation page (docs/model/three-numbers.md). Values are quoted from the
# Oct 20 call, Maguire's Oct 30 sheet as reconstructed in the article, and the workbook's defaults.
# ---------------------------------------------------------------------------------------------
STATIC = {
    "three-numbers": [
        ["Item", "The company (Oct 20 call)", "The bull — Maguire 1.0 (Oct 30)", "Model 2.0 base — Branch A (Nov 2)"],
        ["Compute online, end-2027", "\"Surprised if less than 13 GW\"; 20 GW of power planned", "10.2 GW", "10.0 GW"],
        ["Compute online, end-2028", "Not stated", "~22 GW implied by 2028 capex at $30B/GW", "15.0 GW — build throttled into the glut"],
        ["Revenue run-rate, end-2027", "\"$500 billion to $1 trillion\"", "~$420B", "$255B"],
        ["Revenue 2027 / 2028", "Q1-27 guided $33–37B; years not stated", "$274B / $731B", "$170B / $324B"],
        ["Adjusted EBITDA 2027 / 2028", "Not stated", "$196B / $536B", "$134B / $263B"],
        ["Capex", "Q4-26 guided $35–40B", "$88B / $290B / $369B (2026–28)", "Cash $264B / $187B in 2027–28, plus $86B / $45B of vendor leases"],
        ["Cash generation", "Build \"starts funding itself\" in 1H27", "Cash −$78B / −$123B / +$115B", "Free cash flow −$63B / +$72B; self-funding Q4-27, by throttling"],
        ["Price of compute", "Payback \"of less than a year\"", "$19.5B → $40B per GW-year on 100% of the fleet, then flat", "$6.50 → $11 → $8 per GPU-hour on the external half; Grok's revenue on the internal half"],
        ["Cost to build a gigawatt", "\"Slightly above the $30–50 per watt range\"", "$45B → $30B, booked when capacity arrives", "$42B → $34B, half paid a quarter ahead; power capex separate"],
        ["Internal vs external", "50/50 goal, 60/40 either way", "Not distinguished", "62% external today → 50%"],
        ["GPU life", "—", "16 years implied by 2028 depreciation", "4 years, vintage-tracked"],
        ["Orbital compute", "First Starmind flights 2027", "2.8 GW, $31B of revenue, 135 launches in 2028, no capex", "~0.5 GW by end-2028 with capex; MW per launch 8 → 12"],
        ["Terafab", "Test chip mid-2027; volume Q3–Q4 2028, \"large error bars\"", "Revenue in 2028, no capex", "Capex from 2027; no revenue in the horizon"],
        ["What $137.40 pays for 2028 EBITDA", "—", "3.4×", "7.6× (diluted)"],
    ],
    "provenance": [
        ["", "The company's numbers", "The bull's numbers", "The model's numbers"],
        ["Who and when", "Elon Musk, Gwynne Shotwell and CFO Bret Johnsen on the Q3 call, Oct 20, 2026, and the earnings release", "Shaun Maguire, partner at Sequoia Capital (a major SpaceX shareholder), posted to X on Oct 30, built over the preceding week", "The Bull Case 2.0 workbook, a Nov 2, 2026 snapshot built from the article's corrections to 1.0"],
        ["What kind of statement", "Targets and guidance. The near ones (Q4 capex, Q1 revenue) are guidance a company is held to; the far ones (13 GW, $500B–$1T) are ambitions", "A sketch built for a story: management's claims discounted by a quarter to a half, written in cells so they can be debated", "Conditional arithmetic: four scenarios, each the consequence of stated inputs"],
        ["Built for", "Investors and customers; setting the scale of the ambition", "Distilling \"something complicated into something that can at least be debated\"", "Orienting a reader on what the same ambition delivers when priced at market and depreciated honestly"],
        ["Strongest where", "Things the company controls: deployment speed (200,000 chips a month), launch, the near-term guide", "The four inputs its author named: gigawatts, revenue and capex per gigawatt, the Starship ramp, first orbital launches", "Structure: the internal/external split, the lag and ramp, the funding bridge, the depreciation"],
        ["Weakest where", "The far numbers require ~$16 per GPU-hour on the external fleet, 2.5× today's implied price, or a $100B-plus Grok business within 14 months", "100% of the fleet priced per watt with Grok on top; no construction lag; a 16-year GPU life; orbital and fab with no capex; launch with no depreciation", "Where it must guess: Grok's revenue, the prepayment multiple, the 2028 throttle, the external price path"],
        ["What moves it", "The Q4 call in late January: the 2027 gigawatt guide, the external share, revenue per gigawatt", "Nothing — it is a dated artifact; its author said the outputs are \"trivial\" given the inputs", "The blue cells on Assumptions; the dated tests on the Tests sheet"],
        ["Where it lives in the workbook", "Scenario 1 (Management as stated) and the calculator on Summary", "The 1.0 columns on Summary and Valuation; the Bridge sheet", "Scenarios 2–4 and every model sheet"],
    ],
    "scenarios": [
        ["Workbook scenario", "What it represents", "GW end-2027 / end-2028", "External price ($/GPU-hour)", "Revenue 2027 / 2028", "Self-funding", "Market cap ÷ 2028 EBITDA"],
        ["1 Management as stated", "The company's words reproduced: the price and prepayments the $500B run-rate requires", "13.1 / 29.8", "$10 → $16 → $15", "$254B / $742B", "Q4-27", "2.8×"],
        ["2 Bull 2.0 base (Branch A)", "The bull after the corrections; the dashboard's expansion-holds branch", "10.0 / 15.0", "$6.50 → $11 → $8", "$170B / $324B", "Q4-27 (by throttling)", "7.6×"],
        ["3 Branch B", "A capital-spending bust from 2027: prices fall, the build slows, the bridge stays open", "7.3 / 9.4", "$6.50 → $5.50 → $4", "$107B / $147B", "Not in the horizon", "19.0×"],
        ["4 Branch C", "A credit crunch: the funding window closes, the build throttles to a crawl", "5.3 / 6.3", "$6.50 → $4.50 → $3", "$91B / $103B", "Q4-27 (forced)", "27.4×"],
        ["Reference: Maguire 1.0", "The bull's own sheet, as reconstructed in the article", "10.2 / ~22", "$8.40 at 100% utilization on 100% of the fleet", "$274B / $731B", "Q1 2028", "3.4×"],
    ],
}
STATIC["balance-sheets"] = [
    ["Sept 30, 2026 unless noted", "SpaceX", "Tesla", "Combined (additive, illustrative)"],
    ["Cash and investments", "$89.9B cash and marketable securities", "$45.4B ($17.9B cash, $27.6B short-term investments)", "$135.3B"],
    ["Undrawn credit lines", "Not disclosed; \"several debt pools available\" (CFO)", "~$30B: $8B and $2B revolvers plus a delayed-draw term loan with step-downs and an 18-month draw window (signed Sept 29)", "~$30B disclosed"],
    ["Debt and finance leases", "$38.8B", "$9.5B ($1.4B current, $8.1B non-current)", "$48.3B"],
    ["Net cash", "$51.1B", "$35.9B", "$87.0B"],
    ["Known changes after quarter-end", "$40B GPU purchase restructured as an Apollo finance lease (Oct 26) — a lease liability of that order to come", "—", "Net cash nearer $47B once the lease is on the books"],
    ["Customer money in hand", "$17.5B of deferred revenue inside a $63B backlog ($42B due within a year)", "$3.3B of energy deferred revenue", "$20.8B"],
    ["Third-quarter revenue", "$14.6B (+161% y/y)", "$28.05B (flat y/y)", "$42.7B"],
    ["Third-quarter operating income", "$2.8B (adj. EBITDA $8.8B)", "$0.72B (2.6% margin, −56% y/y)", "$3.5B"],
    ["Third-quarter capex", "$19.6B", "$4.73B (nine months $13.0B)", "$24.3B"],
    ["Capex guidance", "Q4-26: $35–40B", "2026: \"more than $25 billion\" — at least ~$12B still to come in Q4", "Q4-26: ~$47–52B"],
    ["Free cash flow", "Negative through the build; self-funding claimed from 1H27", "$1.53B in Q3 (about −$1B underlying after working-capital timing, per Electrek's reading)", "—"],
    ["Shares outstanding", "13.58B (Sept 30)", "3.95B (Oct 15)", "Exchange ratio unknown"],
    ["Market capitalization, Nov 2 close", "$1.87T at $137.40", "$1.60T at $403.82", "$3.46T — SpaceX 54%, Tesla 46%"],
    ["Cross-holdings and intercompany", "Alphabet holds 551M shares (~4%); Tesla holds the stake at right", "$2.0B of SpaceX stock bought in Q1 at fair value (+$863M over nine months, −$142M in Q3); $588M billed to SpaceX for undelivered Megapacks, sitting in receivables and deferred revenue (per Electrek)", "Eliminated on combination"],
    ["Compute and silicon", "1.7 GW nameplate (2.5–3 by year-end); Terafab test chip mid-2027", "Cortex training clusters (>105 and 120 MW in production, 400 MW planned); AI5 chip; the fab partner", "Whose books Terafab sits on is one of the tests"],
]
STATIC["versions"] = [
    ["Set of numbers", "Entities included", "Revenue projected", "Capex and balance sheet", "Where in the workbook"],
    ["The company's guidance (Oct 20)", "SpaceX consolidated: Space, Connectivity, Super Intelligence (xAI since Feb 2026, X, Cursor). Tesla not included", "SpaceX's three segments only — the Q1-27 guide and the $500B–$1T run-rate are SpaceX numbers", "SpaceX's: $89.9B cash, $38.8B debt, Q4 capex $35–40B", "Scenario 1"],
    ["The bull's sheet (Maguire 1.0)", "SpaceX, plus orbital compute and a chip fab as revenue lines. Tesla absent", "SpaceX plus $31B of orbital revenue and fab revenue in 2028", "SpaceX's, with no capex for orbital or the fab", "Reference columns on Summary and Valuation; the Bridge sheet"],
    ["Model 2.0 (scenarios 2–4)", "SpaceX as reported, with Terafab and Starmind as capex programs. Tesla absent", "SpaceX's three segments; no Tesla revenue", "SpaceX's, with leases, prepayments, debt and equity in the bridge", "Compute, Starlink, Launch, Consolidated"],
    ["Model 2.0 with the Tesla toggle on", "As above, plus Tesla's liquidity as a funding source", "Unchanged — no Tesla revenue", "Adds ~$75B of Tesla cash and lines to the bridge; no Tesla capex, debt or shares", "Assumptions › Combination toggle; Consolidated › Tesla pool"],
    ["A combined SpaceX–Tesla company (the article's thesis)", "Both companies, with eliminations", "Adds Tesla's ~$112B run-rate at a 2–3% operating margin, and the robotaxi program", "Adds $45B cash, $30B of lines, $9.5B debt, >$25B a year of capex, and 3.95B shares at an exchange ratio the special committees would set", "Not modeled — see the page for what a full version needs"],
]
TITLES.update({
    "balance-sheets": "Two balance sheets and their sum",
    "versions": "Which company each set of numbers describes",
    "three-numbers": "The same company, three sets of numbers",
    "provenance": "What kind of number each one is",
    "scenarios": "The workbook's scenario selector, mapped to the three sets of numbers",
})
SUBTITLES.update({
    "balance-sheets": "SpaceX: Q3 2026 release and Oct 20 call. Tesla: Form 10-Q for the quarter ended Sept 30, 2026 (filed Oct 21) and the Q3 update; Electrek for the working-capital and Megapack readings. Combined column is a plain sum with no synergies, no deal premium and no accounting for the exchange ratio",
    "versions": "All revenue projections on this site are SpaceX-only, including xAI; Tesla enters the workbook as money, not as revenue",
    "three-numbers": "Company: Q3 2026 call and release (Oct 20). Bull: Maguire's Oct 30 model as reconstructed in \"Better Together Than Alone\". Model 2.0: the workbook's Branch A defaults, Nov 2, 2026 snapshot",
    "provenance": "Three kinds of statement, not three forecasts of the same thing",
    "scenarios": "Assumptions sheet, cell D4. Prices are the external fleet's $ per GPU-hour at Q4-26 → Q4-27 → Q4-28; market cap at the Nov 2 close ($137.40 × 13.58B) on end-2028 diluted shares",
})


def write_static():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in STATIC.items():
        with open(OUT / f"{name}.md", "w", encoding="utf-8") as f:
            f.write("| " + " | ".join(rows[0]) + " |\n")
            f.write("| " + " | ".join("---" for _ in rows[0]) + " |\n")
            for vals in rows[1:]:
                f.write("| " + " | ".join(v.replace("|", "\\|") for v in vals) + " |\n")
        render_png(name, rows, text_table=True)


def is_num(s):
    t = s.replace(",", "").replace("%", "").replace("x", "").replace("$", "").replace("(", "-").replace(")", "").strip()
    try:
        float(t); return True
    except ValueError:
        return False


def render_png(name, rows, text_table=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed — skipping", name + ".png"); return
    IMG.mkdir(parents=True, exist_ok=True)
    head, body = rows[0], rows[1:]
    ncol = len(head)
    # a column is numeric when most of its non-empty cells are numbers; the unit column is column 1 of a data table
    numeric = []
    for i in range(ncol):
        vals = [r[i] for r in body if r[i] != ""]
        numeric.append(bool(vals) and sum(is_num(v) for v in vals) >= 0.6 * len(vals) and not (text_table and i == 0))
    def hcls(i):
        if not text_table and i == 1: return "unit"
        return "num" if numeric[i] else ""
    ths = "".join(f'<th class="{hcls(i)}">{html.escape(h)}</th>' for i, h in enumerate(head))
    trs = []
    for r in body:
        tds = []
        for i, v in enumerate(r):
            if not text_table and i == 1: cls = "unit"
            elif numeric[i] and (is_num(v) or v == ""): cls = "num"
            else: cls = "txt" if i > 0 else "lab"
            tds.append(f'<td class="{cls}">{html.escape(v)}</td>')
        trs.append("<tr>" + "".join(tds) + "</tr>")
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="card" id="card"><h1>{html.escape(TITLES[name])}</h1><p class="sub">{html.escape(SUBTITLES[name])}</p>
<table><thead><tr>{ths}</tr></thead><tbody>{''.join(trs)}</tbody></table>
<div class="foot"><span>{html.escape(FOOTERS.get(name, DEFAULT_FOOTER))}</span><span>{SITE}</span></div></div>
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
    write_static()
    print("wrote", sorted(p.name for p in OUT.glob("*.md")), sorted(p.name for p in IMG.glob("*.png")) if IMG.exists() else [])


if __name__ == "__main__":
    main()
