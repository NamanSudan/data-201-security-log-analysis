# DATA-201 Security Log Analysis

Relational database analysis of the AIT-LDSv2.0 cybersecurity dataset for DATA-201 (Database Systems) at San Jose State University.

## Project Overview

Analysis of a simulated enterprise network under attack using the Austrian Institute of Technology Log Data Set V2.0. The dataset includes:

- **22 networked hosts** (firewalls, servers, workstations)
- **~1.8M log events** across multiple log types
- **~62K labeled attack events** with ground truth
- **Multi-stage attack chain**: Reconnaissance → Exploitation → Privilege Escalation → Data Exfiltration

## Team

| Name | GitHub |
|------|--------|
| Naman Sudan | [@NamanSudan](https://github.com/NamanSudan) |
| River Roseveare-Hunt | [@DogmaHG](https://github.com/DogmaHG) |
| Ishaan Shetty | [@Ishaanshetty](https://github.com/Ishaanshetty) |

## Tech Stack

- **Database**: PostgreSQL 16
- **Migrations**: Alembic
- **Language**: Python 3.12
- **CI/CD**: GitHub Actions
- **Project Management**: Linear
- **Communication**: Slack

## Quick Start

### Prerequisites

- Docker Desktop
- Python 3.12+
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/namansudan/data-201-security-log-analysis.git
   cd data-201-security-log-analysis
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Start PostgreSQL**
   ```bash
   docker-compose up -d
   ```

4. **Install Python dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   alembic -c alembic/alembic.ini upgrade head
   ```

6. **Verify setup**
   ```bash
   python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://security_logs_user:password@localhost:5432/security_logs'); print('Connected!' if engine.connect() else 'Failed')"
   ```

## Streamlit Dashboard

Single-page dashboard that tells the privilege-escalation-on-`intranet_server` story across nine panels (KPI cards, seven story panels, one static EXPLAIN/index summary). Panels 3, 6, and 8 each combine multiple views (chart plus table, chart plus chips, and chart plus workload-query reference). Reads directly from PostgreSQL using the same connection settings the loaders use.

### Prerequisites
- Steps 1 to 5 of Quick Start completed (Docker container `security-logs-dev` healthy on port 5432, Alembic at head, Python deps installed).
- Repo-root `.env` populated with `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.

### Run on macOS / Linux
```bash
# From repo root
source venv/bin/activate
venv/bin/streamlit run src/dashboard/app.py
```
Open the URL Streamlit prints (default `http://localhost:8501`). Sidebar filters drive the four KPI cards; the seven story panels and the index-improvement summary are canonical and stay fixed.

### Run on Windows (PowerShell)
```powershell
# From repo root
.\venv\Scripts\Activate.ps1
.\venv\Scripts\streamlit.exe run src\dashboard\app.py
```
If `streamlit.exe` is not on `PATH` after activation, fall back to `python -m streamlit run src\dashboard\app.py`.

### What you should see
- **Filtered key counts**: `Labeled lines = 7,748`, `Distinct attack labels = 6`, `Source logs touched = 4`, `Audit events on host = 9` (with default filters).
- **1. Foothold-to-escalate journey on access.log.2** (NTILE bar)
- **2. Foothold accumulation across access.log.2** (cumulative line + per-bucket bars)
- **3. Privilege escalation timeline (su then sudo)** (time scatter of the 9 events plus the underlying 9-row table from `v_privilege_escalation_timeline`)
- **4. Where else does the attack leave traces** (5-row source spread bar)
- **5. Detection rules ranked by lines triggered** (10-row horizontal bar)
- **6. Audit event types touched by the chain** (per-type event-count bar plus 8 metric chips)
- **7. Busiest audit day on intranet_server** (4-day categorical bar, attack day highlighted)
- **8. Index improvement on the incident-response query** (1.462 ms to 0.640 ms before/after bar, summary table, and a collapsible workload-query reference)

### Troubleshooting
- "Could not connect to PostgreSQL" banner: confirm `docker compose ps` shows `security-logs-dev` healthy and that `.env` is in the repo root.
- Empty or zero KPIs: run `alembic -c alembic/alembic.ini current` and confirm the head includes revision `742e860d116f` (the migration that creates `v_privilege_escalation_timeline` and `idx_audit_event_host_timestamp`).
- Pre-PR lint pass for any dashboard edits:
  ```bash
  venv/bin/ruff check src/dashboard --fix
  venv/bin/ruff format src/dashboard
  venv/bin/ruff check src/dashboard
  venv/bin/ruff format --check src/dashboard
  ```

## Project Structure

```
data-201-security-log-analysis/
├── .github/workflows/     # CI/CD pipelines
├── alembic/               # Database migrations
├── docs/                  # Documentation & ER diagrams
├── sql/                   # SQL scripts and queries
├── notebooks/             # Jupyter notebooks for exploration
├── src/                   # Python source code
│   ├── dashboard/         # Streamlit dashboard (app.py, db.py)
│   ├── loaders/           # Staging and 3NF loaders
│   ├── models/            # SQLAlchemy models
│   └── parsers/           # Log parsing modules
├── tests/                 # Test suite
└── presentation/          # Slides and demo materials
```

## Development Workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Branch naming conventions
- Pull request process
- Code review guidelines

## Key Milestones

- **Feb 5, 2026**: Team roster submission
- **Mar 19, 2026**: Mid-presentation
- **May 7, 2026**: Final presentation & technical report

## License

This project is for educational purposes as part of DATA-201 at SJSU.
