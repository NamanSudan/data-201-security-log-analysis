-- =============================================================================
-- Raw (Unnormalized) DDL: CPU Metrics Log → system_cpu_events
-- Source : russellmitchell/gather/internal_share/logs/2022-01-21-system_cpu.log
-- Rows   : 1,919  |  Columns: 12
-- =============================================================================

CREATE TABLE system_cpu_events (
    system_cpu_event_id  SERIAL                   PRIMARY KEY,
    event_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL,
    hostname             TEXT,
    cpu_total_pct        NUMERIC(6,4),
    cpu_user_pct         NUMERIC(6,4),
    cpu_system_pct       NUMERIC(6,4),
    cpu_idle_pct         NUMERIC(6,4),
    cpu_iowait_pct       NUMERIC(6,4),
    cpu_steal_pct        NUMERIC(6,4),
    cpu_softirq_pct      NUMERIC(6,4),
    cpu_cores            SMALLINT,
    created_at           TIMESTAMP                DEFAULT CURRENT_TIMESTAMP
);
