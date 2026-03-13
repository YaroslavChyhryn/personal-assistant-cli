# Backlog

Кожен розробник працює паралельно в окремій `feature/` гілці.

---

### Dev 1 — Contacts + Birthdays ✅

Гілка: `feature/contacts` | Тікет: [ticket-dev1-contacts.md](ticket-dev1-contacts.md)

- [x] SQLModel-моделі в `domain/models.py`: Contact, Phone (з relationships)
- [x] `contacts_repository.py`: наслідує BaseRepository, + search, get_upcoming_birthdays
- [x] Unit-тести

---

### Dev 2 — Notes + Tags ✅

Гілка: `feature/notes` | Тікет: [ticket-dev2-notes.md](ticket-dev2-notes.md)

- [x] SQLModel-моделі в `domain/models.py`: Note, Tag, NoteTagLink (many-to-many)
- [x] `notes_repository.py`: наслідує BaseRepository, + search, search_by_tag, add_with_tags
- [x] Unit-тести

---

### Dev 3 — CLI ✅

Гілка: `feature/cli` | Тікет: [ticket-dev3-cli.md](ticket-dev3-cli.md) | Залежить від Dev 1 і Dev 2

- [x] Декоратор input_error
- [x] Команди контактів: add, change, phone, all
- [x] Команди birthday: add-birthday, show-birthday, birthdays
- [x] Команди нотаток: add-note, find-note, find-tag

---

### Dev 4 (Tech Lead) — Architecture + Services ✅

- [x] Структура проєкту, pyproject.toml, requirements.txt
- [x] config.py, db.py, bootstrap.py
- [x] BaseRepository з CRUD
- [x] .pre-commit-config.yaml, README, BACKLOG
- [x] Тікети для Dev 1, Dev 2, Dev 3
- [x] `contacts_service.py`, `notes_service.py`, `calendar_service.py`
- [x] Code review + інтеграція гілок
- [x] Integration-тести

---

### Optional — Web UI (Streamlit) 🔧

Гілка: `feature/ui`

- [x] Streamlit-додаток (`app/ui/`)
- [x] Сторінка контактів: список, пошук, створення, редагування/видалення телефонів, встановлення дня народження
- [x] Сторінка нотаток: список, пошук за текстом і тегами, створення, додавання/видалення тегів
- [x] Сторінка календаря: слайдер для періоду, таблиця з найближчими днями народження
- [x] Фінальний code review та мердж у `main`

---

## Порядок мерджу

1. `feature/contacts` → `main` ✅
2. `feature/notes` → `main` ✅
3. `feature/cli` → `main` ✅
4. `feature/ui` → `main` ✅

## Важливо

- **models.py** — спільний файл, Dev 1 і Dev 2 домовляються про поля заздалегідь
- Pre-commit hooks мають проходити перед кожним комітом
