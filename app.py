from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from db import init_db, get_db_connection
from auth import auth_bp
from datetime import datetime
import socket

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 换成随机安全密钥
app.register_blueprint(auth_bp)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.168.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('chat.html', username=session['username'])

@app.route('/messages')
def messages():
    if 'username' not in session:
        return jsonify([])
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username, msg, time FROM messages ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return jsonify([tuple(row) for row in rows][::-1])

@app.route('/send', methods=['POST'])
def send():
    if 'username' not in session:
        return '请先登录', 403
    msg = request.form.get('msg', '').strip()
    if not msg:
        return '消息不能为空', 400
    username = session['username']
    t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (username, msg, time) VALUES (?, ?, ?)", (username, msg, t))
    conn.commit()
    conn.close()
    return 'OK'

if __name__ == '__main__':
    init_db()
    print(f"访问：http://{get_local_ip()}:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)  # ← 添加 debug=True

