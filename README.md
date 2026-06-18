# BTL-cnpm

## Chạy dự án

1. Cài dependencies:

```bash
pip install -r requirements.txt
```

2. Cấu hình `.env` với PostgreSQL hiện có.

3. Chạy backend:

```bash
python app.py
```

Hoặc:

```bash
uvicorn backend.src.app:app --reload --host 0.0.0.0 --port 5000
```

## Kiến trúc hiện tại

- `backend/src/domain`: entity và exception.
- `backend/src/application`: use case và business logic.
- `backend/src/infrastructure`: database, ORM model, repository.
- `backend/src/presentation`: router, dependency, request/response handling.
- `static/js/components`: logic UI dùng lại cho frontend.

## Ghi chú

- Database PostgreSQL hiện có được giữ nguyên.
- Các endpoint cũ như `/login`, `/register`, `/forgot-password`, `/api/profile`, `/admin/users` vẫn được giữ để frontend hiện tại tiếp tục hoạt động.
