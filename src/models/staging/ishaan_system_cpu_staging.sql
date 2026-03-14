CREATE SCHEMA IF NOT EXISTS staging;

-- 1:1 staging table for internal_share/logs/2022-01-21-system_cpu.log
-- Columns map to the tokens present in each raw log line plus line_number.
CREATE TABLE IF NOT EXISTS staging.ishaan_system_cpu_staging (
    line_number     INTEGER                  PRIMARY KEY,
    event_timestamp TIMESTAMP WITH TIME ZONE,
    hostname        TEXT,
    cpu_total_pct   NUMERIC(6,4),
    cpu_user_pct    NUMERIC(6,4),
    cpu_system_pct  NUMERIC(6,4),
    cpu_idle_pct    NUMERIC(6,4),
    cpu_iowait_pct  NUMERIC(6,4),
    cpu_steal_pct   NUMERIC(6,4),
    cpu_softirq_pct NUMERIC(6,4),
    cpu_cores       SMALLINT,
    CONSTRAINT ishaan_system_cpu_staging_line_number_ck CHECK (line_number > 0)
);

CREATE INDEX IF NOT EXISTS ishaan_system_cpu_staging_event_ts_idx
    ON staging.ishaan_system_cpu_staging (event_timestamp);

CREATE INDEX IF NOT EXISTS ishaan_system_cpu_staging_host_ts_idx
    ON staging.ishaan_system_cpu_staging (hostname, event_timestamp);
