"""Build the Forecasts section (docs/forecasts/) from the data repository's materialized state.

Usage: python tools/forecasts.py [--feed-dir PATH]

Reads dials/state/ from a clone of tyrel-beede/fred_data_feed (cloned shallow into a temp folder when
--feed-dir is not given) and writes:

  docs/forecasts/index.md            the page: charts (image per color scheme) with a selectable text
                                     version under each, the open-forecast table, the resolved ledger,
                                     the scoreboard by kind and by lead-time bucket, the pig tally
  docs/forecasts/images/*.png        the charts, light and dark variants

Nothing here is computed from the runs; every number is read from state/ (weights.csv, standoff.csv,
ledger.json, scoreboard.json, pigs.json, latest.json), which tools/materialize.py in the data repository
rebuilds from the run folders. The page links every run id to its folder on GitHub.
"""
import argparse, csv, datetime as dt, json, math, pathlib, re, shutil, subprocess, sys, tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import dates as mdates

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "forecasts"
IMG = OUT / "images"
FEED_REPO = "tyrel-beede/fred_data_feed"
FEED_URL = f"https://github.com/{FEED_REPO}.git"
RUN_URL = f"https://github.com/{FEED_REPO}/tree/main/dials/runs/"

# Colors validated with the dataviz palette validator against each surface (both modes pass CVD and
# normal-vision floors; the light-mode contrast warning is answered by direct labels and the text tables).
THEMES = {
    "light": {"surface": "#f7f6f2", "ink": "#1a1f2b", "muted": "#6b7280", "grid": "#e5e3dc",
              "A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a",
              "R+": "#1baf7a", "R-": "#2a78d6", "F": "#eda100", "E": "#e34948"},
    "dark": {"surface": "#0b1020", "ink": "#e6e8ee", "muted": "#aeb6c7", "grid": "#1e2a44",
             "A": "#3987e5", "B": "#d95926", "C": "#199e70",
             "R+": "#199e70", "R-": "#3987e5", "F": "#c98500", "E": "#e66767"},
}
plt.rcParams.update({"font.family": ["IBM Plex Sans", "DejaVu Sans"], "font.size": 11, "axes.titlesize": 12,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none"})


def parse_dt(s):
    """run_at values are ISO with offset, or a bare date for seeded event rows."""
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        m = re.match(r"\d{4}-\d{2}-\d{2}", s)
        return dt.datetime.fromisoformat(m.group(0)) if m else None


def naive(d):
    return d.replace(tzinfo=None) if d and d.tzinfo else d


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def style(ax, t):
    ax.set_facecolor(t["surface"])
    ax.figure.set_facecolor(t["surface"])
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["grid"])
    ax.tick_params(colors=t["muted"], labelsize=9)
    ax.yaxis.grid(True, color=t["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_color(t["muted"])
    ax.title.set_color(t["ink"])


def chart_weights(rows, t, path, horizon):
    rows = [r for r in rows if fnum(r[f"{horizon}_A"]) is not None]
    x = [naive(parse_dt(r["run_at"])) for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 4.6), dpi=160)
    style(ax, t)
    lo = [fnum(r[f"{horizon}_B_q25"]) for r in rows]
    hi = [fnum(r[f"{horizon}_B_q75"]) for r in rows]
    band = [(xi, a, b) for xi, a, b in zip(x, lo, hi) if a is not None and b is not None]
    if band:
        ax.fill_between([b[0] for b in band], [b[1] for b in band], [b[2] for b in band], color=t["B"], alpha=0.18, linewidth=0, label="B interquartile band")
    for k in ("A", "B", "C"):
        y = [fnum(r[f"{horizon}_{k}"]) for r in rows]
        ax.plot(x, y, color=t[k], linewidth=2, marker="o", markersize=5, markeredgecolor=t["surface"], markeredgewidth=1.2, label=f"Branch {k}")
        ax.annotate(f"{k} {y[-1]:.0f}", (x[-1], y[-1]), xytext=(8, 0), textcoords="offset points", va="center", color=t["ink"], fontsize=10)
    hand = [i for i, r in enumerate(rows) if str(r.get("hand_weights")).lower() == "true"]
    for i in hand:
        ax.plot([x[i]], [fnum(rows[i][f"{horizon}_A"])], marker="o", markersize=9, markerfacecolor="none", markeredgecolor=t["muted"], linestyle="none")
    ax.set_ylim(0, 100)
    ax.set_ylabel("weight, %", color=t["muted"])
    ax.set_title(f"Branch weights at {horizon} by run" + (" — hollow ring: hand-set weights before the cone" if hand else ""), loc="left", color=t["ink"])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False, fontsize=9, labelcolor=t["ink"])
    fig.tight_layout()
    fig.savefig(path, facecolor=t["surface"])
    plt.close(fig)


def chart_state(rows, t, path):
    rows = [r for r in rows if fnum(r["s2"]) is not None]
    if not rows:
        return False
    x = [naive(parse_dt(r["run_at"])) for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 4.0), dpi=160)
    style(ax, t)
    ax.axhspan(0, 0.25, color=t["A"], alpha=0.08, linewidth=0)
    ax.axhspan(0.75, 1.0, color=t["B"], alpha=0.08, linewidth=0)
    ax.axhline(0.25, color=t["grid"], linewidth=1); ax.axhline(0.75, color=t["grid"], linewidth=1)
    for key, lab, col, ls in (("s2", "s₂ = P(B at H2 ≥ 20)", t["B"], "-"), ("s3", "s₃ = P(B at H3 ≥ 30)", t["C"], "--")):
        y = [fnum(r[key]) for r in rows]
        ax.plot(x, y, color=col, linewidth=2, linestyle=ls, marker="o", markersize=5, markeredgecolor=t["surface"], label=lab)
    for xi, r in zip(x, rows):
        ax.annotate(r["state"], (xi, fnum(r["s2"])), xytext=(0, 10), textcoords="offset points", ha="center", color=t["ink"], fontsize=8.5)
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of cone paths", color=t["muted"])
    ax.set_title("The numeric state: A below 0.25 on both · B-leaning at s₂ ≥ 0.75 · transition between", loc="left", color=t["ink"])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False, fontsize=9, labelcolor=t["ink"])
    fig.tight_layout()
    fig.savefig(path, facecolor=t["surface"])
    plt.close(fig)
    return True


def chart_standoff(rows, t, path):
    if not rows:
        return False
    x = [naive(parse_dt(r["run_at"])) for r in rows]
    fig, ax = plt.subplots(figsize=(8.4, 4.2), dpi=160)
    style(ax, t)
    for k, col in (("Rp", "R+"), ("Rm", "R-"), ("F", "F"), ("E", "E")):
        y = [fnum(r[f"H2_{k}"]) for r in rows]
        ax.plot(x, y, color=t[col], linewidth=2, marker="o", markersize=5, markeredgecolor=t["surface"], label={"R+": "R+ settlement", "R-": "R− thin deal", "F": "F frozen", "E": "E escalation"}[col])
        ax.annotate(f"{col} {y[-1]:.0f}", (x[-1], y[-1]), xytext=(8, 0), textcoords="offset points", va="center", color=t["ink"], fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_ylabel("weight, %", color=t["muted"])
    ax.set_title("Standoff branch weights at H2 by run", loc="left", color=t["ink"])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4, frameon=False, fontsize=9, labelcolor=t["ink"])
    fig.tight_layout()
    fig.savefig(path, facecolor=t["surface"])
    plt.close(fig)
    return True


def picture(name, alt, sub):
    return (f"![{alt}](images/{name}-light.png#only-light){{ .chart }}\n"
            f"![{alt}](images/{name}-dark.png#only-dark){{ .chart }}\n"
            f"<p class=\"chart-sub\">{sub}</p>\n\n")


def details(title, table):
    indented = "\n".join("    " + l for l in table.split("\n"))
    return f'??? note "{title}"\n{indented}\n\n'


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join("" if v is None else str(v).replace("|", "\\|") for v in r) + " |")
    return "\n".join(out)


def run_link(rid):
    """Link a run id to its folder; a bare date (a migrated registration without a run folder) stays text."""
    if not rid:
        return ""
    return f"[{rid}]({RUN_URL}{rid})" if re.match(r"\d{4}-\d{2}-\d{2}T\d{4}-", rid) else str(rid)


def id_date(fid):
    m = re.match(r"[FS]-(\d{8})", fid or "")
    return dt.date(int(m.group(1)[:4]), int(m.group(1)[4:6]), int(m.group(1)[6:8])) if m else None


def resolve_date(s):
    m = re.search(r"\d{4}-\d{2}-\d{2}", s or "")
    return dt.date.fromisoformat(m.group(0)) if m else None


def lead_days(f):
    """Days from registration to resolution. The date inside an id (F-20261209-…) is the resolution date,
    so the registration date comes from the registering run's id; migrated forks without one are unknown."""
    if f.get("lead_days") is not None:
        return int(f["lead_days"]), "logged"
    reg = f.get("first_registered_run") or f.get("registered_run") or ""
    a, b = resolve_date(reg), resolve_date(f.get("resolves"))
    if a and b:
        return (b - a).days, "from registering run"
    return None, ""


def bucket(days):
    if days is None:
        return "unknown"
    return "≤ 7 d" if days <= 7 else "8–30 d" if days <= 30 else "31–90 d" if days <= 90 else "> 90 d"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed-dir")
    a = ap.parse_args()
    tmp = None
    if a.feed_dir:
        feed = pathlib.Path(a.feed_dir)
    else:
        tmp = tempfile.mkdtemp(prefix="feed-")
        subprocess.run(["git", "clone", "-q", "--depth", "1", FEED_URL, tmp], check=True)
        feed = pathlib.Path(tmp)
    state = feed / "dials" / "state"
    if not (state / "latest.json").exists():
        print("no dials/state in the data repository — Forecasts page not rebuilt"); return
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=feed, capture_output=True, text=True).stdout.strip()

    def rd_csv(name):
        with open(state / name, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    weights = rd_csv("weights.csv"); standoff = rd_csv("standoff.csv")
    ledger = json.load(open(state / "ledger.json")); board = json.load(open(state / "scoreboard.json"))
    latest = json.load(open(state / "latest.json"))
    pigs = json.load(open(state / "pigs.json")) if (state / "pigs.json").exists() else None

    IMG.mkdir(parents=True, exist_ok=True)
    have_state = have_standoff = False
    for mode, t in THEMES.items():
        chart_weights(weights, t, IMG / f"weights-h2-{mode}.png", "H2")
        chart_weights(weights, t, IMG / f"weights-h3-{mode}.png", "H3")
        have_state = chart_state(weights, t, IMG / f"state-{mode}.png")
        have_standoff = chart_standoff(standoff, t, IMG / f"standoff-{mode}.png")

    today = dt.date.today()
    forecasts = ledger["forecasts"]
    opens = sorted([f for f in forecasts if f["status"] == "open"], key=lambda f: (resolve_date(f.get("resolves")) or dt.date.max, f["id"]))
    resolved = sorted([f for f in forecasts if f["status"] == "resolved"], key=lambda f: (f["resolution"].get("resolved_in_run") or "", f["id"]))

    # scoreboard by lead-time bucket, recomputed here from the ledger (the same Brier the scoreboard logs)
    by_bucket = {}
    for f in resolved:
        d, _ = lead_days(f)
        by_bucket.setdefault(bucket(d), []).append(f["resolution"]["brier_recomputed"])

    md = []
    md.append("---\ndescription: The dashboard's forecasts, scored — branch weights by run, the numeric state, every open forecast with its lead time, the resolved ledger and the rolling Brier score.\ncard: forecasts\nkicker: Forecasts · scored, not asserted\n---\n\n")
    md.append("# Forecasts\n\n")
    md.append(f"*Every probability the macro dashboard publishes is logged with an ID, a criterion a stranger could score, and a date — then scored. "
              f"This page is rebuilt from the data repository's materialized state (`dials/state/` at commit `{commit}`); "
              f"every run id links to the folder holding the readings, the cone specification and the forecasts behind it.*\n\n")
    d_latest = latest.get("dials", {}); s_latest = latest.get("standoff", {}); c_latest = latest.get("column", {})
    last_w = next((r for r in reversed(weights) if fnum(r["H2_A"]) is not None), None)
    sb = board.get("all", {}).get("dials", {})
    md.append("## Where the dashboard stands\n\n")
    if last_w:
        md.append(f"- Latest dials run: {run_link(d_latest.get('run_id'))} ({last_w.get('mode')}), state **{last_w.get('state') or 'n/a'}**"
                  + (f" (s₂ {last_w['s2']}, s₃ {last_w['s3']})" if fnum(last_w.get("s2")) is not None else "") + "\n")
        md.append(f"- H2 weights A / B / C: **{fnum(last_w['H2_A']):.0f} / {fnum(last_w['H2_B']):.0f} / {fnum(last_w['H2_C']):.0f}**"
                  + (f", B interquartile band {fnum(last_w['H2_B_q25']):.0f}–{fnum(last_w['H2_B_q75']):.0f}" if fnum(last_w.get("H2_B_q25")) is not None else "")
                  + (f"; H3 {fnum(last_w['H3_A']):.0f} / {fnum(last_w['H3_B']):.0f} / {fnum(last_w['H3_C']):.0f}" if fnum(last_w.get("H3_A")) is not None else "") + "\n")
        if fnum(last_w.get("P_B_conf")) is not None:
            md.append(f"- P(B confirmed by the H2 date) {fnum(last_w['P_B_conf']):.2f} · P(C confirmed) {fnum(last_w['P_C_conf']):.2f} · martingale drift {fnum(last_w['drift_B']):+.1f} pts\n")
    if sb.get("n"):
        md.append(f"- Brier score, all resolved dials forecasts: **{sb['brier_mean']:.3f}** (n = {sb['n']}; last 20: {sb['brier_last20']:.3f}); mean log score {sb['log_score_mean']:.3f}. A coin flip scores 0.25; lower is better.\n")
    if standoff:
        s = standoff[-1]
        md.append(f"- Latest standoff run: {run_link(s_latest.get('run_id'))}, H2 R+ / R− / F / E: **{s['H2_Rp']} / {s['H2_Rm']} / {s['H2_F']} / {s['H2_E']}**\n")
    if c_latest.get("run_id"):
        md.append(f"- Latest column: {run_link(c_latest['run_id'])}\n")
    md.append(f"- Open forecasts: {ledger['n_open']} · resolved: {ledger['n_resolved']}\n\n")

    md.append("## Branch weights by run\n\n")
    md.append("The dashboard sorts the next six weeks (H2) and the next quarter (H3) into three branches — **A** grow out of it, **B** capex bust, **C** debt crunch — and moves the weights only by likelihood ratios on scored events. "
              "From Oct 30 the weights are the medians of a Monte Carlo cone and the shaded band is B's interquartile range; the earliest points are hand-set weights from before the cone existed.\n\n")
    md.append(picture("weights-h2", "Branch weights at H2 by run", "Medians of the cone's layer 1; the band is the 25th–75th percentile of B. Source: dials/state/weights.csv."))
    md.append(picture("weights-h3", "Branch weights at H3 by run", "Same, at the one-quarter horizon."))
    wt = md_table(["Run", "Mode", "H2 A", "H2 B", "H2 C", "B IQR", "H3 A", "H3 B", "H3 C", "P(B conf)", "P(C conf)", "State", "s₂", "s₃"],
                  [[run_link(r["run_id"]), r["mode"], r["H2_A"], r["H2_B"], r["H2_C"],
                    f"{r['H2_B_q25']}–{r['H2_B_q75']}" if r["H2_B_q25"] else "", r["H3_A"], r["H3_B"], r["H3_C"], r["P_B_conf"], r["P_C_conf"], r["state"], r["s2"], r["s3"]] for r in weights])
    md.append(details("Text version (selectable)", wt))

    if have_state:
        md.append("## The numeric state\n\n")
        md.append("The state label is computed from the cone's band, not asserted from the median: s₂ is the share of simulated paths with B at or above 20 at H2, s₃ the share with B at or above 30 at H3. "
                  "Below 0.25 on both the state is **A**; s₂ at or above 0.75 is **B-leaning**; anything between is **transition**. Flips are logged as information, not smoothed away.\n\n")
        md.append(picture("state", "The numeric state by run", "Shares of cone paths above the B lines, with the label each run carried. Source: dials/state/weights.csv."))

    md.append("## Open forecasts\n\n")
    md.append("Each line is a probability the dashboard put on a dated, scorable outcome. *Lead* is the number of days between registration and the resolution date — the scoreboard is read by lead-time bucket, because a forecast made a day ahead and one made a quarter ahead are not the same skill.\n\n")
    md.append(md_table(["ID", "p", "Resolves", "Lead (d)", "Criterion", "Registered in"],
                       [[f["id"], f["p"], f.get("resolves") or "", (lambda d: f"{d[0]}" if d[0] is not None else "")(lead_days(f)), (f.get("criterion") or ""), run_link(f.get("first_registered_run") or f.get("registered_run"))] for f in opens]) + "\n\n")

    md.append("## Resolved ledger\n\n")
    md.append("Brier = (p − outcome)², so a confident right call scores near 0 and a confident wrong one near 1. Both the logged and the recomputed Brier are kept; a mismatch is listed below the table.\n\n")
    md.append(md_table(["ID", "p", "Outcome", "Brier", "Log score", "Resolved in"],
                       [[f["id"], f["p"], f["resolution"]["outcome"], f["resolution"]["brier_recomputed"], f["resolution"].get("log_score"), run_link(f["resolution"].get("resolved_in_run"))] for f in resolved]) + "\n\n")
    mm = board.get("brier_logged_vs_recomputed_mismatches", [])
    md.append(("Logged-vs-recomputed mismatches: " + ", ".join(f"{m['id']} ({m['logged']} vs {m['recomputed']})" for m in mm) if mm else "Logged and recomputed Brier scores agree on every resolved forecast.") + "\n\n")

    md.append("## Scoreboard\n\n")
    md.append(md_table(["Kind", "n", "Brier (all)", "Brier (last 20)", "Mean log score"],
                       [[k, v.get("n", 0), v.get("brier_mean", ""), v.get("brier_last20", ""), v.get("log_score_mean", "")] for k, v in sorted(board.get("all", {}).items())]) + "\n\n")
    md.append("By lead-time bucket (dials and standoff together; lead taken from the forecast's registration date where the run folders carry it, otherwise from the date of the run that registered it; migrated forks without one are *unknown*):\n\n")
    order = ["≤ 7 d", "8–30 d", "31–90 d", "> 90 d", "unknown"]
    md.append(md_table(["Lead bucket", "n", "Mean Brier"],
                       [[b, len(by_bucket[b]), round(sum(by_bucket[b]) / len(by_bucket[b]), 3)] for b in order if b in by_bucket]) + "\n\n")

    if standoff:
        md.append("## Standoff branches\n\n")
        md.append("The Hormuz standoff is the one variable that decides which branch the macro cone lands in, so it has its own cone: **R+** settlement with a security regime, **R−** thin deal, **F** frozen harassment, **E** escalation.\n\n")
        md.append(picture("standoff", "Standoff branch weights at H2 by run", "Weights rounded to 5; the exact odds-form values are in each run's cone.json. Source: dials/state/standoff.csv."))
        md.append(details("Text version (selectable)", md_table(["Run", "H2 R+", "H2 R−", "H2 F", "H2 E", "H3 R+", "H3 R−", "H3 F", "H3 E"],
                                                                 [[run_link(r["run_id"]), r["H2_Rp"], r["H2_Rm"], r["H2_F"], r["H2_E"], r["H3_Rp"], r["H3_Rm"], r["H3_F"], r["H3_E"]] for r in standoff])))

    if pigs:
        tl = pigs.get("tally_recomputed") or {}
        md.append("## The Pigs ledger\n\n")
        md.append(f"The column's asymmetries, graded after the fact: **{tl.get('paid', 0)} paid / {tl.get('cost', 0)} cost / {tl.get('void', 0)} void**, {pigs.get('n_open', 0)} open. Hit rate is not the point; the payoff shape is — a 40% hit rate with 3:1 payoffs is a good record and a 70% hit rate with 1:3 payoffs is not.\n\n")
        md.append(md_table(["ID", "Grade", "Basis", "Graded on"], [[g["id"], g.get("grade"), g.get("basis", ""), g.get("graded_on", "")] for g in pigs.get("graded", [])]) + "\n\n")
        md.append(details("Open pigs", md_table(["ID", "Resolves", "Criterion"], [[p["id"], p.get("resolves", ""), p.get("criterion", "")] for p in pigs.get("open", [])])))

    md.append(f"*Rebuilt {today.isoformat()} from `{FEED_REPO}` commit `{commit}`. Analysis, not advice. Probabilities are the dashboard's or the market's, never a conviction.*{{ .release-stamp }}\n")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.md").write_text("".join(md), encoding="utf-8")
    print("wrote", OUT / "index.md", "and", len(list(IMG.glob("*.png"))), "images from", commit)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
