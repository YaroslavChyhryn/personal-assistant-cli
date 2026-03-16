# Personal Assistant CLI

CLI-помічник для управління контактами, нотатками та днями народження. Фінальний проєкт з Python Programming.

## Архітектура

Проєкт побудований на принципі **Layered Architecture** з чітким розділенням шарів:

- **Domain** — SQLModel-моделі (єдиний клас = таблиця + схема + об'єкт), валідація, репозиторії (бізнес-логіка запитів)
- **Application** — сервіси (use cases): створення контакту, пошук нотатки, upcoming birthdays
- **Interfaces** — CLI (input/print цикл) та Web UI (Streamlit)

**Ключове правило:** інтерфейси (CLI та Web UI) не працюють напряму з БД. Вони викликають сервіси, сервіси працюють через репозиторії, репозиторії працюють із SQLModel/SQLite.

**Підхід до моделей:** один SQLModel-клас на сутність — він одночасно є визначенням SQLite-таблиці, Pydantic-схемою для валідації, та об'єктом для передачі між шарами.

## Функціональність

### Контакти / Дні народження
- CRUD контактів (ім'я, телефон, email, адреса, день народження)
- Валідація всіх полів: ім'я контакту, телефон (10 цифр), email (формат user@domain.tld), адреса, заголовок нотатки, ім'я тегу
- Зберігання дня народження
- Пошук найближчих днів народження за N днів (з урахуванням вихідних)

### Нотатки / Теги
- CRUD нотаток (створення, перегляд, редагування, видалення)
- Повнотекстовий пошук по заголовку та тілу нотатки
- Теги (додавання, видалення, пошук/фільтрація по тегах)

### CLI
- Інтерактивний цикл команд (input/print)
- Декоратор для обробки помилок
- Коректна обробка некоректного введення без закриття програми

### Web UI (Streamlit)
- Сторінка контактів: перегляд, пошук, створення, видалення, управління телефонами та днями народження
- Сторінка нотаток: перегляд, пошук по тексту та тегах, створення, видалення, управління тегами
- Сторінка календаря: перегляд найближчих днів народження з налаштуванням діапазону днів
- Toast-повідомлення для зворотного зв'язку після дій користувача

## Як користуватися CLI

Після запуску бот очікує команди в інтерактивному режимі:

**Контакти:**

| Команда | Опис | Приклад |
|---|---|---|
| `hello` | Привітання | `hello` |
| `add` | Додати контакт (ім'я + телефон) | `add John 0501234567` |
| `change` | Змінити телефон | `change John 0501234567 0509876543` |
| `phone` | Показати телефон контакту | `phone John` |
| `all` | Показати всі контакти | `all` |
| `add-birthday` | Додати день народження | `add-birthday John 25.12.1990` |
| `show-birthday` | Показати день народження | `show-birthday John` |
| `birthdays` | Найближчі дні народження | `birthdays 7` |
| `add-email` | Додати email контакту | `add-email John john@example.com` |
| `add-address` | Додати адресу контакту | `add-address John 123 Main St` |
| `delete-contact` | Видалити контакт | `delete-contact John` |

**Нотатки:**

| Команда | Опис | Приклад |
|---|---|---|
| `add-note` | Додати нотатку (з тегами через #) | `add-note Shopping Buy milk #urgent` |
| `list-notes` | Показати всі нотатки | `list-notes` |
| `find-note` | Пошук нотатки | `find-note keyword` |
| `edit-note` | Редагувати нотатку | `edit-note 1 NewTitle new body` |
| `delete-note` | Видалити нотатку | `delete-note 1` |
| `find-tag` | Пошук нотаток за тегом | `find-tag python` |
| `add-tag` | Додати тег(и) до нотатки | `add-tag 1 python dev` |
| `remove-tag` | Видалити тег з нотатки | `remove-tag 1 python` |

**Загальні:**

| Команда | Опис | Приклад |
|---|---|---|
| `close` / `exit` | Вийти з програми | `exit` |

## Як користуватися Web UI

Запустити Streamlit-додаток:
```bash
streamlit run app/ui/__init__.py
```

Після запуску відкриється браузер з трьома сторінками:
- **Contacts** — управління контактами (CRUD, телефони, дні народження)
- **Notes** — управління нотатками (CRUD, пошук, теги)
- **Calendar** — перегляд найближчих днів народження

## Технології

| Технологія | Призначення |
|---|---|
| Python 3.12+ | Мова |
| SQLModel | ORM (поверх SQLAlchemy + Pydantic) |
| SQLite | Локальне сховище даних |
| Streamlit | Web UI |
| pandas | Табличне відображення даних у Web UI |
| pytest | Тестування |
| ruff | Лінтинг та форматування |
| pre-commit | Git hooks для якості коду |

## Структура проєкту

```
personal-assistant-cli/
├── pyproject.toml
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── requirements.txt
├── docs/
│   └── BACKLOG.md
├── app/
│   ├── main.py
│   ├── cli.py
│   ├── config.py
│   ├── bootstrap.py
│   ├── db.py
│   ├── domain/
│   │   ├── models.py
│   │   └── repository.py
│   ├── application/
│   │   ├── contacts_service.py
│   │   ├── notes_service.py
│   │   └── calendar_service.py
│   └── ui/
│       ├── __init__.py
│       ├── services.py
│       ├── helpers.py
│       ├── contacts.py
│       ├── notes.py
│       └── calendar.py
└── tests/
    ├── unit/
    └── integration/
```

## Розгортання

### Передумови

- Python 3.12+
- pip або uv

### Встановлення

1. Клонувати репозиторій:
```bash
git clone https://github.com/<your-username>/personal-assistant-cli.git
cd personal-assistant-cli
```

2. Створити та активувати віртуальне середовище:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

3. Встановити як пакет:
```bash
pip install .
```

4. Запустити CLI з будь-якого місця системи (віртуальне середовище має бути активоване):
```bash
assistant
```

5. Або запустити Web UI:
```bash
streamlit run app/ui/__init__.py
```

> **Примітка:** команда `assistant` доступна лише при активованому віртуальному середовищі, оскільки виконуваний файл встановлюється у `.venv/bin/`. Перед запуском переконайтесь, що виконали `source .venv/bin/activate`.

> **Зберігання даних:** при першому запуску у домашній директорії користувача створюється папка `~/.assistant/` з файлом бази даних `assistant.db`. Усі контакти, нотатки та теги зберігаються там і не втрачаються після перезапуску програми.

Альтернативний запуск (без встановлення пакету):
```bash
pip install -r requirements.txt
python -m app.main
```

### Для розробників

```bash
pip install -e ".[dev]"
pre-commit install
```

### Розробка

Запустити лінтер:
```bash
ruff check app/
ruff format app/
```

Запустити pre-commit на всіх файлах:
```bash
pre-commit run --all-files
```

## Git Workflow

- `main` — стабільна гілка
- `feature/<name>` — гілки для окремих фіч
