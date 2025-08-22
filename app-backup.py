from flask import Flask, request, render_template, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# --- CONFIGURAÇÕES ---
UPLOAD_FOLDER = 'static/imgs/skins'
ALLOWED_EXTENSIONS = {'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'pi-server',
    'use_pure': True
}

# --- CONFIGURAÇÃO DO SISTEMA DE LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Você precisa estar logado para acessar esta página."
login_manager.login_message_category = "error"

class User(UserMixin):
    def __init__(self, id, username, fullname, numero_matricula, skin_url):
        self.id = id
        self.username = username
        self.fullname = fullname
        self.numero_matricula = numero_matricula
        self.skin_url = skin_url

@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['fullname'], user_data['numero_matricula'], user_data['skin_url'])
    return None

# --- ROTAS PÚBLICAS E DE CADASTRO (continuam iguais) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sobre')
def about_page():
    return render_template('about.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cadastro')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # Lógica para adicionar na fila de espera (pedidos_de_usuario)
    fullname = request.form['fullname']
    username = request.form['username']
    numero_matricula = request.form['numero_matricula']
    password_padrao = "Senac@2025"
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = ("INSERT INTO pedidos_de_usuario (fullname, username, password, numero_matricula) VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (fullname, username, password_padrao, numero_matricula))
        conn.commit()
        return redirect(url_for('success'))
    except mysql.connector.Error:
        flash("Erro! Seu usuário ou matrícula podem já existir na nossa fila de espera.", "error")
        return redirect(url_for('register_page'))
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# --- ROTAS DE AUTENTICAÇÃO E PAINEL ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Lógica de login (continua igual)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['fullname'], user_data['numero_matricula'], user_data['skin_url'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload_skin', methods=['POST'])
@login_required
def upload_skin():
    # Lógica de upload de skin (continua igual)
    if 'skin' not in request.files or request.files['skin'].filename == '':
        flash('Nenhum arquivo de skin selecionado.', 'error')
        return redirect(url_for('dashboard'))
    file = request.files['skin']
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = f"{current_user.username}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        skin_url = f"static/imgs/skins/{filename}"
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET skin_url = %s WHERE id = %s", (skin_url, current_user.id))
        conn.commit()
        conn.close()
        flash('Sua skin foi atualizada com sucesso!', 'success')
    else:
        flash('Formato de arquivo inválido. Apenas .png é permitido.', 'error')
    return redirect(url_for('dashboard'))

# --- NOVA ROTA PARA ALTERAÇÃO DE SENHA ---
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('A nova senha e a confirmação não correspondem.', 'error')
        return redirect(url_for('dashboard'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()

    if not user_data or not check_password_hash(user_data['password_hash'], current_password):
        conn.close()
        flash('A sua senha atual está incorreta.', 'error')
        return redirect(url_for('dashboard'))
    
    # Se a senha atual estiver correta, atualiza para a nova
    new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_password_hash, current_user.id))
    conn.commit()
    conn.close()

    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)