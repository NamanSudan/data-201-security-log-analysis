"""Streamlit dashboard for the DATA 201 final project.

Tells the privilege escalation on intranet_server story by stacking
filter-driven KPI cards above seven canonical SQL story panels and a
static index-improvement summary. Single-page layout, top to bottom,
optimised for a 60 second demo.

Run from the repo root:
    venv/bin/streamlit run src/dashboard/app.py

Prerequisites:
    1. PostgreSQL Docker container `security-logs-dev` running on 5432.
    2. Alembic at head (revision 742e860d116f or later).
    3. Repo root .env populated with DB_USER, DB_PASSWORD, DB_HOST,
       DB_PORT and DB_NAME (or a single DATABASE_URL).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from db import get_engine, run_sql, run_sql_file
from sqlalchemy import bindparam, text
from sqlalchemy.exc import OperationalError

SQL_DIR = "sql/queries/advanced"

ATTACK_DAY = "2022-01-24"

# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="DATA 201 - Privilege Escalation Dashboard",
    layout="wide",
)


def _connect():
    """Return a live SQLAlchemy engine or stop the app with a friendly error."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except OperationalError as exc:
        st.error(
            "Could not connect to PostgreSQL. Verify the Docker container "
            "`security-logs-dev` is running on localhost:5432 and that the "
            "repo root .env holds DB_USER, DB_PASSWORD and DB_NAME. "
            f"Underlying error: {exc.orig}"
        )
        st.stop()
        return None


engine = _connect()


# ---------------------------------------------------------------------
# Filter options (cached)
# ---------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def filter_options() -> dict[str, list[str]]:
    eng = get_engine()
    hosts = run_sql(eng, "SELECT host_key FROM host ORDER BY host_key")["host_key"].tolist()
    phases = run_sql(eng, "SELECT phase_name FROM attack_phase ORDER BY phase_name")[
        "phase_name"
    ].tolist()
    logs = run_sql(
        eng,
        "SELECT DISTINCT source_log FROM labeled_line ORDER BY source_log",
    )["source_log"].tolist()
    return {"hosts": hosts, "phases": phases, "logs": logs}


options = filter_options()

# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
st.sidebar.header("Filters")
st.sidebar.caption(
    "These controls drive the KPI cards at the top of the page. The "
    "seven story panels and the performance summary below the cards "
    "show the canonical narrative and stay fixed."
)

default_host = (
    ["intranet_server"] if "intranet_server" in options["hosts"] else options["hosts"][:1]
)
default_phases = [p for p in ("initial_access", "privilege_escalation") if p in options["phases"]]

selected_hosts = st.sidebar.multiselect("Host", options["hosts"], default=default_host)
selected_phases = st.sidebar.multiselect("Attack phase", options["phases"], default=default_phases)
selected_logs = st.sidebar.multiselect(
    "Source log (optional)",
    options["logs"],
    default=[],
    help="Leave empty to include every source log.",
)

# Empty selection means no constraint; fall back to the full list.
eff_hosts = selected_hosts or options["hosts"]
eff_phases = selected_phases or options["phases"]
eff_logs = selected_logs or options["logs"]

st.sidebar.divider()
st.sidebar.markdown(
    "**Story canon defaults:**\n\n"
    "- Host = `intranet_server`\n"
    "- Phases = `initial_access`, `privilege_escalation`\n"
    "- Source logs = (all)"
)


# ---------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------
st.title("Privilege Escalation on intranet_server")
st.caption(
    "DATA 201 final project, Group 5. Source dataset: AIT-LDSv2.0 / "
    "russellmitchell. Database: PostgreSQL 16, Alembic head "
    "`742e860d116f`. Story: an `initial_access` foothold on "
    "`access.log.2` leads into a `su` then `sudo` chain captured by "
    "the saved view `v_privilege_escalation_timeline`."
)


# ---------------------------------------------------------------------
# Section 1: KPI cards (filter driven)
# ---------------------------------------------------------------------
@st.cache_data(ttl=120, show_spinner=False)
def kpi_counts(
    hosts: tuple[str, ...],
    phases: tuple[str, ...],
    logs: tuple[str, ...],
) -> dict[str, int]:
    eng = get_engine()
    label_stmt = text(
        """
        SELECT
          COUNT(DISTINCT ll.labeled_line_id) AS labeled_lines,
          COUNT(DISTINCT al.label_id)        AS distinct_labels,
          COUNT(DISTINCT ll.source_log)      AS distinct_logs
        FROM labeled_line ll
        JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
        JOIN attack_label al        ON al.label_id = lll.label_id
        JOIN attack_phase ap        ON ap.phase_id = al.phase_id
        WHERE ll.source_host IN :hosts
          AND ap.phase_name IN :phases
          AND ll.source_log IN :logs
        """
    ).bindparams(
        bindparam("hosts", expanding=True),
        bindparam("phases", expanding=True),
        bindparam("logs", expanding=True),
    )
    audit_stmt = text(
        """
        SELECT COUNT(DISTINCT ae.event_id) AS audit_events
        FROM audit_event ae
        JOIN host h ON h.host_id = ae.host_id
        JOIN labeled_line ll
          ON ll.source_host = h.host_key
         AND ll.source_log  = 'audit.log'
         AND ll.line_number = ae.line_number
        JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
        JOIN attack_label al        ON al.label_id = lll.label_id
        JOIN attack_phase ap        ON ap.phase_id = al.phase_id
        WHERE h.host_key IN :hosts
          AND ap.phase_name IN :phases
        """
    ).bindparams(
        bindparam("hosts", expanding=True),
        bindparam("phases", expanding=True),
    )
    with eng.connect() as conn:
        label_row = pd.read_sql(
            label_stmt,
            conn,
            params={"hosts": list(hosts), "phases": list(phases), "logs": list(logs)},
        ).iloc[0]
        audit_row = pd.read_sql(
            audit_stmt,
            conn,
            params={"hosts": list(hosts), "phases": list(phases)},
        ).iloc[0]
    return {
        "labeled_lines": int(label_row["labeled_lines"]),
        "distinct_labels": int(label_row["distinct_labels"]),
        "distinct_logs": int(label_row["distinct_logs"]),
        "audit_events": int(audit_row["audit_events"]),
    }


counts = kpi_counts(tuple(eff_hosts), tuple(eff_phases), tuple(eff_logs))

st.subheader("Filtered key counts")
st.caption(
    "All four metrics respond to the sidebar filters. SQL: inline "
    "queries against `labeled_line`, `labeled_line_label`, "
    "`attack_label`, `attack_phase`, `audit_event` and `host`."
)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Labeled lines", f"{counts['labeled_lines']:,}")
m2.metric("Distinct attack labels", counts["distinct_labels"])
m3.metric("Source logs touched", counts["distinct_logs"])
m4.metric("Audit events on host", counts["audit_events"])

st.divider()


# ---------------------------------------------------------------------
# Section 2: Foothold-to-escalate journey (river_foothold_to_escalate_journey.sql)
# ---------------------------------------------------------------------
st.subheader("1. Foothold-to-escalate journey on access.log.2")
st.caption(
    "NTILE(3) buckets every labeled line on `intranet_server/"
    "access.log.2` into early, middle and late thirds, then counts "
    "labels per phase per third. SQL: "
    "`sql/queries/advanced/river_foothold_to_escalate_journey.sql`."
)
journey_df = run_sql_file(engine, f"{SQL_DIR}/river_foothold_to_escalate_journey.sql")
journey_df["journey_label"] = journey_df["journey_third"].map(
    {1: "1. Early third", 2: "2. Middle third", 3: "3. Late third"}
)
fig_journey = px.bar(
    journey_df,
    x="journey_label",
    y="labeled_lines",
    color="phase_name",
    barmode="stack",
    text="labeled_lines",
    labels={
        "journey_label": "Journey position (NTILE third)",
        "labeled_lines": "Labeled lines",
        "phase_name": "Attack phase",
    },
    category_orders={"phase_name": ["initial_access", "privilege_escalation"]},
)
fig_journey.update_traces(textposition="inside")
fig_journey.update_layout(
    yaxis_title="Labeled lines on access.log.2",
    legend_title_text="Phase",
    height=380,
)
st.plotly_chart(fig_journey, width="stretch")
with st.expander("Show data table"):
    st.dataframe(
        journey_df.drop(columns=["journey_label"]),
        width="stretch",
        hide_index=True,
    )

st.divider()


# ---------------------------------------------------------------------
# Section 3: Foothold cumulative (river_foothold_cumulative.sql)
# ---------------------------------------------------------------------
st.subheader("2. Foothold accumulation across access.log.2")
st.caption(
    "Cumulative count of `foothold` labels in 1,000-line buckets of "
    "`intranet_server/access.log.2`, climbing to ~7,691 by the final "
    "bucket. SQL: "
    "`sql/queries/advanced/river_foothold_cumulative.sql`."
)
cumulative_df = run_sql_file(engine, f"{SQL_DIR}/river_foothold_cumulative.sql")
fig_cumulative = px.line(
    cumulative_df,
    x="line_bucket",
    y="foothold_cumulative",
    markers=True,
    labels={
        "line_bucket": "Line number bucket (start of 1,000-line window)",
        "foothold_cumulative": "Cumulative foothold lines",
    },
)
fig_cumulative.update_traces(line_shape="hv")
fig_cumulative.add_bar(
    x=cumulative_df["line_bucket"],
    y=cumulative_df["foothold_in_bucket"],
    name="Foothold in bucket",
    opacity=0.35,
    yaxis="y2",
)
fig_cumulative.update_layout(
    yaxis2={
        "overlaying": "y",
        "side": "right",
        "title": "Foothold lines per bucket",
        "showgrid": False,
    },
    legend={"orientation": "h", "y": 1.1, "x": 0},
    height=380,
)
st.plotly_chart(fig_cumulative, width="stretch")

st.divider()


# ---------------------------------------------------------------------
# Section 4: Privilege escalation timeline (v_privilege_escalation_timeline)
# ---------------------------------------------------------------------
st.subheader("3. Privilege escalation timeline (su then sudo)")
st.caption(
    "Nine-event chain on `intranet_server` between 2022-01-24 04:37:40 "
    "and 04:38:06 UTC. Source: Alembic-managed view "
    "`v_privilege_escalation_timeline`, exposed by "
    "`sql/queries/advanced/naman_view_privilege_escalation_timeline.sql`."
)
timeline_df = run_sql_file(engine, f"{SQL_DIR}/naman_view_privilege_escalation_timeline.sql")
timeline_display = timeline_df.copy()
timeline_display["timestamp"] = pd.to_datetime(timeline_display["timestamp"]).dt.strftime(
    "%Y-%m-%d %H:%M:%S UTC"
)
st.dataframe(
    timeline_display,
    width="stretch",
    hide_index=True,
    column_config={
        "host_key": st.column_config.TextColumn("Host"),
        "timestamp": st.column_config.TextColumn("Event timestamp"),
        "audit_type": st.column_config.TextColumn("Audit type"),
        "pam_operation": st.column_config.TextColumn("PAM op"),
        "target_account": st.column_config.TextColumn("Target account"),
        "executable": st.column_config.TextColumn("Executable"),
        "terminal": st.column_config.TextColumn("Terminal"),
        "labels": st.column_config.TextColumn("Labels"),
        "rules": st.column_config.TextColumn("Rules"),
    },
)
st.caption(
    f"View returned {len(timeline_df)} rows: burst 1 = `su` from "
    "www-data to jhall, burst 2 = `sudo cat /etc/shadow` as jhall."
)

st.divider()


# ---------------------------------------------------------------------
# Section 5: Source spread (river_priv_esc_source_spread.sql)
# ---------------------------------------------------------------------
st.subheader("4. Where else does the attack leave traces")
st.caption(
    "Five `(source_host, source_log)` vantage points carry "
    "`privilege_escalation` labels: the audit chain on the host plus "
    "auth/access/cpu/dnsmasq side-channels. SQL: "
    "`sql/queries/advanced/river_priv_esc_source_spread.sql`."
)
source_df = run_sql_file(engine, f"{SQL_DIR}/river_priv_esc_source_spread.sql")
source_df["source_pair"] = source_df["source_host"] + " / " + source_df["source_log"]
fig_source = px.bar(
    source_df.sort_values("labeled_lines"),
    x="labeled_lines",
    y="source_pair",
    orientation="h",
    text="labeled_lines",
    color="source_host",
    labels={
        "source_pair": "Source host / source log",
        "labeled_lines": "Labeled lines (privilege_escalation)",
        "source_host": "Host",
    },
)
fig_source.update_traces(textposition="outside")
fig_source.update_layout(height=320, legend_title_text="Host")
st.plotly_chart(fig_source, width="stretch")

st.divider()


# ---------------------------------------------------------------------
# Section 6: Rule effectiveness (naman_rule_effectiveness_priv_esc.sql)
# ---------------------------------------------------------------------
st.subheader("5. Detection rules ranked by lines triggered")
st.caption(
    "DENSE_RANK over `lines_triggered` per detection rule inside the "
    "privilege_escalation phase. SQL: "
    "`sql/queries/advanced/naman_rule_effectiveness_priv_esc.sql`."
)
rule_df = run_sql_file(engine, f"{SQL_DIR}/naman_rule_effectiveness_priv_esc.sql")
fig_rule = px.bar(
    rule_df.sort_values("lines_triggered"),
    x="lines_triggered",
    y="rule_name",
    orientation="h",
    text="lines_triggered",
    labels={
        "rule_name": "Detection rule",
        "lines_triggered": "Distinct labeled lines triggered",
    },
    color="lines_triggered",
    color_continuous_scale="Blues",
)
fig_rule.update_traces(textposition="outside")
fig_rule.update_layout(
    height=420,
    coloraxis_showscale=False,
)
st.plotly_chart(fig_rule, width="stretch")

st.divider()


# ---------------------------------------------------------------------
# Section 7: Audit types (ishaan_audit_types_in_privilege_escalation.sql)
# ---------------------------------------------------------------------
st.subheader("6. Audit event types touched by the chain")
st.caption(
    "Distinct `audit_event.type` values that fire on the same lines "
    "carrying a `privilege_escalation` label. SQL: "
    "`sql/queries/advanced/ishaan_audit_types_in_privilege_escalation.sql`."
)
audit_types_df = run_sql_file(engine, f"{SQL_DIR}/ishaan_audit_types_in_privilege_escalation.sql")
type_cols = st.columns(max(len(audit_types_df), 1))
for col, audit_type in zip(type_cols, audit_types_df["audit_type"], strict=False):
    col.metric("Audit type", audit_type)
st.caption(
    f"{len(audit_types_df)} distinct audit types fire on the "
    "privilege_escalation chain (out of all audit_event types defined "
    "in the kernel taxonomy)."
)

st.divider()


# ---------------------------------------------------------------------
# Section 8: Busiest day (ishaan_intranet_server_busiest_day.sql)
# ---------------------------------------------------------------------
st.subheader("7. Busiest audit day on intranet_server")
st.caption(
    "RANK() over per-day `audit_event` counts on `intranet_server`. "
    f"The attack day ({ATTACK_DAY}) is highlighted. SQL: "
    "`sql/queries/advanced/ishaan_intranet_server_busiest_day.sql`."
)
busiest_df = run_sql_file(engine, f"{SQL_DIR}/ishaan_intranet_server_busiest_day.sql")
busiest_df["event_date"] = pd.to_datetime(busiest_df["event_date"]).dt.strftime("%Y-%m-%d")
busiest_df["is_attack_day"] = (
    busiest_df["event_date"].eq(ATTACK_DAY).map({True: "Attack day", False: "Other"})
)
fig_busy = px.bar(
    busiest_df,
    x="event_date",
    y="events_that_day",
    color="is_attack_day",
    text="events_that_day",
    labels={
        "event_date": "Event date",
        "events_that_day": "Audit events that day",
        "is_attack_day": "",
    },
    category_orders={"event_date": busiest_df["event_date"].tolist()},
    color_discrete_map={"Attack day": "#d62728", "Other": "#1f77b4"},
)
fig_busy.update_traces(textposition="outside", cliponaxis=False)
fig_busy.update_xaxes(type="category")
fig_busy.update_yaxes(
    range=[0, busiest_df["events_that_day"].max() * 1.18],
)
fig_busy.update_layout(height=420, legend_title_text="", margin={"t": 40})
st.plotly_chart(fig_busy, width="stretch")
st.caption(
    "The attack day (2022-01-24, red) carries 565 audit events on "
    "intranet_server and ranks 3 of 4 days by raw volume, blending "
    "into the host's baseline activity. The 9-event "
    "privilege_escalation chain in Section 3 still fires on this day."
)

st.divider()


# ---------------------------------------------------------------------
# Section 9: Performance panel (static, naman_explain_index_improvement.sql)
# ---------------------------------------------------------------------
st.subheader("8. Index improvement on the incident-response query")
st.caption(
    "Static EXPLAIN ANALYZE evidence captured 2026-05-01 on the "
    "russellmitchell slice (3,048 audit_event rows). SQL: "
    "`sql/queries/advanced/naman_explain_index_improvement.sql`. "
    "Index is Alembic managed (revision 742e860d116f, see "
    "`sql/3nf/_indexes.sql`)."
)
perf_df = pd.DataFrame(
    {
        "Plan": ["Before (no index)", "After (idx_audit_event_host_timestamp)"],
        "Execution time (ms)": [1.462, 0.640],
        "Plan node": ["Seq Scan on audit_event", "Index Scan using composite index"],
        "Buffers shared hit": [141, 33],
    }
)
perf_left, perf_right = st.columns([2, 3])
with perf_left:
    fig_perf = px.bar(
        perf_df,
        x="Plan",
        y="Execution time (ms)",
        text="Execution time (ms)",
        color="Plan",
        color_discrete_sequence=["#7f7f7f", "#2ca02c"],
    )
    fig_perf.update_traces(texttemplate="%{text:.3f} ms", textposition="outside", cliponaxis=False)
    fig_perf.update_yaxes(
        range=[0, perf_df["Execution time (ms)"].max() * 1.25],
    )
    fig_perf.update_layout(showlegend=False, height=380, yaxis_title="ms", margin={"t": 40})
    st.plotly_chart(fig_perf, width="stretch")
with perf_right:
    st.markdown(
        """
- **Query**: incident-response zoom on `intranet_server` for the
  04:37:30 to 04:38:15 UTC window on 2022-01-24.
- **Index added**: `idx_audit_event_host_timestamp ON audit_event
  (host_id, timestamp)`.
- **Speedup**: 1.462 ms to 0.640 ms (about 2.3 times faster).
- **Plan node**: Seq Scan (3,039 rows discarded) becomes Index Scan
  (Index Cond covers both equality on host_id and BETWEEN on
  timestamp).
- **Buffers**: shared hit drops from 141 to 33 (about 4 times less).
"""
    )
st.dataframe(perf_df, width="stretch", hide_index=True)


st.divider()
st.caption(
    "Demo flow: filter to `intranet_server` and the two phases, scan "
    "KPI cards, scroll through the seven story panels, close on the "
    "index improvement summary. Repo: `data-201-security-log-analysis`."
)
