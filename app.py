from datetime import datetime, timedelta
from flask import Flask, abort, redirect, render_template_string, request, session, url_for
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = "saman_nightfair_ultimate_production_key"

ADMIN_USERNAME = "Saman550"
ADMIN_PASSWORD = "0090"

def init_db():
    conn = sqlite3.connect('configs.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            uuid TEXT,
            traffic TEXT,
            days TEXT,
            users TEXT,
            sub_link TEXT,
            raw_config TEXT,
            expiry_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل اختصاصی ساخت کانفیگ - سامان</title>
    <style>
        :root {
            --bg-color: #050b14;
            --card-bg: #0f172a;
            --text-color: #f8fafc;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --accent: #10b981;
            --danger: #ef4444;
            --border: #1e293b;
        }
        body {
            font-family: Tahoma, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 12px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
        }
        h2, h3 { margin-top: 0; color: #38bdf8; font-size: 18px; }
        label { display: block; margin-top: 10px; margin-bottom: 4px; font-size: 12px; color: #94a3b8; }
        input, select {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background-color: #020617;
            color: #fff;
            box-sizing: border-box;
            font-size: 14px;
        }
        .row { display: flex; gap: 8px; }
        .row > div { flex: 1; }
        button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            width: 100%;
            font-size: 14px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 12px;
            transition: 0.2s;
        }
        button:hover { background-color: var(--primary-hover); }
        .btn-unlimited {
            background-color: #1e293b;
            color: #38bdf8;
            font-size: 10px;
            padding: 5px;
            margin-top: 4px;
            border: 1px dashed #38bdf8;
        }
        .config-box {
            background: #020617;
            border-right: 4px solid var(--accent);
            padding: 10px;
            margin-top: 10px;
            border-radius: 6px;
            font-size: 12px;
            word-break: break-all;
            position: relative;
        }
        .config-box.expired { border-right-color: var(--danger); opacity: 0.6; }
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
        }
        .badge-active { background-color: rgba(16, 185, 129, 0.2); color: var(--accent); }
        .badge-expired { background-color: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .delete-btn {
            background-color: var(--danger);
            color: white;
            border: none;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            float: left;
            width: auto;
            margin-top: 0;
        }
        .logout { float: left; color: var(--danger); text-decoration: none; font-size: 12px; }
        code { background: #000; padding: 2px 4px; border-radius: 4px; color: #38bdf8; display: block; margin-top: 4px; max-height: 60px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        {% if session.get('logged_in') %}
            <div class="card">
                <a href="/logout" class="logout">خروج 🚪</a>
                <h2>⚡ پنل ساخت کانفیگ زنده</h2>
                <p style="color: #94a3b8; font-size: 11px;">مدیر سیستم: <b>Saman550</b></p>
                
                <form method="POST" action="/create">
                    <label>نام کانفیگ:</label>
                    <input type="text" name="config_name" placeholder="مثال: Saman-VIP-1" required>

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

                    <button type="submit">🚀 تولید کانفیگ و لینک اشتراک</button>
                </form>
            </div>

            <div class="card">
                <h3>📋 لیست کانفیگ‌های ساخته شده ({{ configs|length }})</h3>
                {% if configs %}
                    {% for c in configs %}
                        <div class="config-box {% if c[9] == 'expired' %}expired{% endif %}">
                            <form action="/delete/{{ c[0] }}" method="POST" style="display:inline;">
                                <button type="submit" class="delete-btn">حذف 🗑</button>
                            </form>
                            <strong>🏷 نام:</strong> {{ c[1] }}<br>
                            <strong>📊 حجم:</strong> {{ c[3] }} GB | <strong>⏳ زمان:</strong> {{ c[4] }} روز<br>
                            <strong>👥 ظرفیت:</strong> {{ c[5] }} کاربر | <strong>📅 انقضا:</strong> {{ c[8] }}<br>
                            <strong>وضعیت:</strong> 
                            {% if c[9] == 'active' %}<span class="badge badge-active">فعال ✅</span>
                            {% else %}<span class="badge badge-expired">منقضی ❌</span>{% endif %}<br>
                            <strong>🔗 لینک اشتراک (Sub Link):</strong>
                            <code>{{ c[6] }}</code>
                            <strong>⚙️ کانفیگ اختصاصی (Vless):</strong>
                            <code>{{ c[7] }}</code>
                        </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #475569; text-align: center; font-size: 13px;">هنوز هیچ کانفیگی ساخته نشده است.</p>
                {% endif %}
            </div>
        {% else %}
            <div class="card" style="margin-top: 30px;">
                <h2>🔒 ورود امن به پنل سامان</h2>
                {% if error %}
                    <p style="color: var(--danger); font-size: 12px;">{{ error }}</p>
                {% endif %}
                <form method="POST" action="/login">
                    <label>نام کاربری:</label>
                    <input type="text" name="username" required>
                    <label>رمز عبور:</label>
                    <input type="password" name="password" required>
                    <button type="submit">ورود به پنل</button>
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
                btn.style.backgroundColor = '#1e293b';
                btn.style.color = '#38bdf8';
                btn.innerText = '∞ نامحدود';
            } else {
                field.value = 'نامحدود';
                field.disabled = false; /* اجازه ارسال فرم حتی وقتی نامحدود است */
                btn.style.backgroundColor = '#10b981';
                btn.style.color = '#fff';
                btn.innerText = '✓ فعال (نامحدود)';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    conn = sqlite3.connect('configs.db', check_same_thread=False)
    cursor = conn.cursor()
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
    traffic = request.form.get("traffic", "نامحدود")
    days = request.form.get("days", "نامحدود")
    users = request.form.get("users_count", "1")
    
    host_url = request.host
    config_uuid = str(uuid.uuid4())
    
    sub_link = f"https://{host_url}/sub/{config_uuid}"
    raw_config = f"vless://{config_uuid}@{host_url}:443?encryption=none&security=tls&type=ws&path=%2F#{name}"
    
    if days and days != 'نامحدود':
        try:
            expiry_date = (datetime.now() + timedelta(days=int(days))).strftime('%Y-%m-%d %H:%M')
        except ValueError:
            expiry_date = "30 روزه"
    else:
        expiry_date = "دائم / نامحدود"
        
    conn = sqlite3.connect('configs.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO configs (name, uuid, traffic, days, users, sub_link, raw_config, expiry_date, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, config_uuid, traffic, days, users, sub_link, raw_config, expiry_date, 'active'))
    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))

@app.route("/sub/<config_uuid>")
def subscription(config_uuid):
    conn = sqlite3.connect('configs.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT raw_config, status FROM configs WHERE uuid = ?", (config_uuid,))
    res = cursor.fetchone()
    conn.close()
    
    if not res:
        abort(404, description="کانفیگ یافت نشد یا منقضی شده است.")
    
    raw_cfg, status = res
    if status == 'expired':
        return "Config Expired / منقضی شده", 403
        
    return raw_cfg

@app.route("/delete/<int:config_id>", methods=["POST"])
def delete_config(config_id):
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    
    conn = sqlite3.connect('configs.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM configs WHERE id = ?", (config_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
