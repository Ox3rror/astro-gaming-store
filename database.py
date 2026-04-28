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

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'cashier'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        platform TEXT NOT NULL,
        genre TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'Full Game',
        quantity INTEGER NOT NULL DEFAULT 0,
        price REAL NOT NULL DEFAULT 0.0,
        reorder_threshold INTEGER NOT NULL DEFAULT 5
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        sale_price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        sale_time TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )""")
    conn.commit()

    # Seed users with bcrypt-hashed passwords
    # admin_user  -> SG$RmZsf8
    # cashier_user -> fy$NuaToG
    if not c.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        c.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [
            ("admin_user",
             "$2b$12$G1fcscr3mG3VhoHbVhJpKOrJS.Yu88lcMCd3OO3GzxJA8twhoB0qS",
             "admin"),
            ("cashier_user",
             "$2b$12$bmh5nGsAo2ONtzc/prkONeaL2ahQEf/liuPEwLmjY22wsvlBi/6VC",
             "cashier"),
        ])

    if not c.execute("SELECT 1 FROM products LIMIT 1").fetchone():
        products = [
            ("GW-001","God of War Ragnarok",              "PS5",   "Action",    "Full Game", 14,69.99,5),
            ("ZL-002","Zelda: Tears of the Kingdom",      "Switch","Adventure", "Full Game",  3,59.99,5),
            ("HL-003","Halo Infinite",                    "Xbox",  "FPS",       "Full Game",  8,49.99,5),
            ("EL-004","Elden Ring",                       "PC",    "RPG",       "Full Game",  0,59.99,5),
            ("MC-005","Minecraft",                        "Switch","Sandbox",   "Full Game", 22,60.00,5),
            ("HW-006","Hogwarts Legacy",                  "PS5",   "RPG",       "Full Game",  0,59.99,6),
            ("GT-007","Grand Theft Auto V",               "PC",    "Action",    "Full Game", 11,79.99,5),
            ("FI-008","FIFA 26",                          "PS5",   "Sports",    "Full Game",  0,69.99,8),
            ("FZ-009","Forza Horizon 5",                  "Xbox",  "Racing",    "Full Game",  2,49.99,5),
            ("SF-010","Starfield",                        "PC",    "RPG",       "Full Game",  1,49.99,4),
            ("SP-011","Spider-Man 2",                     "PS5",   "Action",    "Full Game",  7,69.99,5),
            ("MK-012","Mario Kart 8 Deluxe",              "Switch","Racing",    "Full Game", 15,49.99,5),
            ("AC-013","Assassin's Creed Mirage",          "PS5",   "Action",    "Full Game",  6,59.99,5),
            ("DM-014","Diablo IV",                        "PC",    "RPG",       "Full Game",  9,69.99,5),
            ("RD-015","Red Dead Redemption 2",            "PC",    "Action",    "Full Game", 12,39.99,5),
            ("CB-016","Cyberpunk 2077",                   "PC",    "RPG",       "Full Game",  8,49.99,5),
            ("MG-017","Mortal Kombat 1",                  "PS5",   "Fighting",  "Full Game",  4,69.99,5),
            ("AR-018","ARC Raiders",                      "PC",    "FPS",       "Full Game",  4,70.00,5),
            ("OV-019","Overwatch 2",                      "PC",    "FPS",       "Full Game", 18,29.99,5),
            ("BG-020","Baldur's Gate 3",                  "PC",    "RPG",       "Full Game",  5,59.99,4),
            ("FF-021","Final Fantasy XVI",                "PS5",   "RPG",       "Full Game",  6,59.99,5),
            ("RE-022","Resident Evil 4 Remake",           "PS5",   "Horror",    "Full Game", 10,49.99,5),
            ("SM-023","Splatoon 3",                       "Switch","Shooter",   "Full Game",  9,59.99,5),
            ("PO-024","Pokemon Scarlet",                  "Switch","RPG",       "Full Game", 13,59.99,5),
            ("FO-025","Fortnite V-Bucks 2800",            "PC",    "FPS",       "DLC",       35,19.99,10),
            ("DB-026","Dragon's Dogma 2",                 "PS5",   "RPG",       "Full Game",  7,69.99,5),
            ("SN-027","Sonic Frontiers",                  "Switch","Platformer","Full Game",  5,39.99,5),
            ("HM-028","Hades II",                         "PC",    "Roguelike", "Full Game", 11,29.99,5),
            ("TK-029","Tekken 8",                         "PS5",   "Fighting",  "Full Game",  8,69.99,5),
            ("ST-030","Street Fighter 6",                 "PS5",   "Fighting",  "Full Game",  3,59.99,5),
            ("DL-031","Dead Cells: DLC Bundle",           "PC",    "Roguelike", "DLC",       20,14.99,8),
            ("WL-032","Lies of P",                        "Xbox",  "Action",    "Full Game",  6,59.99,5),
            ("AN-033","Animal Crossing: New Horizons",    "Switch","Simulation","Full Game", 16,59.99,5),
            ("CE-034","Celeste",                          "Switch","Platformer","Indie",     12,19.99,5),
            ("HO-035","Hollow Knight",                    "PC",    "Platformer","Indie",      9,14.99,5),
            ("GS-036","Ghost of Tsushima Directors Cut",  "PS5",   "Action",    "Full Game",  5,59.99,5),
            ("XB-037","Xbox Game Pass 3-Month Card",      "Xbox",  "Sandbox",   "Subscription",30,29.99,10),
            ("CP-038","Cuphead: The Delicious Last Course","Switch","Platformer","DLC",      14, 7.99,8),
            ("AP-039","Apex Legends: Starter Pack",       "PC",    "FPS",       "DLC",       25, 4.99,10),
            ("WZ-040","Call of Duty: Warzone Bundle",     "Xbox",  "FPS",       "DLC",       18,19.99,8),
        ]
        c.executemany("""INSERT INTO products
            (sku,title,platform,genre,category,quantity,price,reorder_threshold)
            VALUES (?,?,?,?,?,?,?,?)""", products)

    if not c.execute("SELECT 1 FROM sales LIMIT 1").fetchone():
        conn.commit()
        product_rows = c.execute("SELECT id, price FROM products").fetchall()

        def gen_days(base_dt, daily_targets):
            rows = []
            for day_idx, target in enumerate(daily_targets):
                acc, attempts = 0, 0
                while acc < target and attempts < 150:
                    p = random.choice(product_rows)
                    price = p["price"]
                    if acc + price > target + 100:
                        attempts += 1; continue
                    t = base_dt + timedelta(
                        days=day_idx,
                        hours=random.randint(0, 10),
                        minutes=random.randint(0, 59)
                    )
                    rows.append((p["id"], price, 1, t.strftime("%Y-%m-%d %H:%M:%S")))
                    acc += price; attempts += 1
            return rows

        # March 2026
        march_targets = [
            290,380,440,510,620,700,580,
            310,420,390,480,600,680,550,
            270,360,430,500,590,660,520,
            300,410,470,560,650,730,610,
            340,450,495,
        ]
        # April 2026
        april_targets = [
            320,415,280,355,495,725,595,
            310,385,265,425,515,815,655,
            295,455,305,395,485,765,625,
            345,425,315,365,535,885,705,
            375,445,
        ]

        all_sales = gen_days(datetime(2026,3,1,9,0,0), march_targets)
        all_sales += gen_days(datetime(2026,4,1,9,0,0), april_targets)

        c.executemany(
            "INSERT INTO sales (product_id,sale_price,quantity,sale_time) VALUES (?,?,?,?)",
            all_sales
        )

    conn.commit()
    conn.close()
