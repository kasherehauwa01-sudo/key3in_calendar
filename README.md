# Key3in

Key3in — mobile-first PWA-календарь с общей датой и персональной заметкой каждого пользователя. Production URL: `https://kvasmix.ru/key3in/`.

## Возможности

- цельная сетка из 6 недель, понедельник — первый день; соседние месяцы доступны для выбора;
- навигация кнопками и горизонтальным свайпом, переход и мягкое выделение сегодняшней даты;
- регистрация и вход по логину и пин-коду, персональные имя и цвет;
- несколько пользователей могут оставить по одной заметке на общую дату;
- создание, редактирование и удаление пустой заметки без перезагрузки;
- регистронезависимый поиск по подстроке с debounce 300 мс и возвратом в результаты;
- кэш уже загруженных месяцев, skeleton и Snackbar ошибок;
- устанавливаемая PWA: оболочка, календарные данные, поиск и редактирование работают офлайн;
- доступность: семантика, aria-label, клавиатурный focus, touch targets и reduced motion.

## Архитектура

- **Frontend:** React 19, TypeScript, Vite, Material UI; API URL вычисляется из `import.meta.env.BASE_URL`, Vite base равен `/key3in/`. IndexedDB хранит заметки и очередь локальных изменений.
- **Backend:** FastAPI, async SQLAlchemy 2, Pydantic; REST находится под `/api`, а внешний reverse proxy добавляет `/key3in`.
- **БД:** PostgreSQL; `users`, `sessions` и `notes`; заметка уникальна для пары `(date, user_id)`. `DATE` исключает timezone-сдвиги. Поиск изолирован в service layer для будущего FTS.
- **Production:** multi-stage frontend image + Nginx, backend image с автоматической миграцией, PostgreSQL volume.

## Пользователи и настройки

При первом запуске показывается регистрация: имя, уникальный логин и цифровой пин-код из 4–12 цифр. Пин-код хранится только как `scrypt`-хэш с индивидуальной солью. Сессия выдаётся на 90 дней. Все вошедшие пользователи видят общие заметки, но изменяют только собственную запись дня. Имя перед текстом окрашивается выбранным пользователем цветом. В настройках можно изменить имя и цвет, выйти из аккаунта, а также одним нажатием скопировать `/var/www/html/vr/update_key3in.sh`.

## Работа офлайн и синхронизация

Service worker кэширует оболочку приложения. Заметки каждого открытого месяца сохраняются в IndexedDB. Создание, изменение и удаление сначала атомарно отражаются в локальном хранилище и записываются в persistent-очередь `syncQueue`, поэтому переживают закрытие вкладки или установленного PWA. При событии `online` очередь последовательно отправляется на сервер; запись удаляется из неё только после успешного ответа. Несколько офлайн-изменений одной даты схлопываются в последнее. Применяется понятная для персональной записи пользователя стратегия **последнее локальное изменение побеждает**.

Индикатор в верхней части показывает состояния «Онлайн», «Офлайн» и «Синхронизация». В офлайне поиск выполняется по локально сохранённым заметкам. Не открывавшиеся ранее месяцы могут не содержать серверные данные до первого подключения.

## API

`POST /key3in/api/auth/register`, `POST /key3in/api/auth/login`, `GET|PUT /key3in/api/users/me`, `GET /key3in/api/health`, `GET /key3in/api/notes?year=2026&month=9`, `GET /key3in/api/notes/{date}`, `POST /key3in/api/notes`, `PUT /key3in/api/notes/{date}`, `DELETE /key3in/api/notes/{date}`, `GET /key3in/api/notes/search?q=...`. Максимум текста — 20 000 символов. Пустое обновление удаляет запись. `PUT` и `DELETE` идемпотентны, чтобы безопасно повторять операции из offline-очереди.

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

Manifest, service worker, start URL, scope и icons используют `/key3in/`. Для проверки offline-режима сначала откройте нужный месяц онлайн, затем включите DevTools → Network → Offline, измените заметку, верните Online и убедитесь, что индикатор синхронизации завершился. После TLS-развертывания откройте:

- `https://kvasmix.ru/key3in/`
- `https://kvasmix.ru/key3in/api/health`
- `https://kvasmix.ru/key3in/manifest.webmanifest`
- DevTools → Application → Manifest / Service Workers.

Вручную требуются: секрет в `.env`, добавление location в существующий Nginx, DNS/TLS (если ещё не настроены), регулярные внешние backup. При смене PostgreSQL-пароля существующего volume синхронно обновите роль в БД; одной правки `.env` недостаточно.

## Уведомления

Колокольчик справа от поиска открывает список заметок, добавленных другими пользователями. Непрочитанные записи выделяются жирным и отмечаются красной точкой на колокольчике; запись помечается прочитанной при открытии, также доступна кнопка «Прочитать все». Пока приложение открыто, оно опрашивает сервер каждые 30 секунд. После разрешения браузера новая запись показывается как системное уведомление со звуком и вибрацией (если эти возможности поддерживаются устройством и не запрещены его настройками).
