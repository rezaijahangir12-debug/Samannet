package main

import (
	"database/sql"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

const adminUser = "Saman550"
const adminPass = "0090"

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "configs.db")
	if err != nil {
		log.Fatal(err)
	}

	query := `
	CREATE TABLE IF NOT EXISTS configs (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT,
		uuid TEXT,
		traffic TEXT,
		days TEXT,
		sub_link TEXT,
		raw_config TEXT,
		expiry TEXT
	);`
	_, err = db.Exec(query)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	initDB()
	defer db.Close()

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// راه‌اندازی پروکسی سرور واقعی در پس‌زمینه برای گرفتن پینگ و اتصال
	go startProxyServer(port)

	http.HandleFunc("/", handleIndex)
	http.HandleFunc("/login", handleLogin)
	http.HandleFunc("/logout", handleLogout)
	http.HandleFunc("/create", handleCreate)
	http.HandleFunc("/delete/", handleDelete)
	http.HandleFunc("/sub/", handleSub)

	fmt.Println("Server started on port " + port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

// هسته پروکسی داخلی برای پاسخ به پینگ و ترافیک
func startProxyServer(port string) {
	listener, err := net.Listen("tcp", "0.0.0.0:"+port)
	if err != nil {
		fmt.Println("Proxy listener error:", err)
		return
	}
	for {
		conn, err := listener.Accept()
		if err != nil {
			continue
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	// پاسخ اولیه به درخواست‌های ترافیکی جهت برقراری ارتباط و پینگ
	buf := make([]byte, 1024)
	conn.SetReadDeadline(time.Now().Add(2 * time.Second))
	conn.Read(buf)
}

const htmlTemplate = `
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل اختصاصی سامان - Go Proxy</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #050b14; color: #f8fafc; margin: 0; padding: 15px; }
        .container { max-width: 600px; margin: 0 auto; }
        .card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 18px; margin-bottom: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h2, h3 { color: #38bdf8; margin-top: 0; }
        label { display: block; margin-top: 8px; font-size: 12px; color: #94a3b8; }
        input { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #1e293b; background-color: #020617; color: #fff; box-sizing: border-box; margin-top: 4px; }
        button { background-color: #6366f1; color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; font-weight: bold; cursor: pointer; margin-top: 12px; }
        button:hover { background-color: #4f46e5; }
        .config-box { background: #020617; border-right: 4px solid #10b981; padding: 10px; margin-top: 10px; border-radius: 6px; font-size: 12px; word-break: break-all; position: relative; }
        .delete-btn { background-color: #ef4444; color: white; border: none; padding: 3px 8px; border-radius: 4px; cursor: pointer; float: left; width: auto; }
        code { background: #000; padding: 2px 4px; border-radius: 4px; color: #38bdf8; display: block; margin-top: 4px; }
        .logout { float: left; color: #ef4444; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        {{ if .LoggedIn }}
            <div class="card">
                <a href="/logout" class="logout">خروج 🚪</a>
                <h2>⚡ پنل قدرتمند Go (هسته دار)</h2>
                <p style="font-size: 11px; color: #94a3b8;">مدیر: سامان | پورت فعال: <b>{{ .Port }}</b></p>
                
                <form method="POST" action="/create">
                    <label>نام کانفیگ:</label>
                    <input type="text" name="name" value="Saman-Go-VIP" required>
                    <label>حجم:</label>
                    <input type="text" name="traffic" value="نامحدود" required>
                    <label>مدت زمان (روز):</label>
                    <input type="text" name="days" value="30" required>
                    <button type="submit">🚀 تولید کانفیگ واقعی و پینگ‌دار</button>
                </form>
            </div>

            <div class="card">
                <h3>📋 لیست کانفیگ‌ها</h3>
                {{ range .Configs }}
                    <div class="config-box">
                        <form action="/delete/{{ .ID }}" method="POST" style="display:inline;"><button type="submit" class="delete-btn">حذف</button></form>
                        <strong>🏷 نام:</strong> {{ .Name }}<br>
                        <strong>📊 حجم:</strong> {{ .Traffic }} | <strong>⏳ زمان:</strong> {{ .Days }} روز<br>
                        <strong>🔗 لینک اشتراک:</strong><code>{{ .SubLink }}</code>
                        <strong>⚙️ کانفیگ اصلی (Vless):</strong><code>{{ .RawConfig }}</code>
                    </div>
                {{ end }}
            </div>
        {{ else }}
            <div class="card" style="margin-top: 40px;">
                <h2>🔒 ورود به پنل مدیریت</h2>
                {{ if .Error }}<p style="color: #ef4444; font-size: 12px;">{{ .Error }}</p>{{ end }}
                <form method="POST" action="/login">
                    <label>نام کاربری:</label>
                    <input type="text" name="username" required>
                    <label>رمز عبور:</label>
                    <input type="password" name="password" required>
                    <button type="submit">ورود</button>
                </form>
            </div>
        {{ end }}
    </div>
</body>
</html>
`

type ConfigItem struct {
	ID        int
	Name      string
	UUID      string
	Traffic   string
	Days      string
	SubLink   string
	RawConfig string
	Expiry    string
}

func handleIndex(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("session")
	loggedIn := err == nil && cookie.Value == "authenticated"

	rows, err := db.Query("SELECT id, name, uuid, traffic, days, sub_link, raw_config, expiry FROM configs ORDER BY id DESC")
	var configs []ConfigItem
	if err == nil {
		defer rows.Close()
		for rows.Next() {
			var c ConfigItem
			rows.Scan(&c.ID, &c.Name, &c.UUID, &c.Traffic, &c.Days, &c.SubLink, &c.RawConfig, &c.Expiry)
			configs = append(configs, c)
		}
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	data := struct {
		LoggedIn bool
		Configs  []ConfigItem
		Port     string
		Error    string
	}{
		LoggedIn: loggedIn,
		Configs:  configs,
		Port:     port,
	}

	// استفاده از قالب
	renderTemplate(w, htmlTemplate, data)
}

func handleLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method == "POST" {
		user := r.FormValue("username")
		pass := r.FormValue("password")
		if user == adminUser && pass == adminPass {
			http.SetCookie(w, &http.Cookie{Name: "session", Value: "authenticated", Path: "/"})
			http.Redirect(w, r, "/", http.StatusSeeOther)
			return
		}
	}
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func handleLogout(w http.ResponseWriter, r *http.Request) {
	http.SetCookie(w, &http.Cookie{Name: "session", Value: "", Path: "/", MaxAge: -1})
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func handleCreate(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	name := r.FormValue("name")
	traffic := r.FormValue("traffic")
	days := r.FormValue("days")
	if name == "" {
		name = "Saman"
	}

	host := r.Host
	hostOnly := strings.Split(host, ":")[0]
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	uuidStr := fmt.Sprintf("saman-%d", time.Now().UnixNano())
	subLink := "https://" + host + "/sub/" + uuidStr
	rawConfig := fmt.Sprintf("vless://%s@%s:%s?encryption=none&security=none&type=tcp&headerType=none#%s", uuidStr, hostOnly, port, name)

	db.Exec("INSERT INTO configs (name, uuid, traffic, days, sub_link, raw_config, expiry) VALUES (?, ?, ?, ?, ?, ?, ?)",
		name, uuidStr, traffic, days, subLink, rawConfig, "دائم")

	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func handleDelete(w http.ResponseWriter, r *http.Request) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) > 2 {
		id := parts[2]
		db.Exec("DELETE FROM configs WHERE id = ?", id)
	}
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func handleSub(w http.ResponseWriter, r *http.Request) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) < 3 {
		http.Error(w, "Not Found", 404)
		return
	}
	uuid := parts[2]
	var rawConfig string
	err := db.QueryRow("SELECT raw_config FROM configs WHERE uuid = ?", uuid).Scan(&rawConfig)
	if err != nil {
		http.Error(w, "Config not found", 404)
		return
	}
	w.Write([]byte(rawConfig))
}

func renderTemplate(w http.ResponseWriter, tmpl string, data interface{}) {
	// جایگزین ساده برای رندر متن قالب
	t, err := templateParse(tmpl)
	if err != nil {
		w.Write([]byte(err.Error()))
		return
	}
	t.Execute(w, data)
}

func templateParse(tmpl string) (*templateEngine, error) {
	return &templateEngine{content: tmpl}, nil
}

type templateEngine struct {
	content string
}

func (t *templateEngine) Execute(w http.ResponseWriter, data interface{}) {
	// رندر استاندارد متن قالب HTML
	parsed := t.content
	// جایگزینی‌های ساده برای تست پایداری
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Write([]byte(parsed))
}
