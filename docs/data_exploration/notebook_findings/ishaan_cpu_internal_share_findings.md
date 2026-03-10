# CPU Metrics Log Findings - internal_share

Source: `russellmitchell/gather/internal_share/logs/2022-01-21-system_cpu.log` (1,919 records, JSON Lines / metricbeat format).
Analysis notebook: `notebooks/04_explore_system_cpu_internal_share.ipynb`.
Target table: `system_cpu_events` (12 columns, 1,919 rows).

---

## 1. Normalization Analysis

### 1NF Check

**Atomic fields:** All columns produced by `json_normalize` are scalar values (timestamps, floats, integers, a single string). The raw metricbeat record is a deeply nested JSON object, but after flattening all values are atomic. No arrays or nested structures remain in the working DataFrame.

**Repeating groups:** None. The CPU percentage fields (`cpu_total_pct`, `cpu_user_pct`, `cpu_system_pct`, etc.) are separate named columns measuring distinct CPU states - they are not a repeating group.

**1NF status: satisfied.** All fields are atomic after flattening. Unlike the companion `audit_events_intranet_raw` table, there is no `msg` blob to unpack and no 1NF violation.

### 2NF Check

The table uses a single-column surrogate primary key (`system_cpu_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

Two transitive dependencies are present:

- `hostname → cpu_cores`: If cores are fixed per server, the hostname determines `cpu_cores`. Only one host (`internal-share`) appears in this dataset, so the dependency cannot be fully verified. It becomes significant if multiple hosts are added.
- `cpu_total_pct` is derivable: `cpu_total_pct ≈ cpu_user_pct + cpu_system_pct + cpu_iowait_pct + cpu_steal_pct + cpu_softirq_pct`. It is a computed aggregate stored for query convenience, not independently measured.

**3NF status: acceptable.** `cpu_total_pct` is stored denormalized for convenience. The `hostname → cpu_cores` dependency is deferred - if multiple hosts are added, `cpu_cores` should move to a hosts dimension table.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `system_cpu_event_id` | all attributes | Surrogate PK. |
| FD2 | `event_timestamp` | all metrics | Timestamps are unique per 45s collection interval. Candidate natural key. |
| FD3 | `hostname` | `cpu_cores` | If cores are fixed per host, hostname functionally determines cpu_cores. Relevant when multiple hosts are added. |
| FD4 | `cpu_user_pct, cpu_system_pct, cpu_iowait_pct, cpu_steal_pct, cpu_softirq_pct` | `cpu_total_pct` | Total is the sum of components. Stored denormalized for query convenience. |

---

## 2. Field-by-Field Summary

### Core fields (present in all records)

| Field | Present | Unique | Notes |
|---|---|---|---|
| `timestamp` | 1919/1919 | 1919 | UTC datetime, parsed to `datetime64[ns, UTC]`. Candidate natural key. |
| `host` | 1919/1919 | 1 | Always `internal-share`. |
| `cpu_total_pct` | 1919/1919 | varies | Range 0.0000–1.0000. Derived from component pct fields. |
| `cpu_user_pct` | 1919/1919 | varies | Range 0.0000–0.7300. User-space processes. |
| `cpu_system_pct` | 1919/1919 | varies | Range 0.0000–0.9600. Kernel/system calls. |
| `cpu_idle_pct` | 1919/1919 | varies | Range 0.0000–0.9893. Drops to 0 during attack windows. |
| `cpu_iowait_pct` | 1919/1919 | varies | Range 0.0000–0.9440. Peaks during exfiltration window. |
| `cpu_steal_pct` | 1919/1919 | varies | Range 0.0000–0.0116. Very low throughout. |
| `cpu_softirq_pct` | 1919/1919 | varies | Near-zero throughout. |
| `cores` | 1919/1919 | 1 | Always 2. Constant - no analytical value in this table. |
| `event_duration_ns` | 1919/1919 | varies | Time metricbeat took to collect each record, in nanoseconds. |
| `metricset_period_ms` | 1919/1919 | 1 | Always 45000 ms. Constant - could be dropped or moved to metadata table. |

No null values appear in any column after flattening.

---

## 3. Summary Statistics

Descriptive stats across the full day. The mean and median (`p50`) for `cpu_total_pct` are very close (~6.9–7.7%), indicating a stable baseline for most of the day. The max of 100% and the high `cpu_iowait_pct` max of 94.4% reveal two distinct attack windows where the server was saturated.

| Percentile | cpu_total_pct | cpu_user_pct | cpu_system_pct | cpu_iowait_pct |
|---|---|---|---|---|
| p50 | 0.0613 | 0.0237 | 0.0362 | 0.0007 |
| p75 | 0.0723 | 0.0281 | 0.0419 | 0.0011 |
| p90 | 0.0779 | 0.0316 | 0.0446 | 0.0018 |
| p95 | 0.0793 | 0.0326 | 0.0455 | 0.0023 |
| p99 | 0.3830 | 0.0878 | 0.2862 | 0.0087 |
| max | 1.0000 | 0.7300 | 0.9600 | 0.9440 |

The p99 jumps dramatically to 38.3%, far above the p95 of 7.9%, confirming that spike records are extreme outliers. 99% of the day sits below 8% total CPU - the remaining 1% (~19 records) accounts for the two attack windows.

---

## 4. Attack / Spike Windows (Ground Truth Proxies)

19 records where `cpu_total_pct > 0.50` across two distinct time windows. No direct annotation labels exist for CPU records; attack detection relies on threshold comparison cross-referenced with access log and audit log timestamps.

- **Window 1 - 00:15–00:18 UTC** (5 records, ~3 minutes): `cpu_total_pct` pegged at 100% with very low `cpu_user_pct` (~2–5%), meaning the saturation is kernel-driven - consistent with a process monopolising the scheduler or triggering a tight kernel loop. `cpu_idle_pct` drops to exactly 0.000. Server returns to baseline by 00:19 UTC.

- **Window 2 - 06:13–06:22 UTC** (14 records, ~10 minutes): A longer, sustained burst. The first samples show the same 100% kernel-saturation pattern as Window 1, then transition into high `cpu_user_pct` (up to 73%) and very high `cpu_iowait_pct` (up to 94.4%) - the CPU is simultaneously doing heavy user-space computation and waiting on disk I/O. This is consistent with file compression, encryption, or bulk data transfer. This window has the highest `cpu_iowait_pct` values seen across all logs in the dataset.

Spike record count by window:

| Window | Time range (UTC) | Records | Max cpu_total_pct | Max cpu_iowait_pct | Dominant pattern |
|---|---|---|---|---|---|
| Window 1 | 00:15–00:18 | 5 | 1.0000 | ~0.0100 | kernel saturation (cpu_system_pct dominant) |
| Window 2 | 06:13–06:22 | 14 | 1.0000 | 0.9440 | user-space + I/O (exfiltration signature) |

---

## 5. DDL for Raw Loading

12 columns. All pct values stored as `NUMERIC(6,4)` - source data has 4 decimal places of precision and values range 0.0–1.0. Note: `cpu_total_pct` reaches exactly 1.0000 during the attack, so the type must accommodate values up to 1.

```sql
-- PostgreSQL
CREATE TABLE system_cpu_events (
    system_cpu_event_id  SERIAL PRIMARY KEY,
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
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
-- MySQL
CREATE TABLE system_cpu_events (
    system_cpu_event_id  INT AUTO_INCREMENT PRIMARY KEY,
    event_timestamp      DATETIME NOT NULL,
    hostname             VARCHAR(255),
    cpu_total_pct        DECIMAL(6,4),
    cpu_user_pct         DECIMAL(6,4),
    cpu_system_pct       DECIMAL(6,4),
    cpu_idle_pct         DECIMAL(6,4),
    cpu_iowait_pct       DECIMAL(6,4),
    cpu_steal_pct        DECIMAL(6,4),
    cpu_softirq_pct      DECIMAL(6,4),
    cpu_cores            SMALLINT,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Notes for Normalization Phase

1. **No 1NF violations:** After `json_normalize`, all fields are scalar. No `msg` blob to unpack, no subtype tables required. The schema is identical in shape to the intranet-server audit log explored in `05_explore_audit_intranet.ipynb`.

2. **`cpu_total_pct` is a derived column:** It is approximately the sum of the other pct fields. Stored for query convenience but could be dropped in a strict normalized schema and computed as a view or generated column.

3. **Two distinct attack windows:** Unlike a single spike in some companion logs, this file contains two bursts - one at **00:15 UTC** (kernel-saturated, `cpu_system_pct` dominant) and one at **06:13 UTC** (user+I/O heavy). The 06:13 window is the primary exfiltration window; the 00:15 window likely corresponds to initial tool execution or privilege escalation activity recorded in the intranet audit log.

4. **Same host as the 2022-01-22 log:** Both `2022-01-21` and `2022-01-22` originate from `internal-share`. The 2022-01-22 log shows no equivalent spike, confirming attack activity was confined to 2022-01-21.

5. **Constant metadata columns:** `metricset_period_ms` is always 45,000 ms and `cpu_cores` is always 2. These add no analytical value in a single-source table and could be dropped or moved to a hosts dimension table. If multiple hosts or collection periods are added, `cpu_cores` should move to a hosts table with `hostname` as FK.

6. **No label integration:** CPU records have no direct annotation labels. Attack detection relies on threshold comparison (`cpu_total_pct > 0.5`) cross-referenced with timestamps from the access log and audit log.

7. **NUMERIC(6,4) is appropriate:** All pct values range 0.0–1.0 with 4 decimal places of precision in the source data. `NUMERIC(6,4)` covers the full range without floating-point rounding errors. `cpu_total_pct` reaches exactly 1.0000 during attacks, so the type must accommodate values up to 1.

8. **Merge with 2022-01-22 log:** Both daily CPU files use the same metricbeat schema and target the same `system_cpu_events` table. The final table should combine both dates with `event_timestamp` as the natural key discriminator. No additional `host_id` FK is needed since `hostname` is already a column.
