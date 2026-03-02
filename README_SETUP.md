# Quick setup (development)

## 1. Create a Python virtualenv and activate it

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Run migrations and create superuser

```powershell
python manage.py migrate
python manage.py createsuperuser
```

## 3. Run development server (ASGI with channels)

```powershell
python manage.py runserver
```

## Notes
- This scaffold uses an in-memory channel layer for local development. For production, configure Redis and secure channels.
- Add trained `.pt` model files later to `media/models/` and assign them in the Model Management UI.
