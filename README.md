# Report Catalog

Multi-source reporting metadata explorer: a **Flask** web app backed by **SQL Server**, with **T-SQL ETL** that merges interactive dashboard history and SSRS-style catalog data into one searchable index.

![Python](https://img.shields.io/badge/Python-3.10+-3670A0?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web-000?style=flat-square&logo=flask&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-database-CC2927?style=flat-square&logo=microsoft-sql-server&logoColor=white)

---

## Overview

Organizations often scatter report definitions across portals, SSRS, and BI tools. This sample illustrates how you can:

- Load metadata from **more than one source** into a consolidated table (`dbo.catalog_data`)
- Offer **browse-by-category** pages with paging
- Expose **parameterized**, cross-category search over ODBC (**`pyodbc`**) to avoid naive string concatenation against SQL Server

Hosts, linked servers, and ODBC targets are placeholders or env-driven—you plug in names from **your own** demo or lab instance.

---

## Features

| Capability | Detail |
|------------|--------|
| Browse | Category views with paging over catalog rows |
| Search | Cross-category search endpoint backed by parameterized `LIKE` queries |
| Config | `.env`/environment-driven connection settings (including optional SQL auth vs Windows auth) |

---

## Tech stack

- **Backend:** Flask, Python 3.10+
- **Data:** SQL Server, `pyodbc` (recommended: ODBC Driver 17 or 18 for SQL Server)
- **Deploy sample:** IIS-style `web.config` stub for **`wfastcgi`** (paths must match your machine)

---

## Repository layout

```
report_catalog/
├── report_catalog.sln
└── Catalog/                 ← Flask application
    ├── runserver.py
    ├── main/
    ├── templates/
    └── web.config           ← IIS / wfastcgi stub
```

You can rename `report_catalog` if you prefer a different top-level folder name.

---

## For reviewers / recruiters

| Area | Where to look |
|------|----------------|
| Python / Flask | [`report_catalog/Catalog/main/views.py`](report_catalog/Catalog/main/views.py) — routes, ODBC factory, parameterized search |
| SQL / data engineering | [`report_catalog/Catalog/main/catalogquery.sql`](report_catalog/Catalog/main/catalogquery.sql) — multi-source merge pattern (`#results` → `#main` → insert), placeholder linked servers |
| Ops / IIS | [`report_catalog/Catalog/web.config`](report_catalog/Catalog/web.config) — generic `wfastcgi` handler (adjust paths locally) |

---

## Quick start (local development)

**Prerequisites:** Python 3.10+, ODBC driver for SQL Server, and a database (e.g. **`ReportCatalog`**) whose `dbo.catalog_data` aligns with the queries in this app.

From the Flask app directory:

```bash
cd report_catalog/Catalog
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
set CATALOG_SQL_SERVER=your_host_or_instance
set CATALOG_SQL_DATABASE=ReportCatalog
python runserver.py
```

Open **http://localhost:5555** (defaults in `runserver.py`; override with `SERVER_HOST` / `SERVER_PORT`).

See **[`report_catalog/Catalog/.env.example`](report_catalog/Catalog/.env.example)** for the full set of supported environment variables (driver, credentials, optional report-type overrides, etc.).

---

## ETL (`catalogquery.sql`)

The SQL script sketches a repeatable pattern:

1. Truncate target
2. Fill temp tables from **web dashboard** history and **SSRS execution** metadata
3. Unify into **`#results`**, optionally enrich with `catalog_manual_data`
4. Insert into the persisted catalog table

Replace placeholders such as **`LINKED_DW`**, **`YOUR_SSRS_CATALOG`**, **`ReportCatalog`**, and **`example.local`** URL bases with objects that exist in **your** environment.

---

## License / attribution

Portfolio-style demonstration derived from internal-style tooling; names and identifiers are fictionalized or scrubbed. Sensitive or employer-specific wording and sample binary artifacts were omitted or removed from tracked content where applicable.
