# DATA-201 Security Log Analysis

Relational database analysis of the AIT-LDSv2.0 cybersecurity dataset for DATA-201 (Database Systems) at San Jose State University.

## Project Overview

Analysis of a simulated enterprise network under attack using the Austrian Institute of Technology Log Data Set V2.0. The dataset includes:

- **22 networked hosts** (firewalls, servers, workstations)
- **~1.8M log events** across multiple log types
- **~62K labeled attack events** with ground truth
- **Multi-stage attack chain**: Reconnaissance → Exploitation → Privilege Escalation → Data Exfiltration

## Team

| Name | Email | GitHub |
|------|-------|--------|
| Naman Sudan | namansudans@gmail.com | @namansudan |
| River Roseveare-Hunt | river.roseveare-hunt@sjsu.edu | TBD |
| Ishaan Shetty | ishaan.shetty@sjsu.edu | TBD |
| TBD | TBD | TBD |

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
   alembic upgrade head
   ```

6. **Verify setup**
   ```bash
   python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://security_logs_user:password@localhost:5432/security_logs'); print('Connected!' if engine.connect() else 'Failed')"
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
