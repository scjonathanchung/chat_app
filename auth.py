from flask import Blueprint, render_template, request, redirect, url_for, session
import hashlib
import sqlite3
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = '用户名和密码不能为空'
        else:
            password_hash = hash_password(password)
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                conn.close()
                return redirect(url_for('auth.login'))  # ✅ 跳转到登录页
            except sqlite3.IntegrityError:
                error = '用户名已存在'
    return render_template('register.html', error=error)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row and verify_password(password, row['password_hash']):
            session['username'] = username
            return redirect(url_for('index'))  # ✅ 修改这里，原来是 chat.index，改为 index
        else:
            error = '用户名或密码错误'
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
