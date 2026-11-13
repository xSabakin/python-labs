# Лабораторна робота №3 — FastAPI + SQLite

Предметна область: реєстр вразливостей вебзастосунку (варіант 1).
`value` — навчальна оцінка небезпеки (score, 0–10), поріг 7.0.

## Встановлення
```bash
pip install fastapi uvicorn pydantic ruff
```

## Початкове заповнення (з кореня репозиторію)
```bash
python -m labs.lab03.seed
```

## Запуск API
```bash
uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000
```
Swagger UI: http://127.0.0.1:8000/docs

## Приклади
```bash
curl -i "http://127.0.0.1:8000/ping"
curl -i "http://127.0.0.1:8000/records?category_id=1&status=new&limit=5"
curl -i -X POST "http://127.0.0.1:8000/records" -H "Content-Type: application/json" \
  -d '{"code":"V01-TEST","title":"Навчальна знахідка","category_id":1,"value":7.5,"status":"new"}'
```
