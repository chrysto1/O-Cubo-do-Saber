from flask import Flask, request, render_template, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import logging

# --- CONFIGURAÇÃO DO LOGGING ---
# Cria um ficheiro de log para depuração no servidor
logging.basicConfig(filename='debug.log', level=logging.INFO, 
                    format=f'%(asctime)s %(levelname)s : %(message)s')

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

app = Flask(__name__)
# Carrega a chave secreta de forma segura
app.secret_key = os.environ.get('SECRET_KEY')

# --- CONFIGURAÇÕES GERAIS ---
# Caminho correto para a pasta de skins
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
login_manager.login_view = 'login' # Página para a qual os utilizadores não logados são redirecionados
login_manager.login_message = "Você precisa estar logado para aceder a esta página."
login_manager.login_message_category = "error"

# --- MODELO DE UTILIZADOR PARA O FLASK-LOGIN ---
class User(UserMixin):
    def __init__(self, id, username, fullname, numero_matricula, skin_url):
        self.id = id
        self.username = username
        self.fullname = fullname
        self.numero_matricula = numero_matricula
        self.skin_url = skin_url

@login_manager.user_loader
def load_user(user_id):
    # Carrega um utilizador da base de dados para manter a sessão
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['fullname'], user_data['numero_matricula'], user_data['skin_url'])
    except Exception as e:
        app.logger.error(f"Erro ao carregar utilizador: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    return None

# --- ROTAS PÚBLICAS E DE REGISTO ---
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
    # Apenas adiciona à "fila de espera" (pedidos_de_usuario)
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
    except mysql.connector.Error as e:
        app.logger.error(f"Erro no registo: {e}")
        flash("Erro! O seu utilizador ou matrícula podem já existir na nossa fila de espera.", "error")
        return redirect(url_for('register_page'))
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# --- ROTAS DE AUTENTICAÇÃO E PAINEL PRIVADO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        app.logger.info(f"--- TENTATIVA DE LOGIN --- Username: '{username}'")
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()

            if user_data:
                app.logger.info(f"Utilizador '{username}' encontrado no banco de dados.")
                is_password_correct = check_password_hash(user_data['password_hash'], password)
                app.logger.info(f"A senha para '{username}' está correta? {is_password_correct}")

                if is_password_correct:
                    app.logger.info(f"SUCESSO: Senha correta para '{username}'. A fazer o login.")
                    user = User(user_data['id'], user_data['username'], user_data['fullname'], user_data['numero_matricula'], user_data['skin_url'])
                    login_user(user)
                    return redirect(url_for('dashboard'))
                else:
                    app.logger.warning(f"FALHA: A verificação da senha falhou para '{username}'.")
            else:
                app.logger.warning(f"FALHA: Utilizador '{username}' não encontrado na tabela 'users'.")
        
        except Exception as e:
            app.logger.error(f"Erro durante o processo de login: {e}")
            flash('Ocorreu um erro no servidor. Tente novamente mais tarde.', 'error')
            return render_template('login.html')
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        flash('Utilizador ou senha inválidos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Se o método for POST, significa que o utilizador está a enviar a skin
    if request.method == 'POST':
        if 'skin' not in request.files:
            flash('Nenhum ficheiro de skin selecionado.', 'error')
            return redirect(url_for('dashboard'))

        file = request.files['skin']

        if file.filename == '':
            flash('Nenhum ficheiro selecionado.', 'error')
            return redirect(url_for('dashboard'))

        if file and allowed_file(file.filename):
            try:
                # Salva o arquivo localmente para a pré-visualização no dashboard
                filename = f"{current_user.username}.png"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_content = file.read()
                with open(file_path, 'wb') as f:
                    f.write(file_content)

                # URL da API do Mineskin
                MINESKIN_API_URL = "https://api.mineskin.org/generate/upload"
                files_for_api = {'file': (file.filename, file_content, 'image/png')}
                
                app.logger.info(f"A enviar a skin para a API Mineskin para o utilizador {current_user.username}...")
                response = requests.post(MINESKIN_API_URL, files=files_for_api, timeout=15)
                response.raise_for_status()
                
                skin_data = response.json()
                app.logger.info("Resposta da API Mineskin recebida com sucesso.")

                # Extrai os dados da resposta da API
                value = skin_data['data']['texture']['value']
                signature = skin_data['data']['texture']['signature']
                timestamp = int(time.time() * 1000)
                nick = current_user.username

                # Conecta ao banco de dados e insere/atualiza os dados na tabela 'skins'
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM skins WHERE nick = %s", (nick,))
                result = cursor.fetchone()
                
                if result:
                    cursor.execute("""
                        UPDATE skins SET value = %s, signature = %s, timestamp = %s WHERE nick = %s
                    """, (value, signature, timestamp, nick))
                else:
                    cursor.execute("""
                        INSERT INTO skins (nick, value, signature, timestamp) VALUES (%s, %s, %s, %s)
                    """, (nick, value, signature, timestamp))
                
                # Atualiza a URL da skin na tabela 'users' para a pré-visualização
                skin_url_for_db = f"static/imgs/skins/{filename}"
                cursor.execute("UPDATE users SET skin_url = %s WHERE id = %s", (skin_url_for_db, current_user.id))

                conn.commit()
                flash('A sua skin foi atualizada com sucesso no jogo!', 'success')

            except requests.exceptions.RequestException as e:
                app.logger.error(f"Erro ao comunicar com o serviço de skins: {e}")
                flash(f'Erro ao comunicar com o serviço de skins. Tente novamente mais tarde.', 'danger')
            except Exception as e:
                app.logger.error(f"Ocorreu um erro inesperado durante o upload da skin: {e}")
                flash(f'Ocorreu um erro inesperado: {e}', 'danger')
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()
        else:
            flash('Formato de ficheiro inválido. Apenas .png é permitido.', 'error')
        
        # Após o POST, redireciona para a mesma página para evitar reenvio do formulário
        return redirect(url_for('dashboard'))

    # Se o método for GET, apenas renderiza a página normalmente
    return render_template('dashboard.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('A nova senha e a confirmação não correspondem.', 'error')
        return redirect(url_for('dashboard'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user.id,))
        user_data = cursor.fetchone()

        if not user_data or not check_password_hash(user_data['password_hash'], current_password):
            flash('A sua senha atual está incorreta.', 'error')
            return redirect(url_for('dashboard'))
        
        new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_password_hash, current_user.id))
        conn.commit()

        flash('Senha alterada com sucesso!', 'success')
    except Exception as e:
        app.logger.error(f"Erro ao alterar a senha: {e}")
        flash('Ocorreu um erro ao alterar a sua senha.', 'error')
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)