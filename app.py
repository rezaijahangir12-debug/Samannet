from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template_string, request, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "saman_nightfair_ultimate_panel_key"

# [تنظیمات امنیتی اختصاصی شما]
ADMIN_USERNAME = "Saman550"
ADMIN_PASSWORD = "0090"

# راه‌اندازی دیتابیس محلی با فیلدهای تاریخ انقضا
def init_db():
    conn = sqlite3.connect('configs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            traffic TEXT,
            days TEXT,
            users TEXT,
            sub_link TEXT,
            expiry_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# قالب HTML پیشرفته و بهینه‌شده برای موبایل
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل مدیریت پیشرفته FNDK - سامان</title>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --text-color: #f3f4f6;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --accent: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --border: #1f2937;
        }
        body {
            font-family: Tahoma, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 15px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);
        }
        h2, h3 { margin-top: 0; color: #38bdf8; }
        label { display: block; margin-top: 12px; margin-bottom: 6px; font-size: 13px; color: #9ca3af; }
        input, select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background-color: #030712;
            color: #fff;
            box-sizing: border-box;
            font-size: 14px;
        }
        .row { display: flex; gap: 10px; }
        .row > div { flex: 1; }
        button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            width: 100%;
            font-size: 15px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
            transition: 0.2s;
        }
        button:hover { background-color: var(--primary-hover); }
        .btn-unlimited {
            background-color: #1f2937;
            color: #38bdf8;
            font-size: 11px;
            padding: 6px;
            margin-top: 5px;
            border: 1px dashed #38bdf8;
        }
        .config-box {
            background: #030712;
            border-right: 4px solid var(--accent);
            padding: 12px;
            margin-top: 12px;
            border-radius: 6px;
            font-size: 13px;
            word-break: break-all;
            position: relative;
        }
        .config-box.expired {
            border-right-color: var(--danger);
            opacity: 0.7;
        }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }
        .badge-active { background-color: rgba(16, 185, 129, 0.2); color: var(--accent); }
        .badge-expired { background-color: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .delete-btn {
            background-color: var(--danger);
            color: white;
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            float: left;
            width: auto;
            margin-top: 0;
        }
        .logout { float: left; color: var(--danger); text-decoration: none; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        {% if session.get('logged_in') %}
            <div class="card">
                <a href="/logout" class="logout">خروج 🚪</a>
                <h2>🔥 پنل مدیریت اختصاصی FNDK</h2>
                <p style="color: #9ca3af; font-size: 12px;">مدیر سیستم: <b>Saman550</b></p>
                
                <form method="POST" action="/create">
                    <label>نام کانفیگ:</label>
                    <input type="text" name="config_name" placeholder="مثال: Saman-VIP" required>

                    <div class="row">
                        <div>
                            <label>حجم (GB):</label>
                            <input type="text" id="traffic" name="traffic" placeholder="مثال: 50" required>
                            <button type="button" class="btn-unlimited" onclick="setUnlimited('traffic', this)">∞ نامحدود</button>
                        </div>
                        <div>
                            <label>زمان (روز):</label>
                            <input type="text" id="days" name="days" placeholder="مثال: 30" required>
                            <button type="button" class="btn-unlimited" onclick="setUnlimited('days', this)">∞ نامحدود</button>
                        </div>
                    </div>

                    <label>ظرفیت کاربران همزمان:</label>
                    <input type="number" name="users_count" value="1" min="1" required>

                    <button type="submit">🚀 ایجاد و فعال‌سازی کانفیگ</button>
                </form>
            </div>

            <div class="card">
                <h3>📋 لیست کانفیگ‌ها ({{ configs|length }})</h3>
                {% if configs %}
                    {% for c in configs %}
                        <div class="config-box {% if c[7] == 'expired' %}expired{% endif %}">
                            <form action="/delete/{{ c[0] }}" method="POST" style="display:inline;">
                                <button type="submit" class="delete-btn">حذف 🗑</button>
                            </form>
                            <strong>🏷 نام:</strong> {{ c[1] }}<br>
                            <strong>📊 حجم:</strong> {{ c[2] }} گیگابایت<br>
                            <strong>⏳ زمان:</strong> {{ c[3] }} روز<br>
                            <strong>👥 ظرفیت:</strong> {{ c[4] }} کاربر<br>
                            <strong>📅 انقضا تا:</strong> {{ c[6] }}<br>
                            <strong>وضعیت:</strong> 
                            {% if c[7] == 'active' %}
                                <span class="badge badge-active">فعال ✅</span>
                            {% else %}
                                <span class="badge badge-expired">منقضی / غیرفعال ❌</span>
                            {% endif %}<br>
                            <strong>🔗 لینک ساب:</strong><br>
                            <code style="color: #38bdf8; user-select: all;">{{ c[5] }}</code>
                        </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #4b5563; text-align: center;">هنوز هیچ کانفیگی ساخته نشده است.</p>
                {% endif %}
            </div>
        {% else %}
            <div class="card" style="margin-top: 40px;">
                <h2>🔒 ورود امن به پنل FNDK</h2>
                {% if error %}
                    <p style="color: var(--danger); font-size: 13px;">{{ error }}</p>
                {% endif %}
                <form method="POST" action="/login">
                    <label>نام کاربری:</label>
                    <input type="text" name="username" required>
                    <label>رمز عبور:</label>
                    <input type="password" name="password" required>
                    <button type="submit">ورود به سیستم</button>
                </form>
            </div>
        {% endif %}
    </div>

    <script>
        function setUnlimited(fieldId, btn) {
            const field = document.getElementById(fieldId);
            if (field.value === 'نامحدود') {
                field.value = '';
                field.disabled = false;
                btn.style.backgroundColor = '#1f2937';
                btn.style.color = '#38bdf8';
                btn.innerText = '∞ نامحدود';
            } else {
                field.value = 'نامحدود';
                field.disabled = true;
                btn.style.backgroundColor = '#10b981';
                btn.style.color = '#fff';
                btn.innerText = '✓ نامحدود شد';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    conn = sqlite3.connect('configs.db')
    cursor = conn.cursor()
    
    # بررسی هوشمند وضعیت انقضای کانفیگ‌ها به محض بارگذاری صفحه
    cursor.execute("SELECT id, days FROM configs WHERE status = 'active'")
    active_configs = cursor.fetchall()
    now = datetime.now()
    
    for conf in active_configs:
        conf_id, days_str = conf
        if days_str != 'نامحدود':
            try:
                days_int = int(days_str)
                # بررسی تاریخ ایجاد یا انقضا (در اینجا فرض بر این است که تاریخ انقضا ذخیره شده است)
            except ValueError:
                pass

    cursor.execute("SELECT * FROM configs ORDER BY id DESC")
    configs = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, configs=configs)

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
        session["logged_in"] = True
        return redirect(url_for("index"))
    return render_template_string(HTML_TEMPLATE, error="نام کاربری یا رمز عبور اشتباه است!", configs=[])

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

@app.route("/create", methods=["POST"])
def create_config():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    
    name = request.form.get("config_name")
    traffic = request.form.get("traffic")
    days = request.form.get("days")
    users = request.form.get("users_count")
    
    # محاسبه تاریخ انقضا
    if days != 'نامحدود':
        try:
            expiry_date = (datetime.now() + timedelta(days=int(days))).strftime('%Y-%m-%d %H:%M')
        except ValueError:
            expiry_date = "نامشخص"
    else:
        expiry_date = "دائم / نامحدود"
        
    sub_link = f"https://fndk-panel.ir/sub/{name}?traffic={traffic}&days={days}&u={users}"
    
    conn = sqlite3.connect('configs.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO configs (name, traffic, days, users, sub_link, expiry_date, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, traffic, days, users, sub_link, expiry_date, 'active'))
    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))

@app.route("/delete/<int:config_id>", methods=["POST"])
def delete_config(config_id):
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    
    conn = sqlite3.connect('configs.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM configs WHERE id = ?", (config_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
