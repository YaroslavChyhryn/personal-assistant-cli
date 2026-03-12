# Backlog

Кожен розробник працює паралельно в окремій `feature/` гілці.

---

### Dev 1 — Contacts + Birthdays

Гілка: `feature/contacts` | Тікет: [ticket-dev1-contacts.md](ticket-dev1-contacts.md)

- [ ] SQLModel-моделі в `domain/models.py`: Contact, Phone (з relationships)
- [ ] `contacts_repository.py`: наслідує BaseRepository, + search, get_upcoming_birthdays
- [ ] Unit-тести

---

### Dev 2 — Notes + Tags

Гілка: `feature/notes` | Тікет: [ticket-dev2-notes.md](ticket-dev2-notes.md)

- [ ] SQLModel-моделі в `domain/models.py`: Note, Tag, NoteTagLink (many-to-many)
- [ ] `notes_repository.py`: наслідує BaseRepository, + search, search_by_tag, add_with_tags
- [ ] Unit-тести

---

### Dev 3 — CLI

Гілка: `feature/cli` | Тікет: [ticket-dev3-cli.md](ticket-dev3-cli.md) | Залежить від Dev 1 і Dev 2

- [ ] Декоратор input_error
- [ ] Команди контактів: add, change, phone, all
- [ ] Команди birthday: add-birthday, show-birthday, birthdays
- [ ] Команди нотаток: add-note, find-note, find-tag

---

### Dev 4 (Tech Lead) — Architecture + Services

- [x] Структура проєкту, pyproject.toml, requirements.txt
- [x] config.py, db.py, bootstrap.py
- [x] BaseRepository з CRUD
- [x] .pre-commit-config.yaml, README, BACKLOG
- [x] Тікети для Dev 1, Dev 2, Dev 3
- [ ] `contacts_service.py`, `notes_service.py`, `calendar_service.py`
- [ ] Code review + інтеграція гілок
- [ ] Integration-тести

---

## Порядок мерджу

1. `feature/contacts` → `develop`
2. `feature/notes` → `develop`
3. `feature/cli` → `develop` (залежить від 1 і 2)
4. `develop` → `main`

## Важливо

- **models.py** — спільний файл, Dev 1 і Dev 2 домовляються про поля заздалегідь
- Pre-commit hooks мають проходити перед кожним комітом
