# CleanOps

Автоматизированная система управления клининговой службой.

## Стек

- Python 3.13
- PyQt6 (GUI)
- SQLAlchemy + SQLite (БД)
- pytest (тесты)
- black + flake8 (качество кода)

## Установка

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
python main.py

### 5.6. `main.py`

```bash
cat > main.py << 'EOF'
"""Точка входа приложения CleanOps."""


def main() -> None:
    """Запуск приложения."""
    print("CleanOps starting...")


if __name__ == "__main__":
    main()
