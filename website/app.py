from flask import Flask, request, render_template, flash, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'pi-server',
    'use_pure': True
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def register_page():
    return render_template('register.html')

@app.route('/sobre')
def about_page():
    return render_template('about.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/register', methods=['POST'])
def register():
    conn = None
    cursor = None
    try:
        fullname = request.form['fullname']
        username = request.form['username']
        numero_matricula = request.form['numero_matricula']
        password = "Senac@2025"

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = ("INSERT INTO pedidos_de_usuario "
                 "(fullname, username, password, numero_matricula) "
                 "VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (fullname, username, password, numero_matricula))
        conn.commit()

        # ALTERAÇÃO 1: Se tudo deu certo, redireciona para a rota 'success'
        # A mensagem de flash para sucesso foi removida daqui.
        return redirect(url_for('success'))

    except mysql.connector.Error as db_err:
        print(f"--- ERRO DE BANCO DE DADOS: {db_err} ---")
        # Se der erro, mostra a mensagem na própria página de cadastro.
        flash(f"Erro de Banco de Dados! Usuário ou matrícula podem já existir.", "error")
        return redirect(url_for('register_page'))

    except Exception as e:
        print(f"--- ERRO GERAL INESPERADO: {e} ---")
        # Se der erro, mostra a mensagem na própria página de cadastro.
        flash(f"Ocorreu um erro inesperado no servidor.", "error")
        return redirect(url_for('register_page'))

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)