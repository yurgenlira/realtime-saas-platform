# Realtime SaaS Platform

## Project Overview

Multi-tenant webhook ingestion platform designed using event-driven architecture and DevOps best practices.

## Architecture

Client → FastAPI

## Tech Stack

- FastAPI
- Python 3.12

## Local Development

Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies
```bash
cd apps/server
pip install -r requirements.txt
```

Run application
```bash
uvicorn main:app --app-dir src --reload
```

## Repository Structure
```
.
├── apps
│   └── server
│       ├── requirements.txt
│       └── src
│           └── main.py
├── CHANGELOG.md
└── README.md
```

## Changelog

See [Changelog](CHANGELOG.md)
