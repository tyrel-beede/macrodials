---
description: The dashboard's forecasts, scored — branch weights by run, the numeric state, every open forecast with its lead time, the resolved ledger and the rolling Brier score.
card: forecasts
kicker: Forecasts · scored, not asserted
---

# Forecasts

*Every probability the macro dashboard publishes is logged with an ID, a criterion a stranger could score, and a date — then scored. This page is rebuilt from the data repository's materialized state (`dials/state/` at commit `dbefb0a`); every run id links to the folder holding the readings, the cone specification and the forecasts behind it.*

## Where the dashboard stands

- Latest dials run: [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) (lite), state **TRANSITION** (s₂ 0.46, s₃ 0.52)
- H2 weights A / B / C: **78 / 19 / 2**, B interquartile band 12–30; H3 66 / 31 / 3
- P(B confirmed by the H2 date) 0.17 · P(C confirmed) 0.13 · martingale drift -1.0 pts
- Brier score, all resolved dials forecasts: **0.121** (n = 12; last 20: 0.121); mean log score -0.412. A coin flip scores 0.25; lower is better.
- Latest standoff run: [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff), H2 R+ / R− / F / E: **10 / 20 / 25 / 45**
- Latest column: [2026-10-30T2000-column](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T2000-column)
- Open forecasts: 34 · resolved: 12

## Branch weights by run

The dashboard sorts the next six weeks (H2) and the next quarter (H3) into three branches — **A** grow out of it, **B** capex bust, **C** debt crunch — and moves the weights only by likelihood ratios on scored events. From Oct 30 the weights are the medians of a Monte Carlo cone and the shaded band is B's interquartile range; the earliest points are hand-set weights from before the cone existed.

![Branch weights at H2 by run](images/weights-h2-light.png#only-light){ .chart }
![Branch weights at H2 by run](images/weights-h2-dark.png#only-dark){ .chart }
<p class="chart-sub">Medians of the cone's layer 1; the band is the 25th–75th percentile of B. Source: dials/state/weights.csv.</p>

![Branch weights at H3 by run](images/weights-h3-light.png#only-light){ .chart }
![Branch weights at H3 by run](images/weights-h3-dark.png#only-dark){ .chart }
<p class="chart-sub">Same, at the one-quarter horizon.</p>

??? note "Text version (selectable)"
    | Run | Mode | H2 A | H2 B | H2 C | B IQR | H3 A | H3 B | H3 C | P(B conf) | P(C conf) | State | s₂ | s₃ |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
    | [2026-10-18T0823-dials](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-18T0823-dials) | full | 70 | 20 | 10 |  |  |  |  |  |  |  |  |  |
    | [2026-10-27T0817-dials](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-27T0817-dials) | full | 60 | 35 | 5 |  | 45 | 50 | 5 |  |  |  |  |  |
    | [2026-10-28T0000-dials-event](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-28T0000-dials-event) | event | 65 | 30 | 5 |  | 50 | 45 | 5 |  |  |  |  |  |
    | [2026-10-30T1445-dials](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1445-dials) | full | 82.8 | 13.2 | 3.4 | 9.8–19 | 72.7 | 22.7 | 3.8 | 0.164 | 0.1 |  |  |  |
    | [2026-10-30T1640-dials](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1640-dials) | full | 86.4 | 10.5 | 2.6 | 7.4–16.4 | 77.8 | 18.5 | 3 | 0.156 | 0.128 | A | 0.19 | 0.22 |
    | [2026-11-02T1855-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1855-dials-lite) | lite | 86.8 | 10.1 | 2.7 | 6.8–16.4 | 78.6 | 17.7 | 3.1 | 0.163 | 0.127 | A | 0.19 | 0.21 |
    | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) | lite | 78.5 | 18.7 | 2.4 | 12.2–30.1 | 66.3 | 30.7 | 2.6 | 0.166 | 0.129 | TRANSITION | 0.46 | 0.52 |

## The numeric state

The state label is computed from the cone's band, not asserted from the median: s₂ is the share of simulated paths with B at or above 20 at H2, s₃ the share with B at or above 30 at H3. Below 0.25 on both the state is **A**; s₂ at or above 0.75 is **B-leaning**; anything between is **transition**. Flips are logged as information, not smoothed away.

![The numeric state by run](images/state-light.png#only-light){ .chart }
![The numeric state by run](images/state-dark.png#only-dark){ .chart }
<p class="chart-sub">Shares of cone paths above the B lines, with the label each run carried. Source: dials/state/weights.csv.</p>

## Open forecasts

Each line is a probability the dashboard put on a dated, scorable outcome. *Lead* is the number of days between registration and the resolution date — the scoreboard is read by lead-time bucket, because a forecast made a day ahead and one made a quarter ahead are not the same skill.

| ID | p | Resolves | Lead (d) | Criterion | Registered in |
|---|---|---|---|---|---|
| S-20261103-STRIKE | 0.1 | 2026-11-03 | 4 | US or Israeli strikes on Iranian territory before Nov 3 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| F-20261104-OBDC | 0.6 | 2026-11-04 | 8 | Q3 non-accruals at FV above Q2's | 2026-10-27 |
| F-20261104-REFUND | 0.25 | 2026-11-04 | 8 | coupon sizes increased or a bills shift | 2026-10-27 |
| S-20261109-YANBU | 0.3 | 2026-11-09 | 10 | Saudi-acknowledged damage to the East-West line or Yanbu export facilities Oct 20-Nov 9 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| F-20261110-10Y | 0.15 | 2026-11-10 | 8 | 10y auction tail >= 2 bp | 2026-11-02 |
| F-20261110-CPI | 0.3 | 2026-11-10T08:30-05:00 | 14 | Oct core CPI m/m >= 0.4 | 2026-10-27 |
| F-20261110-CRWV | 0.3 | 2026-11-10T17:00-05:00 | 14 | Q3 discloses a customer-contract renegotiation, deferral or cancellation | 2026-10-27 |
| F-20261112-30Y | 0.2 | 2026-11-12 | 16 | 30y auction tail >= 2 bp | 2026-10-27 |
| F-20261117-NVDA-AR | 0.6 | 2026-11-17 | 21 | AR growth > revenue growth again | 2026-10-27 |
| F-20261117-NVDA-GUIDE | 0.25 | 2026-11-17 after the close | 21 | Q4 revenue guide below the ~$110B implied consensus | 2026-10-27 |
| F-20261118-20Y | 0.2 | 2026-11-18 | 16 | 20y auction tail >= 2 bp | 2026-11-02 |
| F-20261120-ANTHROPIC | 0.42 | 2026-11-30 | 34 | IPO delayed past Nov 30, downsized below the ~$75B reported raise, or priced below the top of the initial range | 2026-10-27 |
| S-20261130-STRIKE | 0.45 | 2026-11-30 | 31 | US or Israeli strikes on Iranian territory Nov 4-30 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| S-20261204-ISRAELGOV | 0.3 | 2026-12-04 | 35 | a new Israeli government sworn in by Dec 4 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| F-20261027-B-H2 | 0.35 | 2026-12-09 | 43 | B confirmed by Dec 9 (10/27 line, scored alongside) | 2026-10-27 |
| F-20261027-C-H2 | 0.05 | 2026-12-09 | 43 | C confirmed by Dec 9 (10/27 line) | 2026-10-27 |
| F-20261209-B-CONF | 0.17 | 2026-12-09 | 37 | B confirmed by Dec 9 (two of the five B elements) | 2026-11-02 |
| F-20261209-C-CONF | 0.13 | 2026-12-09 | 37 | C confirmed by Dec 9 | 2026-11-02 |
| F-20261209-FOMC | 0.15 | 2026-12-09 | 43 | hike with claims 4-wk > +10% from the 189k low (LR-carrying form; P(hike) market 0.77 on 11/2) | 2026-10-27 |
| F-20261209-HORMUZ | 0.38 | 2026-12-09 | 43 | signing by Dec 9 | 2026-10-27 |
| F-20261209-IG100 | 0.45 | 2026-12-09 | 43 | IG OAS >= 100 bp on any day by Dec 9 | 2026-10-27 |
| F-20261209-IG115 | 0.14 | 2026-12-09 | 43 | IG OAS >= 115 bp on any day by Dec 9 | 2026-10-27 |
| F-20261209-OILE | 0.33 | 2026-12-09 | 43 | standoff E criteria met or Brent front-month >= 120 by Dec 9 | 2026-10-27 |
| F-20261209-REAL3 | 0.09 | 2026-12-09 | 37 | real 10y > 3.0 by Dec 9 | 2026-11-02 |
| S-20261209-BRENT120 | 0.35 | 2026-12-09 | 40 | Brent front-month settles >= 120 on any day by Dec 9 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| S-20261209-BRENT90 | 0.15 | 2026-12-09 | 40 | Brent front-month settles <= 90 on any day by Dec 9 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| S-20261209-E | 0.4 | 2026-12-09 | 40 | E criteria met by Dec 9 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| S-20261209-M3 | 0.15 | 2026-12-09 | 40 | a Hormuz war-risk premium <= 2% of hull reported by Dec 9 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| S-20261209-SIGN | 0.3 | 2026-12-09 | 40 | a written US-Iran agreement announced by both governments by Dec 9 | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| F-20261210-ORCL | 0.09 | after 2026-12-11 (options term structure); Dec 14 cited; unverified | 45 | FQ2 capex cut, deferral or verified restraint language | 2026-10-27 |
| F-202612xx-MU | 0.15 | ~2026-12-16/17 (unverified) | 44 | Micron FQ1 guide below consensus or LTA-renegotiation language | 2026-11-02 |
| S-20261231-FUSE | 0.1 | 2026-12-31 | 62 | any tranche of the SpaceX $40B prices by Dec 31 at an IG spread with no collateral or sweeteners reported | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) |
| F-20261027-B-H3 | 0.5 | 2027-01-20 | 85 | B confirmed by Jan 20, 2027 (10/27 line) | 2026-10-27 |
| F-20270120-B-H3 | 0.31 | 2027-01-20 | 79 | B confirmed by Jan 20, 2027 (cone H3 median; 0.18 before the amendment) | 2026-11-02 |

## Resolved ledger

Brier = (p − outcome)², so a confident right call scores near 0 and a confident wrong one near 1. Both the logged and the recomputed Brier are kept; a mismatch is listed below the table.

| ID | p | Outcome | Brier | Log score | Resolved in |
|---|---|---|---|---|---|
| F-20261020-SPCX | 0.8 | 1 | 0.04 | -0.223144 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261021-META | 0.8 | 1 | 0.04 | -0.223144 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261028-DISSENT | 0.55 | 1 | 0.2025 | -0.597837 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261028-FOMC | 0.7 | 1 | 0.09 | -0.356675 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261028-GEV | 0.75 | 1 | 0.0625 | -0.287682 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261028-GOOGL | 0.85 | 1 | 0.0225 | -0.162519 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261028-MSFT | 0.8 | 0 | 0.64 | -1.609438 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261029-AMZN | 0.85 | 1 | 0.0225 | -0.162519 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261030-ANY-RESTRAINT | 0.4 | 0 | 0.16 | -0.510826 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261030-META-EQ | 0.75 | 1 | 0.0625 | -0.287682 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261102-SLOOS | 0.3 | 0 | 0.09 | -0.356675 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |
| F-20261103-ORCL-BONDS | 0.85 | 1 | 0.0225 | -0.162519 | [2026-11-02T1935-dials-lite](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-11-02T1935-dials-lite) |

Logged and recomputed Brier scores agree on every resolved forecast.

## Scoreboard

| Kind | n | Brier (all) | Brier (last 20) | Mean log score |
|---|---|---|---|---|
| dials | 12 | 0.12125 | 0.12125 | -0.411722 |
| standoff | 0 |  |  |  |

By lead-time bucket (dials and standoff together; lead taken from the forecast's registration date where the run folders carry it, otherwise from the date of the run that registered it; migrated forks without one are *unknown*):

| Lead bucket | n | Mean Brier |
|---|---|---|
| unknown | 12 | 0.121 |

## Standoff branches

The Hormuz standoff is the one variable that decides which branch the macro cone lands in, so it has its own cone: **R+** settlement with a security regime, **R−** thin deal, **F** frozen harassment, **E** escalation.

![Standoff branch weights at H2 by run](images/standoff-light.png#only-light){ .chart }
![Standoff branch weights at H2 by run](images/standoff-dark.png#only-dark){ .chart }
<p class="chart-sub">Weights rounded to 5; the exact odds-form values are in each run's cone.json. Source: dials/state/standoff.csv.</p>

??? note "Text version (selectable)"
    | Run | H2 R+ | H2 R− | H2 F | H2 E | H3 R+ | H3 R− | H3 F | H3 E |
    |---|---|---|---|---|---|---|---|---|
    | [2026-10-20T0620-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-20T0620-standoff) | 10 | 20 | 35 | 35 | 10 | 20 | 30 | 40 |
    | [2026-10-30T1253-standoff](https://github.com/tyrel-beede/fred_data_feed/tree/main/dials/runs/2026-10-30T1253-standoff) | 10 | 20 | 25 | 45 | 10 | 20 | 20 | 50 |

## The Pigs ledger

The column's asymmetries, graded after the fact: **0 paid / 4 cost / 0 void**, 14 open. Hit rate is not the point; the payoff shape is — a 40% hit rate with 3:1 payoffs is a good record and a 70% hit rate with 1:3 payoffs is not.

| ID | Grade | Basis | Graded on |
|---|---|---|---|
| PG-20261018-CONVEX | cost | SPX -1.4% Oct 19-30 (range +1.5/-1.7%), SMH -4.7% vs +/-4% / +/-8% lines | 2026-10-30 |
| PG-20261018-SPCX | cost | SPCX +7.79% on Oct 21 with capex raised vs a +/-8% line | 2026-10-27 |
| PG-20261027-AMZN-TAPE | cost | AMZN -7% premarket, closed -1.4% vs a +/-6% line | 2026-10-30 |
| PG-20261027-DISSENT | cost | two dissents for a hike; 2y 4.67 vs 4.68 prior = 1 bp vs an 8 bp line | 2026-10-30 |

??? note "Open pigs"
    | ID | Resolves | Criterion |
    |---|---|---|
    | PG-20261018-DEC-HIKE | 2026-12-09 | no hike on Dec 9, or Dec-hike odds < 60% at any point before |
    | PG-20261018-PERIPHERY-REBOUND | 2026-11-13 | equal-weight basket (IWM, XHB, E7 neoclouds) outperforms the top-8 equal-weight by > 3 pts from the Oct 16 close to Nov 13 |
    | PG-20261018-TAIL | 2026-11-13 | gold +5% from Oct 16 by Nov 13 together with a 30y tail >= 2 bp or custody down 4 straight weeks |
    | PG-20261018-UNMOVED | 2026-12-09 | IG OAS > 100 or E6 3m < -15 by Dec 9; void if no B element |
    | PG-20261027-AVGO-SPV | 2026-12-01 | AVGO close on Dec 1 >= +/-8% from 329.17 (10/26) |
    | PG-20261027-CRWV-80 | 2026-12-09 | CRWV 5y CDS <= 900 bp on any day by Dec 9 -> paid; else cost |
    | PG-20261027-NVDA-LAST-NODE | 2026-11-19 | NVDA close on Nov 19 >= +/-10% from 216.00 (10/26) |
    | PG-20261027-SINGLE-B | 2026-12-09 | HY OAS >= 400 on any day by Dec 9 -> paid; else cost |
    | PG-20261030-BREADTH-TREND | 2026-11-20 | paid if on Nov 20 >= 63.7% above the 200d AND the A/D line > its Oct 29 level; cost if either fails |
    | PG-20261030-JUNE-TOP | 2026-12-09 | equal-weight (LRCX, AMAT, 000660.KS, 005930.KS) beats top-8 equal-weight by > 5 pts from Oct 30 -> paid; void if a B element fires first |
    | PG-20261030-LAST-SUPPLIER | 2026-12-18 | MU/SMH ratio down > 10% from 1.693 (10/30) -> paid; else cost |
    | PG-20261030-SHELTER | 2026-11-13 | 10y close >= 5.20 on any day by Nov 13, or a 30y tail >= 2 bp on Nov 12 -> paid; else cost |
    | PG-20261030-UNHEDGED-NAMES | 2026-11-20 | top-8 dispersion sigma >= 12 with SPX within 5% of its high -> paid; sigma < 7 or SPX > 5% down -> cost |
    | PG-20261030-UNOWNED-OIL | 2026-12-09 | WTI front-month close outside $90-120 on any day by Dec 9 -> paid; else cost |

*Rebuilt 2026-11-06 from `tyrel-beede/fred_data_feed` commit `dbefb0a`. Analysis, not advice. Probabilities are the dashboard's or the market's, never a conviction.*{ .release-stamp }
