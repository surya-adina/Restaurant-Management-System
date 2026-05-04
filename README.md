# Restaurant Management System

Python Tkinter UI + MySQL database.

## Setup

1. Install MySQL Server and start it.
2. Create the database:
   ```bash
   mysql -u root -p < schema.sql
   ```
3. Install Python dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Edit `DB_CONFIG` in `app.py` if your MySQL username/password is different.
5. Run:
   ```bash
   python app.py
   ```

## Adapt it

- Add/remove fields by changing `schema.sql`, then update the matching form in `app.py`.
- Add new modules by creating a new dashboard button and a new window method.
- Keep table names consistent between MySQL and Python.
