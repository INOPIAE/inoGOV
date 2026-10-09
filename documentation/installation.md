# inoGOV - Installation, Start and Tests

inoGOV consists of a FastAPI backend (PostgreSQL, Alembic) and a Vue.js frontend.
The commands below use Windows PowerShell and are run from the repository root unless stated otherwise.

```
inoGOV/
  backend/    FastAPI application, Alembic migrations, tests
  frontend/   Vue 3 application (Vite), tests
  documentation/
```

## 1. Prerequisites

| Tool | Version used in development |
|---|---|
| Python | 3.12 |
| Node.js / npm | 24 / 11 (Node 20 or newer should work) |
| PostgreSQL | 17 |

## 2. Database

Create a database user and an empty database (as a PostgreSQL superuser, for example with `psql -U postgres`):

```sql
CREATE USER inogov_user WITH PASSWORD 'choose-a-password';
CREATE DATABASE inogov_db OWNER inogov_user;
```

Check the login:

```powershell
psql -h localhost -p 5432 -U inogov_user -d inogov_db
```

## 3. Backend

### 3.1 Install

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3.2 Configure

Copy the template and edit it:

```powershell
Copy-Item .env.example .env
```

`.env` contains secrets and is excluded from Git. Environment variables with the same name override values in the file.

| Variable | Purpose | Default |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | PostgreSQL connection | localhost, 5432, inogov_user, inogov_password, inogov_db_dev |
| `SECRET_KEY` | Signs login tokens and email links. **Required.** Use a long random value. | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifetime of a login token | 60 |
| `LOCKOUT_TIERS` | Login lockout as `failed attempts:minutes`, comma separated. `3:3,5:10,10:60` locks for 3 min after 3 failures, 10 min after 5, 60 min after 10. | `3:3,5:10,10:60` |
| `APP_NAME`, `COPYRIGHT_NAME` | Name shown in the header, name shown in the footer copyright | inoGOV |
| `PUBLIC_SEARCH` | `true`: place search and master data readable without login. `false`: only for signed-in users. | true |
| `ADMIN_OTP_REQUIRED` | `true`: administrators must set up OTP before they can continue | true |
| `FRONTEND_URL` | Base URL used in links inside emails | http://localhost:5173 |
| `CORS_ORIGINS` | Allowed browser origins, comma separated | http://localhost:5173 |
| `PASSWORD_RESET_MINUTES` | Validity of the "forgot password" link | 60 |
| `ADMIN_LINK_HOURS` | Validity of invitation and admin reset links | 24 |
| `IMPORT_ARCHIVE_DIR` | Folder where processed import files and their protocol are stored | import_archive |
| `IMPORT_MAX_MB` | Maximum size of an uploaded import file | 10 |
| `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME` | Outgoing email | see below |

Generate a secret key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Email.** Without `SMTP_SERVER` no email is sent; the message including its link is only written to the API log (useful for local development). The connection type depends on the port:

| Port | Connection |
|---|---|
| 465 | TLS from the start (for example `smtp.strato.de`) |
| 587 | STARTTLS (for example Gmail, Office 365) |
| 25 | plain, no TLS (local Postfix) |

Gmail requires an app password, the normal account password does not work.

### 3.3 Create the tables and base data

```powershell
alembic upgrade head
```

This creates all tables and seeds the roles (`admin`, `user`) and the languages (German, English, Polish, Russian, Ukrainian).

### 3.4 Create the first administrator

```powershell
python -m app.create_admin --username admin --email you@example.com
```

The password is asked for twice and is not stored in the shell history. After the first login the administrator is guided through the OTP setup (see `ADMIN_OTP_REQUIRED`). Further users are invited from the web interface (User management).

### 3.5 Start

```powershell
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive API documentation (Swagger): http://localhost:8000/docs

Restart the server after changing `.env`.

### 3.6 Database migrations

```powershell
alembic upgrade head                                   # apply
alembic revision --autogenerate --rev-id 0004 -m "name"   # create after a model change
alembic downgrade -1                                   # undo the last migration
```

Migration files are named `<revision>_<slug>.py` (see `file_template` in `alembic.ini`). Pass `--rev-id` with the next number to keep the files in order.

## 4. Frontend

### 4.1 Install

```powershell
cd frontend
npm install
```

Optional: if the API does not run at http://localhost:8000, create `frontend/.env` (template: `.env.example`):

```
VITE_API_URL=http://localhost:8000
```

Bootstrap and all other libraries are installed locally from npm; nothing is loaded from the internet at runtime.

### 4.2 Start (development)

```powershell
npm run dev
```

Open http://localhost:5173. The backend must be running, and the address must be listed in `CORS_ORIGINS`.

### 4.3 Production build

```powershell
npm run build
```

The result is written to `frontend/dist/` and can be served by any web server. Set `FRONTEND_URL` and `CORS_ORIGINS` in the backend to the public address.

### 4.4 Translations

Texts are written in English and translated through gettext files in `frontend/src/language/`. German and English are provided.

```powershell
npm run i18n:extract   # collect texts from the code into messages.pot and de/app.po
npm run i18n:compile   # build translations.json from the .po files
```

Translate new entries (empty `msgstr`) in `src/language/de/app.po`, then compile. `dev`, `build` and `test` run the compile step automatically. GNU gettext is not required.

## 5. Tests

### 5.1 Backend

```powershell
cd backend
venv\Scripts\Activate.ps1
python -m pytest -q
```

The tests use an in-memory SQLite database; PostgreSQL does not have to be running and `.env` values do not influence the result. Useful variants:

```powershell
python -m pytest -q tests/test_imports.py      # one file
python -m pytest -q -k otp                     # tests matching a name
python -m pytest -x -q                         # stop at the first failure
```

### 5.2 Frontend

```powershell
cd frontend
npm test
```

Run a single file:

```powershell
npx vitest run src/__tests__/imports.test.js
```

The first start of each test file can take several seconds on Windows. The configuration limits the run to two parallel workers and a 30 second timeout per test.

## 6. Importing data

Administrators find the page **Management > Imports** in the web interface.

**ImportLueck** reads a CSV file with a header row and three columns: Polish place name, Polish district name, coordinate (for example `B5`).

- The Polish district is looked up by name (case and extra spaces are ignored). If it does not exist, a new district with a Polish name is created and listed in the report.
- Each row creates a new place with its Polish name and a map reference on the map "Lück". Duplicates are not checked.
- Semicolon, comma or tab separated files are accepted; UTF-8 and Windows-1250 encodings are detected.
- Rows with errors are skipped and listed with their line number; all other rows are imported.
- After processing, the file and a protocol (`.log`) are stored in `IMPORT_ARCHIVE_DIR`. The folder is excluded from Git.

## 7. Troubleshooting

| Symptom | Cause and remedy |
|---|---|
| `password authentication failed for user` | `DB_USER` / `DB_PASSWORD` in `.env` differ from the PostgreSQL user. Test with `psql`. |
| Alembic cannot connect | Check `DB_*` values; make sure no environment variable overrides them (`echo $env:DB_PASSWORD`). |
| Email sending fails with a timeout | Wrong port for the server. Use 465 (TLS) or 587 (STARTTLS) as the provider documents. |
| Browser shows CORS errors | Add the frontend address to `CORS_ORIGINS` and restart the backend. |
| Login works but pages redirect to "My account" | The administrator has not set up OTP yet (`ADMIN_OTP_REQUIRED=true`). |
| Search page redirects to the login | `PUBLIC_SEARCH=false`. |
| Email links point to the wrong address | Set `FRONTEND_URL`. |
| Frontend tests fail with "Failed to start worker" | The machine is overloaded; run a single file or close other programs. |
