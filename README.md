# Key3in

Key3in — mobile-first PWA-календарь с одной ежедневной заметкой на дату. Production URL: `https://kvasmix.ru/key3in/`.

## Возможности

- цельная сетка из 6 недель, понедельник — первый день; соседние месяцы доступны для выбора;
- навигация кнопками и горизонтальным свайпом, переход и мягкое выделение сегодняшней даты;
- создание, редактирование и удаление пустой заметки без перезагрузки;
- регистронезависимый поиск по подстроке с debounce 300 мс и возвратом в результаты;
- кэш уже загруженных месяцев, skeleton и Snackbar ошибок;
- устанавливаемая PWA: shell работает офлайн, API намеренно использует только сеть;
- доступность: семантика, aria-label, клавиатурный focus, touch targets и reduced motion.

## Архитектура

- **Frontend:** React 19, TypeScript, Vite, Material UI; API URL вычисляется из `import.meta.env.BASE_URL`, Vite base равен `/key3in/`.
- **Backend:** FastAPI, async SQLAlchemy 2, Pydantic; REST находится под `/api`, а внешний reverse proxy добавляет `/key3in`.
- **БД:** PostgreSQL; `notes(id, date, text, created_at, updated_at)`, уникальный индекс даты. `DATE` исключает timezone-сдвиги. Поиск изолирован в service layer для будущего FTS.
- **Production:** multi-stage frontend image + Nginx, backend image с автоматической миграцией, PostgreSQL volume.

## API

`GET /key3in/api/health`, `GET /key3in/api/notes?year=2026&month=9`, `GET /key3in/api/notes/{date}`, `POST /key3in/api/notes`, `PUT /key3in/api/notes/{date}`, `DELETE /key3in/api/notes/{date}`, `GET /key3in/api/notes/search?q=...`. Максимум текста — 20 000 символов. Пустое обновление удаляет запись.

## Локальная разработка

Требуются Python 3.12+, Node 22+ и PostgreSQL (для тестов используется SQLite):

```bash
cp .env.example .env
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
# другой терминал
cd frontend && npm install && npm run dev
```

Vite dev URL содержит `/key3in/`. Для связи с локальным backend удобнее запускать весь Compose либо временно настроить proxy Vite.

## Проверки и production build

```bash
cd backend && pytest && ruff check .
cd frontend && npm install && npm test && npm run lint && npm run build
cp .env.example .env             # замените пароль
sudo docker compose config
sudo docker compose build
```

## Развертывание на Timeweb

```bash
sudo mkdir -p /opt/key3in && sudo chown "$USER":"$USER" /opt/key3in
cd /opt/key3in
git clone <URL-РЕПОЗИТОРИЯ> .
cp .env.example .env
openssl rand -base64 36           # результат внесите как POSTGRES_PASSWORD
nano .env
sudo docker compose up -d --build
sudo docker compose ps
curl http://127.0.0.1:8083/key3in/api/health
```

Добавьте содержимое `deploy/nginx-key3in.conf` **в существующий** HTTPS `server {}` домена, не заменяя остальные location, затем:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Конфигурация проксирует только `/key3in` и `/key3in/`; внутренний Nginx отделяет API и возвращает `index.html` для прямой загрузки frontend route.

## Миграции и обновление

Backend при старте исполняет `alembic upgrade head`. Ручной запуск и обновление:

```bash
sudo docker compose exec backend alembic upgrade head
git pull --ff-only
sudo docker compose up -d --build
```

## Backup и восстановление

```bash
sudo docker compose exec -T postgres pg_dump -U key3in -d key3in -Fc > key3in-$(date +%F).dump
cat backup.dump | sudo docker compose exec -T postgres pg_restore -U key3in -d key3in --clean --if-exists
```

## PWA и проверка

Manifest, service worker, start URL, scope и icons используют `/key3in/`. После TLS-развертывания откройте:

- `https://kvasmix.ru/key3in/`
- `https://kvasmix.ru/key3in/api/health`
- `https://kvasmix.ru/key3in/manifest.webmanifest`
- DevTools → Application → Manifest / Service Workers.

Вручную требуются: секрет в `.env`, добавление location в существующий Nginx, DNS/TLS (если ещё не настроены), регулярные внешние backup. При смене PostgreSQL-пароля существующего volume синхронно обновите роль в БД; одной правки `.env` недостаточно.
