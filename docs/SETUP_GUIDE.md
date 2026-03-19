# Team Setup Guide

**Linear Issue:** [DAT-30](https://linear.app/data-201/issue/DAT-30/team-onboarding-setup-guide-pgadmin-config-and-first-exploration)

This guide walks you through setting up the entire development environment from scratch. Follow every step in order.

---

## Prerequisites

You need three things installed before anything else:

### 1. Docker Desktop

Docker runs our PostgreSQL database in a container so everyone has the exact same setup.

| OS | Download |
|----|----------|
| **Mac** | https://docs.docker.com/desktop/setup/install/mac-install/ |
| **Windows** | https://docs.docker.com/desktop/setup/install/windows-install/ |

After installing, **open Docker Desktop** and let it finish starting up. You'll see a whale icon in your menu bar (Mac) or system tray (Windows) when it's ready.

### 2. Git

| OS | How to install |
|----|---------------|
| **Mac** | Open Terminal and run `git --version`. If not installed, it will prompt you to install Xcode Command Line Tools. Click Install. |
| **Windows** | Download from https://git-scm.com/downloads/win and install with default options. |

### 3. Python 3.12+

| OS | Download |
|----|----------|
| **Mac** | https://www.python.org/downloads/macos/ |
| **Windows** | https://www.python.org/downloads/windows/ - **check "Add Python to PATH"** during install |

Verify with:
```bash
python3 --version   # Mac
python --version     # Windows
```

---

## Step 1: Create Your Workspace

Create a folder on your computer that will hold everything for this project. Name it whatever you like (e.g., `data-201-group-project`).

```bash
# Mac
mkdir ~/Desktop/data-201-group-project
cd ~/Desktop/data-201-group-project

# Windows (PowerShell)
mkdir ~\Desktop\data-201-group-project
cd ~\Desktop\data-201-group-project
```

---

## Step 2: Clone the Repository

Inside your workspace folder:

```bash
git clone https://github.com/NamanSudan/data-201-security-log-analysis.git
```

This creates a `data-201-security-log-analysis/` folder with all the project code.

---

## Step 3: Download the Dataset

Download the Russell Mitchell dataset from the shared link (provided by Naman). Extract it so the `russellmitchell/` folder sits **at the same level** as the repo:

```
data-201-group-project/
├── data-201-security-log-analysis/   <-- the repo you just cloned
└── russellmitchell/                  <-- the dataset you downloaded
    ├── dataset.yaml
    ├── gather/
    ├── labels/
    ├── rules/
    ├── processing/
    └── environment/
```

> **Important:** The notebooks expect the dataset to be at this exact location relative to the repo. If it's somewhere else, you'll need to adjust the path in the notebook.

---

## Step 4: Set Up Environment File

```bash
cd data-201-security-log-analysis

# Mac
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

The default values work for local development - no changes needed.

---

## Step 5: Start the Database

Make sure **Docker Desktop is running** (check for the whale icon), then:

```bash
docker-compose up -d
```

This starts three containers:
| Container | What it does | Port |
|-----------|-------------|------|
| `security-logs-dev` | PostgreSQL development database | `localhost:5432` |
| `security-logs-test` | PostgreSQL test database (ephemeral) | `localhost:5433` |
| `security-logs-pgadmin` | pgAdmin web UI for browsing the database | `localhost:5050` |

Wait about 15 seconds, then verify all three are running:

```bash
docker ps
```

You should see three containers with `STATUS` showing `Up` and `(healthy)` for the Postgres ones.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `port is already allocated` on 5432 | Another Postgres is running. Stop it or change the port in `docker-compose.yml`. |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running. Open it and wait for it to start. |
| Container keeps restarting | Run `docker-compose logs db-dev` to see the error. |

---

## Step 6: Connect with pgAdmin

1. Open your browser and go to **http://localhost:5050**

2. **Log in** with:
   - Email: `admin@localhost.com`
   - Password: `admin`

3. **Add the database server:**
   - Click **"Add New Server"** (or right-click "Servers" → "Register" → "Server")
   - **General tab:**
     - Name: `Security Logs Dev`
   - **Connection tab:**
     - Host: `db-dev`
     - Port: `5432`
     - Maintenance database: `security_logs`
     - Username: `security_logs_user`
     - Password: `change_this_password`
     - Check **"Save password"**
   - Click **Save**

   > **Why `db-dev` and not `localhost`?** pgAdmin runs inside Docker on the same network as PostgreSQL. Docker containers talk to each other using service names, not `localhost`.

4. **Verify the connection:**
   - Expand: Servers → Security Logs Dev → Databases → security_logs
   - Right-click `security_logs` → **Query Tool**
   - Type `SELECT 1;` and click the play button (or press F5)
   - You should see a result with the value `1`

If you see that - congratulations, your database is working!

---

## Step 7: Install Python Dependencies & JupyterLab

Go back to your terminal, make sure you're in the repo folder:

```bash
cd data-201-security-log-analysis
```

Create a virtual environment and install dependencies:

```bash
# Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Note:** After activating the venv, you should see `(venv)` at the beginning of your terminal prompt.

---

## Step 8: Launch JupyterLab

With your virtual environment activated:

```bash
jupyter lab
```

This opens JupyterLab in your browser (usually at `http://localhost:8888`).

Navigate to `notebooks/` and open `01_explore_hosts.ipynb` to start exploring the dataset.

---

## Quick Reference

### Connection Details

| Setting | Value |
|---------|-------|
| **Host** (from your machine) | `localhost` |
| **Host** (from pgAdmin/Docker) | `db-dev` |
| **Port** | `5432` |
| **Database** | `security_logs` |
| **Username** | `security_logs_user` |
| **Password** | `change_this_password` |
| **pgAdmin URL** | http://localhost:5050 |
| **pgAdmin Login** | `admin@localhost.com` / `admin` |

### Common Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# Stop and delete all data (fresh start)
docker-compose down -v

# Check container status
docker ps

# View database logs
docker-compose logs db-dev

# Activate Python environment (Mac)
source venv/bin/activate

# Activate Python environment (Windows)
.\venv\Scripts\Activate.ps1

# Launch JupyterLab
jupyter lab
```

---

## What's Next?

Once you have everything running:
1. Open the notebook `01_explore_hosts.ipynb` in JupyterLab
2. Follow along to see how raw YAML data becomes a database table
3. Check Linear for your assigned tasks