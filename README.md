# Personal Assistant CLI

CLI-помічник для управління контактами, нотатками та днями народження. Фінальний проєкт з Python Programming.

## Архітектура

Проєкт побудований на принципі **Layered Architecture** з чітким розділенням шарів:

- **Domain** — SQLModel-моделі (єдиний клас = таблиця + схема + об'єкт), валідація, репозиторії (бізнес-логіка запитів)
- **Application** — сервіси (use cases): створення контакту, пошук нотатки, upcoming birthdays
- **Interfaces** — CLI (input/print цикл як у домашці), у майбутньому — Streamlit / API

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

## Технології

| Технологія | Призначення |
|---|---|
| Python 3.12+ | Мова |
| SQLModel | ORM (поверх SQLAlchemy + Pydantic) |
| SQLite | Локальне сховище даних |
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
├── src/
│   └── app/
│       ├── main.py
│       ├── cli.py
│       ├── config.py
│       ├── bootstrap.py
│       ├── db.py
│       ├── domain/
│       │   ├── models.py
│       │   └── repository.py
│       └── application/
│           ├── contacts_service.py
│           ├── notes_service.py
│           └── calendar_service.py
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
```bash
python -m app.main
```

### Розробка

Запустити лінтер:
```bash
ruff check src/
ruff format src/
```


Запустити pre-commit на всіх файлах:
```bash
pre-commit run --all-files
```

## Git Workflow

- `main` — стабільна гілка
- `feature/<name>` — гілки для окремих фіч
