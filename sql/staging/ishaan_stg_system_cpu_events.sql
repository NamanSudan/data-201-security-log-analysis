-- stg_system_cpu_events: Raw 1:1 with Metricbeat system/cpu JSON records
-- Source: 2022-01-21-system_cpu.log (internal_share)
-- Notebook: 08_system_cpu_internal_share.ipynb
-- Candidate key: (source_host, source_log, event_timestamp)

CREATE TABLE stg_system_cpu_events (
    row_id              SERIAL PRIMARY KEY,
    source_host         VARCHAR(30)     NOT NULL,           -- YAML host_key, e.g. "internal-share"
    source_log          VARCHAR(100)    NOT NULL,           -- log filename, e.g. "2022-01-21-system_cpu.log"
    event_timestamp     TIMESTAMPTZ     NOT NULL,           -- Metricbeat @timestamp (UTC)
    hostname            VARCHAR(255),                       -- host.name field from the beat document
    cpu_total_pct       NUMERIC(6, 4),                      -- system.cpu.total.pct  (0.0–1.0)
    cpu_user_pct        NUMERIC(6, 4),                      -- system.cpu.user.pct
    cpu_system_pct      NUMERIC(6, 4),                      -- system.cpu.system.pct
    cpu_idle_pct        NUMERIC(6, 4),                      -- system.cpu.idle.pct
    cpu_iowait_pct      NUMERIC(6, 4),                      -- system.cpu.iowait.pct
    cpu_steal_pct       NUMERIC(6, 4),                      -- system.cpu.steal.pct (hypervisor steal)
    cpu_softirq_pct     NUMERIC(6, 4),                      -- system.cpu.softirq.pct
    cpu_irq_pct         NUMERIC(6, 4),                      -- system.cpu.irq.pct
    cpu_nice_pct        NUMERIC(6, 4),                      -- system.cpu.nice.pct
    cpu_cores           SMALLINT,                           -- system.cpu.cores (logical core count)
    event_duration_ns   BIGINT,                             -- event.duration in nanoseconds
    metricset_period_ms INTEGER                             -- metricset.period in milliseconds (45000)
);
