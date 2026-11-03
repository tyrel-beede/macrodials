# The data feed

The data lives in a separate repository, [tyrel-beede/fred_data_feed](https://github.com/tyrel-beede/fred_data_feed), which pulls the dashboard's inputs on a schedule with GitHub Actions and commits them as plain CSV and JSON under `data/`. Nothing is served from a database; the files are the record. This site holds the articles and the models; the feed stays where it is.

## What is pulled

| Group | Source | Examples |
| --- | --- | --- |
| Rates, inflation, credit, activity | FRED | Treasury yields and real yields, breakevens and the 5y5y forward, ICE BofA option-adjusted spreads by rating tier, jobless claims, C&I loans, SLOOS, financial-conditions and liquidity series |
| Equity prices and breadth | Yahoo chart API; S&P 500 constituents | Daily closes for the lens names, the index funds and the Korean suppliers; advance/decline, members above moving averages, new highs and lows, drawdown distributions |
| Option surfaces | CBOE delayed quotes | Chains and implied-volatility surfaces for 17 names, from which the dashboard computes event-implied moves and skews |
| Positioning and flows | CFTC, New York Fed, Treasury FiscalData | Commitments of Traders (TFF and disaggregated), primary-dealer positions, auction results and the Treasury cash balance |
| Narrative | GDELT | Volume and tone timelines for a fixed set of queries (AI bubble, data-center capex, term premium, Hormuz), in their own job |

## Schedule

Two main pulls on weekdays (22:40 and 13:10 UTC) and two GDELT pulls offset by 35 minutes, each committing whatever it fetched and writing a status file (`data/_status_main.json`, `data/_status_gdelt.json`) that lists what succeeded and what failed. The dashboard reads the status file first.

## What is not served

The ICE BofA spread series carry FRED's "internal use only" note. They feed the dashboard's charts and readings but are not published as files from this site.

## How the dashboard uses it

The `/macro-dials` run reads the repository, scores the event dials, reads the fields, equity lenses, flows and discourse, runs the convergence check and computes a Monte Carlo cone of branch weights — A (expansion holds), B (capital-spending bust), C (bond-market crunch) — over two horizons. Each run is logged with its date and inputs, and the articles cite the run they were built from.
