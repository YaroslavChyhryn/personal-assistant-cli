# Personal Assistant

Помічник для управління контактами, нотатками та днями народження з CLI та Web UI інтерфейсами. Фінальний проєкт з Python Programming.

## Архітектура

Проєкт побудований на принципі **Layered Architecture** з чітким розділенням шарів:

- **Domain** — SQLModel-моделі (єдиний клас = таблиця + схема + об'єкт), валідація, репозиторії (бізнес-логіка запитів)
- **Application** — сервіси (use cases): створення контакту, пошук нотатки, upcoming birthdays
- **Interfaces** — CLI (input/print цикл), Web UI (Streamlit)

**Ключове правило:** CLI не працює напряму з БД. CLI викликає сервіси, сервіси працюють через репозиторії, репозиторії працюють із SQLModel/SQLite.

**Підхід до моделей:** один SQLModel-клас на сутність — він одночасно є визначенням SQLite-таблиці, Pydantic-схемою для валідації, та об'єктом для передачі між шарами.

## Функціональність

### Контакти / Дні народження
- CRUD контактів
- Валідація телефону та email
- Зберігання дня народження
- Пошук найближчих днів народження за N днів

### Нотатки / Теги
- CRUD нотаток
- Повнотекстовий пошук
- Теги (додавання, видалення, пошук/фільтрація по тегах)

### CLI
- Інтерактивний цикл команд (input/print)
- Декоратор для обробки помилок

### Web UI (Streamlit)
- Сторінка контактів — пошук, створення, редагування телефонів, видалення
- Сторінка нотаток — пошук за текстом і тегами, створення, управління тегами
- Сторінка календаря — найближчі дні народження з налаштуванням періоду (слайдер)

## Технології

| Технологія | Призначення |
|---|---|
| Python 3.12+ | Мова |
| SQLModel | ORM (поверх SQLAlchemy + Pydantic) |
| SQLite | Локальне сховище даних |
| Streamlit | Web UI |
| pandas | Табличне відображення даних |
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
│   ├── ui.py
│   ├── config.py
│   ├── bootstrap.py
│   ├── db.py
│   ├── domain/
│   │   ├── models.py
│   │   └── repository.py
│   └── application/
│       ├── contacts_service.py
│       ├── notes_service.py
│       └── calendar_service.py
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

3. Встановити залежності:
```bash
pip install -r requirements.txt
```

4. Встановити pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

5. Запустити застосунок:

**CLI режим:**
```bash
python -m app.main
```

**Web UI (Streamlit):**
```bash
PYTHONPATH=. streamlit run app/ui/__init__.py
```

> На Windows використовуйте:
> ```bash
> set PYTHONPATH=. && streamlit run app/ui.py
> ```

## Приклади використання

### CLI

```
$ python -m app.main

Welcome to Personal Assistant!
Enter a command (or 'help'): help

Available commands:
  add-contact     — Create a new contact
  search-contact  — Search contacts by name
  show-contacts   — List all contacts
  add-phone       — Add a phone to a contact
  change-phone    — Change an existing phone
  remove-phone    — Remove a phone from a contact
  set-birthday    — Set a contact's birthday
  birthdays       — Show upcoming birthdays
  add-note        — Create a new note
  search-notes    — Search notes by text
  show-notes      — List all notes
  add-tags        — Add tags to a note
  search-by-tag   — Search notes by tag
  delete-contact  — Delete a contact
  delete-note     — Delete a note
  exit            — Quit the assistant

Enter a command: add-contact
Name: John Doe
Phone (10 digits): 0501234567
Birthday (DD.MM.YYYY, optional):
Contact 'John Doe' created!

Enter a command: add-note
Title: Shopping list
Body: Milk, bread, eggs
Tags (comma-separated, optional): grocery, todo
Note 'Shopping list' created!

Enter a command: birthdays
Days ahead (default 7): 30
Upcoming birthdays:
  John Doe — 15.04.2000 — (050) 123-45-67
```

### Web UI (Streamlit)

Після запуску `PYTHONPATH=. streamlit run app/ui/__init__.py` відкрийте браузер за адресою `http://localhost:8501`.

Доступні сторінки:
- **Contacts** — перегляд, пошук, створення, редагування та видалення контактів
- **Notes** — перегляд, пошук, створення нотаток, управління тегами
- **Calendar** — перегляд найближчих днів народження з налаштуванням періоду

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
