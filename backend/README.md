# Backend

## Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

Default admin account: `admin` / `admin123`

