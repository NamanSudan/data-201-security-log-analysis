# DATA 201 Final Report

LaTeX sources for the Group 5 final technical report. Submission deadline 05/07/2026 11:59 PM PT.

## Layout

```
report/
├── main.tex              # compile entry point (IEEEtran conference)
├── listings_sql_setup.tex
├── references.bib        # BibTeX entries (IEEE style)
├── README.md             # this file
├── sections/
│   ├── 01_abstract.tex
│   ├── 02_introduction.tex
│   ├── 03_dataset.tex
│   ├── 04_schema_normalization.tex
│   ├── 05_database_setup.tex
│   ├── 06_sql_analysis.tex   <- heaviest section, 20 pts
│   ├── 07_dashboard.tex
│   ├── 08_conclusion.tex
│   ├── 09_references_ai.tex
│   └── 10_appendix.tex
└── figures/
    └── (drop figures here as PDF/PNG; placeholders referenced in .tex)
```

## How to compile

### Option A: Overleaf (recommended for the team)

1. Create a new project at https://www.overleaf.com (free tier).
2. Click **New Project -> Upload Project**, then ZIP the `report/` directory and upload it.
3. In Overleaf project settings, set **Main document** to `main.tex` and **Compiler** to `pdfLaTeX`.
4. Click **Recompile** twice (the bibliography needs the second pass to resolve citations).
5. Invite River and Ishaan as collaborators (Share button, top right). Their edits will show up in the History panel with distinct colors. Screenshot that panel for the appendix.

### Option B: Local pdflatex (Naman, smoke test)

```bash
cd report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `report/main.pdf`. Requires a TeX distribution with `IEEEtran.cls` available (TeX Live, MacTeX, MikTeX all ship it).

## Owner map (per RUBRIC_TRACKER.md)

| Section file | Owner | Status today |
|---|---|---|
| 01_abstract.tex | River | Skeleton drafted (250-word target) |
| 02_introduction.tex | River | Skeleton drafted, refine prose + cite |
| 03_dataset.tex | River | Skeleton drafted |
| 04_schema_normalization.tex | Naman | Skeleton lifted from data_model_3nf.md |
| 05_database_setup.tex | Naman | Skeleton drafted, fill in row counts |
| 06_sql_analysis.tex | All three | All 13 queries embedded; result figures + insight prose TBD |
| 07_dashboard.tex | Naman | Skeleton; finalize after dashboard built |
| 08_conclusion.tex | River | Skeleton drafted |
| 09_references_ai.tex | Ishaan | AI ack drafted; verify wording before submit |
| 10_appendix.tex | Ishaan | Placeholders for Overleaf history + git log screenshots |

`% TBD` and `% TODO` markers in each `.tex` file indicate where prose or figures still need to be filled in. Search the directory with `grep -n "TBD\|TODO" sections/*.tex`.

## Figure pipeline

Figures live in `report/figures/`. Inputs to add before submission:

| File | Source | How to produce |
|---|---|---|
| `eer_3nf_combined.pdf` | `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml` | Open in drawio.com, File -> Export As -> PDF, crop to drawing |
| `dashboard_overview.png` | running Streamlit app | Cmd+Shift+4 a window-bound screenshot |
| `dashboard_filter_demo.png` | running Streamlit app | Same, after applying the host filter |
| `explain_before.png` | psql `EXPLAIN ANALYZE` before index | Copy plan text, paste in a text editor, screenshot |
| `explain_after.png` | psql `EXPLAIN ANALYZE` after index | Same |
| `q_b1_result.png` ... `q_a7_result.png` | psql `SELECT` outputs | Same; or use the dashboard chart for the ones already plotted |
| `overleaf_history.png` | Overleaf -> History panel | Cmd+Shift+4, full panel |
| `git_log_report.png` | `git log --pretty=format:'%h %an %ad %s' -- report/` | Terminal screenshot |

## Workflow until 05/07

1. **05/01:** Skeleton built. Each owner reads their section, replaces `TBD` markers with prose. Naman exports the EER diagram and commits the PDF to `figures/`.
2. **05/02-05/03:** Streamlit dashboard built. Section 7 finalized after the app is running. Result snapshots taken from the dashboard for the queries it exposes.
3. **05/04:** Section 6 result snapshots filled in. Section 5 row counts filled in. EXPLAIN before/after captured.
4. **05/05:** Compile + style pass (River). Verify abstract is exactly 250 words. Verify no `TBD`/`TODO` markers remain.
5. **05/06:** Final read-through. Compile to PDF. Get Overleaf history screenshot for the appendix.
6. **05/07:** Submit on Canvas (PDF + repo zip / link).

## Style rules

- **No em dashes or `--` in prose.** Use a single hyphen.
- **No emojis.**
- **Use the IEEEtran `\cite{...}`** for every external claim. Add new BibTeX entries to `references.bib` with the lastname-year-shortword cite-key convention.
- **All SQL goes in `lstlisting` blocks** (already configured in `listings_sql_setup.tex`).
- **Figures are referenced by `\ref{fig:...}` and `\label{...}` in their `\begin{figure}` block.**
- **Section labels are `\label{sec:...}`.**

## Referenced docs in the project repo

- `docs/schema/data_model_3nf.md` - source of section 4 prose
- `docs/schema/normalization_raw_to_3nf.md` - source of normalization narrative
- `docs/data_exploration/notebook_findings/*.md` - per-source findings, useful for sections 3 and 8
- `sql/queries/basic/*.sql` and `sql/queries/advanced/*.sql` - SQL embedded in section 6
- `presentation/DATA 201_ Group Project Mid-presentation - Submission Version.pptx` - mid-pres deck for context

## Troubleshooting

- **`! LaTeX Error: File 'IEEEtran.cls' not found.`** Update your TeX Live distribution; on Overleaf this is shipped by default.
- **Bibliography is empty.** You need three compile passes when bibliography changes. Hit Recompile twice on Overleaf, or run `pdflatex; bibtex; pdflatex; pdflatex` locally.
- **A figure is missing.** That figure file has not been added to `figures/` yet. The `.tex` file references it by name; check the relevant `% TODO` comment in the section.
