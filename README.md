# 🤖 TeleFixBot — Telegram-бот для продажи VPN-подписок

Автоматизированный бот для продажи и управления VPN-подписками прямо в Telegram. Поддерживает автоматическую выдачу ключей, встроенную оплату, уведомления об истечении подписки и мультиплатформенные ссылки на клиенты.

---

## ⚡ Возможности

- 🛒 Продажа VPN-подписок с выбором тарифа
- 💳 Автоматический приём оплаты через **aiosend**
- 🔑 Мгновенная выдача VPN-ключа после оплаты
- 📅 Уведомления об истечении подписки (APScheduler)
- 📦 Фоновые задачи через **Celery + Redis**
- 🖥 Ссылки на клиенты под Windows / Linux / macOS
- 👤 Личный кабинет пользователя
- 🛡 Панель администратора
- 🐳 Полный деплой через Docker Compose

---

## 🛠 Стек технологий

| Слой | Технологии |
|---|---|
| Бот | Python 3.11+, aiogram 3.x |
| База данных | PostgreSQL + asyncpg + SQLAlchemy (async) |
| Миграции | Alembic |
| Очереди | Celery + Redis |
| Планировщик | APScheduler |
| Оплата | aiosend |
| HTTP | httpx, httpx[http2] |
| Кэш | cachetools |
| Деплой | Docker, Docker Compose |

---

## 🚀 Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/byteow/TeleFixBot.git
cd TeleFixBot
```

### 2. Настрой переменные окружения

```bash
cp .env.example .env
```

Открой `.env` и заполни все значения (см. раздел ниже).

### 3. Запусти через Docker Compose

```bash
docker compose up -d --build
```

### 4. Примени миграции

```bash
docker compose exec bot alembic upgrade head
```

Бот запущен ✅

---

## ⚙️ Переменные окружения

| Переменная | Описание |
|---|---|
| `API_TOKEN` | Токен бота от [@BotFather](https://t.me/BotFather) |
| `PG_URI` | Строка подключения к PostgreSQL (`postgresql+asyncpg://...`) |
| `ADMIN_USERNAME` | Username администратора в Telegram |
| `ADMINS_IDS` | ID администраторов через запятую (`123456,789012`) |
| `BOT_USERNAME` | Username бота без @ |
| `SOFT_WIN_LINK` | Ссылка на клиент для Windows |
| `SOFT_LINUX_LINK` | Ссылка на клиент для Linux |
| `SOFT_MAC_LINK` | Ссылка на клиент для macOS |
| `VIRUS_TOTAL_LINK` | Ссылка на проверку файла на VirusTotal |

---

## 📁 Структура проекта

```
TeleFixBot/
├── src/                  # Основной код бота
│   ├── handlers/         # Обработчики команд и callback
│   ├── models/           # SQLAlchemy модели
│   ├── services/         # Бизнес-логика
│   └── ...
├── .env.example          # Пример конфигурации
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── servers.sql           # Начальные данные для серверов
├── insert.sh             # Скрипт инициализации БД
└── alembic/              # Миграции
```

---

## 🐳 Запуск без Docker (локально)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# заполни .env

alembic upgrade head
python -m src.bot
```

> Убедись, что PostgreSQL и Redis запущены локально.

---

## 👨‍💻 Автор

**byteow** — Full Stack Developer (Python / React)

- GitHub: [@byteow](https://github.com/byteow)
- Telegram: [@warfenow](https://t.me/artembyteow)
