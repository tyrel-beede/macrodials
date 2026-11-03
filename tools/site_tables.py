"""Export the display tables of the Bull Case 2.0 workbook as Markdown tables for the site.

Reads docs/files/SpaceX_Bull_Case_2.0.xlsx (cached values, so the file must have been saved after a
recalculation) and writes docs/model/tables/*.md, which the Models page includes with the snippets
syntax (--8<-- "model/tables/summary.md"). Run by the site workflow before `mkdocs build`; safe to run locally.
"""
import pathlib, sys
from openpyxl import load_workbook

ROOT = pathlib.Path(__file__).resolve().parents[1]
XLSX = ROOT / "docs" / "files" / "SpaceX_Bull_Case_2.0.xlsx"
OUT = ROOT / "docs" / "model" / "tables"


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
    print("wrote", sorted(p.name for p in OUT.glob("*.md")))


if __name__ == "__main__":
    main()
