# Astro Gaming Store — Inventory Management System

## Tech Stack

- **Backend:** Python · Flask
- **Database:** SQLite (auto-created on first run)
- **Frontend:** HTML · CSS · Bootstrap 5 · Chart.js
- **Version Control:** GitHub

---

## Quick Start

### 1. Clone / Download

```bash
git clone <repo-url>
cd astro_gaming
```

### 2. Create a virtual environment

```bash
python -m venv venv
python3 -m venv venv (macos)


# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
python3 app.py (macos)

```
If you want to run locally , In app.py relace these lines at the end:

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)

Open your browser at: **http://localhost:8000**

---

## Default Login Credentials

| Role    | Username | Password |
| ------- | -------- | -------- |
| Admin   | admin_user |  SG$RmZsf8
| Cashier | cashier_user| fy$NuaToG 

- **Admin** — full access (add, edit, delete products)
- **Cashier** — read-only access (view inventory, alerts, dashboard)

---

## Project Structure

```
astro_gaming/
├── app.py              ← Flask routes and application logic
├── database.py         ← SQLite setup and seed data
├── requirements.txt    ← Python dependencies
├── instance/
│   └── astro.db        ← SQLite database (auto-created)
├── static/
│   ├── css/style.css   ← Custom styles (light + dark mode)
│   └── js/main.js      ← Theme toggle and JS helpers
└── templates/
    ├── base.html        ← Master layout (sidebar, topbar)
    ├── login.html       ← Login screen
    ├── dashboard.html   ← Dashboard
    ├── inventory.html   ← Inventory list
    ├── add_edit_item.html ← Add / Edit form
    ├── alerts.html      ← Low-stock alerts
    └── reports.html     ← Reports & analytics
```

---

## Features

| Screen    | Features                                                       |
| --------- | -------------------------------------------------------------- |
| Login     | Role-based auth (Admin / Cashier), dark/light mode             |
| Dashboard | Stat cards, recent sales, stock alert panel                    |
| Inventory | Search, filter by platform/genre/status, pagination, CRUD      |
| Add/Edit  | Form validation, reorder threshold warning, danger zone delete |
| Alerts    | Filter tabs (All/Out/Low), CSV export, Reorder buttons         |
| Reports   | Colorful bar chart, top sellers table, CSV export              |
