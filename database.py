import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "astro.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    # ── USERS ──────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT NOT NULL DEFAULT 'cashier'
        )
    """)

    # ── PRODUCTS ───────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            sku               TEXT UNIQUE NOT NULL,
            title             TEXT NOT NULL,
            platform          TEXT NOT NULL,
            genre             TEXT NOT NULL,
            category          TEXT NOT NULL DEFAULT 'Full Game',
            quantity          INTEGER NOT NULL DEFAULT 0,
            price             REAL NOT NULL DEFAULT 0.0,
            reorder_threshold INTEGER NOT NULL DEFAULT 5
        )
    """)

    # ── SALES ──────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL,
            sale_price  REAL NOT NULL,
            quantity    INTEGER NOT NULL DEFAULT 1,
            sale_time   TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()

    # ── SEED DATA (only if tables are empty) ───────────────────
    if not c.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        # Passwords stored in plain text for simplicity 
        c.executemany(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [
                ("admin_user",   "SG$RmZsf8", "admin"),
                ("cashier_user", "fy$NuaToG", "cashier"),
            ]
        )

    if not c.execute("SELECT 1 FROM products LIMIT 1").fetchone():
        products = [
            ("GW-001", "God of War Ragnarok",   "PS5",    "Action",    "Full Game",  14, 69.99, 5),
            ("ZL-002", "Zelda: TotK",           "Switch", "Adventure", "Full Game",   3, 59.99, 5),
            ("HL-003", "Halo Infinite",         "Xbox",   "FPS",       "Full Game",   8, 49.99, 5),
            ("EL-004", "Elden Ring",            "PC",     "RPG",       "Full Game",   0, 39.99, 5),
            ("MC-005", "Minecraft",             "Switch", "Sandbox",   "Full Game",  22, 60.00, 5),
            ("HW-006", "Hogwarts Legacy",       "PS5",    "RPG",       "Full Game",   4, 59.99, 6),
            ("GT-007", "Grand Theft Auto V",    "PC",     "Action",    "Full Game",  11, 60.00, 5),
            ("FI-008", "FIFA 25",               "PS5",    "Sports",    "Full Game",   0, 59.99, 8),
            ("FZ-009", "Forza Horizon 5",       "Xbox",   "Racing",    "Full Game",   2, 49.99, 5),
            ("SF-010", "Starfield",             "PC",     "RPG",       "Full Game",   1, 49.99, 4),
            ("SP-011", "Spider-Man 2",          "PS5",    "Action",    "Full Game",   7, 69.99, 5),
            ("MK-012", "Mario Kart 8 Deluxe",  "Switch", "Racing",    "Full Game",  15, 49.99, 5),
        ]
        c.executemany(
            """INSERT INTO products
               (sku, title, platform, genre, category, quantity, price, reorder_threshold)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            products
        )

    if not c.execute("SELECT 1 FROM sales LIMIT 1").fetchone():
        # Seed sales for the last 7 days
        conn.commit()
        products_rows = c.execute("SELECT id, price FROM products").fetchall()
        base = datetime(2026, 3, 1, 9, 0, 0)
        # Daily revenue targets: Mon420 Tue315 Wed525 Thu350 Fri630 Sat820 Sun490
        targets = [420, 315, 525, 350, 630, 820, 490]
        sales_rows = []
        for day, target in enumerate(targets):
            accumulated = 0
            attempts = 0
            while accumulated < target and attempts < 50:
                p = random.choice(products_rows)
                price = p["price"]
                if accumulated + price > target + 80:
                    attempts += 1
                    continue
                sale_time = base + timedelta(days=day, hours=random.randint(0, 8),
                                             minutes=random.randint(0, 59))
                sales_rows.append((p["id"], price, 1, sale_time.strftime("%Y-%m-%d %H:%M:%S")))
                accumulated += price
                attempts += 1
        c.executemany(
            "INSERT INTO sales (product_id, sale_price, quantity, sale_time) VALUES (?, ?, ?, ?)",
            sales_rows
        )

    conn.commit()
    conn.close()
