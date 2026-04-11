from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from database import get_db, init_db
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "astro-gaming-secret-2026"


# ── BOOTSTRAP ─────────────────────────────────────────────────
@app.before_request
def ensure_db():
    pass  # db initialised once at startup


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        db.close()
        if user:
            session["user_id"]   = user["id"]
            session["username"]  = user["username"]
            session["role"]      = user["role"]
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    total_products = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    # Count products at or below their threshold
    low_stock_count = db.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= reorder_threshold"
    ).fetchone()[0]

    # Today's sales (count of transactions)
    today = datetime.now().strftime("%Y-%m-%d")
    todays_sales = db.execute(
        "SELECT COUNT(*) FROM sales WHERE sale_time LIKE ?", (today + "%",)
    ).fetchone()[0]

    # Revenue = all sales total (for demo, last 7 days)
    revenue = db.execute(
        "SELECT COALESCE(SUM(sale_price * quantity), 0) FROM sales"
    ).fetchone()[0]

    # Recent 5 sales
    recent_sales = db.execute("""
        SELECT s.sale_price, s.sale_time, s.quantity,
               p.title, p.platform
        FROM sales s
        JOIN products p ON p.id = s.product_id
        ORDER BY s.sale_time DESC
        LIMIT 5
    """).fetchall()

    # Stock alerts (out of stock or low, max 6 shown)
    alerts = db.execute("""
        SELECT title, platform, quantity, reorder_threshold,
               CASE WHEN quantity = 0 THEN 'Out of Stock' ELSE 'Low Stock' END AS status
        FROM products
        WHERE quantity <= reorder_threshold
        ORDER BY quantity ASC
        LIMIT 6
    """).fetchall()

    db.close()
    return render_template("dashboard.html",
        total_products=total_products,
        low_stock_count=low_stock_count,
        todays_sales=todays_sales,
        revenue=revenue,
        recent_sales=recent_sales,
        alerts=alerts
    )


# ══════════════════════════════════════════════════════════════
# INVENTORY
# ══════════════════════════════════════════════════════════════
@app.route("/inventory")
@login_required
def inventory():
    db = get_db()
    search   = request.args.get("search", "").strip()
    platform = request.args.get("platform", "")
    genre    = request.args.get("genre", "")
    status   = request.args.get("status", "")
    page     = int(request.args.get("page", 1))
    per_page = 10

    query  = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR sku LIKE ? OR platform LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    if genre:
        query += " AND genre = ?"
        params.append(genre)
    if status == "In Stock":
        query += " AND quantity > reorder_threshold"
    elif status == "Low Stock":
        query += " AND quantity > 0 AND quantity <= reorder_threshold"
    elif status == "Out of Stock":
        query += " AND quantity = 0"

    total = db.execute(f"SELECT COUNT(*) FROM ({query})", params).fetchone()[0]
    query += f" ORDER BY sku LIMIT {per_page} OFFSET {(page-1)*per_page}"
    products = db.execute(query, params).fetchall()

    platforms = [r[0] for r in db.execute("SELECT DISTINCT platform FROM products ORDER BY platform").fetchall()]
    genres    = [r[0] for r in db.execute("SELECT DISTINCT genre FROM products ORDER BY genre").fetchall()]
    db.close()

    total_pages = (total + per_page - 1) // per_page
    return render_template("inventory.html",
        products=products, total=total,
        page=page, total_pages=total_pages,
        per_page=per_page,
        search=search, platform=platform,
        genre=genre, status=status,
        platforms=platforms, genres=genres
    )


@app.route("/inventory/add", methods=["GET", "POST"])
@login_required
def add_item():
    if session.get("role") != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("inventory"))
    if request.method == "POST":
        db = get_db()
        try:
            db.execute("""
                INSERT INTO products (sku, title, platform, genre, category,
                                      quantity, price, reorder_threshold)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form["sku"].strip().upper(),
                request.form["title"].strip(),
                request.form["platform"],
                request.form["genre"],
                request.form.get("category", "Full Game"),
                int(request.form.get("quantity", 0)),
                float(request.form.get("price", 0)),
                int(request.form.get("reorder_threshold", 5)),
            ))
            db.commit()
            flash("Product added successfully.", "success")
            return redirect(url_for("inventory"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
    return render_template("add_edit_item.html", item=None, mode="add")


@app.route("/inventory/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    if session.get("role") != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("inventory"))
    db = get_db()
    item = db.execute("SELECT * FROM products WHERE id = ?", (item_id,)).fetchone()
    if not item:
        db.close()
        flash("Product not found.", "danger")
        return redirect(url_for("inventory"))
    if request.method == "POST":
        try:
            db.execute("""
                UPDATE products SET
                    sku=?, title=?, platform=?, genre=?, category=?,
                    quantity=?, price=?, reorder_threshold=?
                WHERE id=?
            """, (
                request.form["sku"].strip().upper(),
                request.form["title"].strip(),
                request.form["platform"],
                request.form["genre"],
                request.form.get("category", "Full Game"),
                int(request.form.get("quantity", 0)),
                float(request.form.get("price", 0)),
                int(request.form.get("reorder_threshold", 5)),
                item_id
            ))
            db.commit()
            flash("Product updated successfully.", "success")
            return redirect(url_for("inventory"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            db.close()
        return redirect(url_for("inventory"))
    db.close()
    return render_template("add_edit_item.html", item=item, mode="edit")


@app.route("/inventory/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    if session.get("role") != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("inventory"))
    db = get_db()
    # Delete related sales records first to avoid FK constraint error
    db.execute("DELETE FROM sales WHERE product_id = ?", (item_id,))
    db.execute("DELETE FROM products WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    flash("Product deleted.", "warning")
    return redirect(url_for("inventory"))


# ══════════════════════════════════════════════════════════════
# ALERTS
# ══════════════════════════════════════════════════════════════
@app.route("/alerts")
@login_required
def alerts():
    db  = get_db()
    tab = request.args.get("tab", "all")

    base  = "SELECT * FROM products WHERE quantity <= reorder_threshold"
    if tab == "out":
        query = base + " AND quantity = 0 ORDER BY title"
    elif tab == "low":
        query = base + " AND quantity > 0 ORDER BY quantity ASC"
    else:
        query = base + " ORDER BY quantity ASC"

    items      = db.execute(query).fetchall()
    all_count  = db.execute(base).fetchone()
    out_count  = db.execute(base + " AND quantity = 0").fetchone()
    low_count  = db.execute(base + " AND quantity > 0").fetchone()

    all_count  = db.execute("SELECT COUNT(*) FROM products WHERE quantity <= reorder_threshold").fetchone()[0]
    out_count  = db.execute("SELECT COUNT(*) FROM products WHERE quantity = 0").fetchone()[0]
    low_count  = db.execute("SELECT COUNT(*) FROM products WHERE quantity > 0 AND quantity <= reorder_threshold").fetchone()[0]

    db.close()
    return render_template("alerts.html",
        items=items, tab=tab,
        all_count=all_count, out_count=out_count, low_count=low_count
    )


# ══════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════
@app.route("/reports")
@login_required
def reports():
    db = get_db()

    # Daily revenue for the last 7 days (Mar 1-7)
    daily = db.execute("""
        SELECT DATE(sale_time) as day,
               COALESCE(SUM(sale_price * quantity), 0) as total
        FROM sales
        GROUP BY DATE(sale_time)
        ORDER BY day
        LIMIT 7
    """).fetchall()

    # Top sellers by units sold
    top_sellers = db.execute("""
        SELECT p.title, p.platform,
               SUM(s.quantity) as units,
               SUM(s.sale_price * s.quantity) as revenue
        FROM sales s
        JOIN products p ON p.id = s.product_id
        GROUP BY p.id
        ORDER BY units DESC
        LIMIT 5
    """).fetchall()

    total_revenue = db.execute("SELECT COALESCE(SUM(sale_price * quantity),0) FROM sales").fetchone()[0]
    db.close()

    days   = [r["day"]   for r in daily]
    totals = [round(r["total"], 2) for r in daily]
    avg    = round(total_revenue / max(len(daily), 1), 2)

    return render_template("reports.html",
        days=days, totals=totals,
        top_sellers=top_sellers,
        total_revenue=total_revenue,
        avg_per_day=avg
    )


# ══════════════════════════════════════════════════════════════
# API — export CSV (simple inline)
# ══════════════════════════════════════════════════════════════
@app.route("/api/export/alerts")
@login_required
def export_alerts_csv():
    from flask import Response
    db = get_db()
    rows = db.execute(
        "SELECT sku, title, platform, quantity, reorder_threshold FROM products WHERE quantity <= reorder_threshold ORDER BY quantity"
    ).fetchall()
    db.close()
    lines = ["SKU,Title,Platform,Qty,Threshold"]
    for r in rows:
        lines.append(f"{r['sku']},{r['title']},{r['platform']},{r['quantity']},{r['reorder_threshold']}")
    return Response("\n".join(lines), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=low_stock_alerts.csv"})


@app.route("/api/export/reports")
@login_required
def export_reports_csv():
    from flask import Response
    db = get_db()
    rows = db.execute("""
        SELECT p.title, p.platform, SUM(s.quantity) as units,
               SUM(s.sale_price*s.quantity) as revenue
        FROM sales s JOIN products p ON p.id=s.product_id
        GROUP BY p.id ORDER BY units DESC
    """).fetchall()
    db.close()
    lines = ["Rank,Title,Platform,Units,Revenue"]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i},{r['title']},{r['platform']},{r['units']},{r['revenue']:.2f}")
    return Response("\n".join(lines), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=top_sellers.csv"})


# ══════════════════════════════════════════════════════════════
import os

if __name__ == "__main__":
    init_db()
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )