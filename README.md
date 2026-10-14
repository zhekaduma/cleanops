# CleanOps

Автоматизированная система управления клининговой службой.

## Стек

- Python 3.9+
- PyQt5
- SQLAlchemy 2.0 + SQLite
- bcrypt, openpyxl, reportlab
- pytest, PyInstaller
- GitHub Actions

## Установка

```bash
git clone https://github.com/zhekaduma/cleanops.git
cd cleanops
python3 -m venv venv39
source venv39/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python main.py
```

## Логины для входа

| Роль | Логин | Пароль |
|------|-------|--------|
| Администратор | admin | admin123 |
| Менеджер | manager | manager123 |
| Бригадир | brigadier | brig123 |
| Клинер | cleaner | clean123 |
| Бухгалтер | accountant | acc123 |

## Сборка .exe

```bash
pyinstaller cleanops.spec
```

## Тесты

```bash
pytest tests/ -v
```

## Автор

Кудусов Евгений Александрович, группа ИСП-34.
