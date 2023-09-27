from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
openai.api_key = os.getenv('API_KEY')
app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_DB')

mysql = MySQL( app )

conversation = []

@app.route('/', methods=['GET', 'POST'])
def chat():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    except:
        return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

    id = session.get('id')

    if request.method == 'GET':

        try:
            cursor.execute('SELECT * FROM chats WHERE id={}'.format(id))
        except:
            return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

        chat = cursor.fetchall()
        return render_template('index.html', chat=chat)

    if request.method == 'POST':
        data = request.get_json()
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": data["question"]}
            ]
        )
        answer = completion['choices'][0]['message']['content']

        try:
            cursor.execute('INSERT INTO chats VALUES ({}, \'{}\', \'{}\')'.format(id, data["question"], answer))
        except:
            return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

        mysql.connection.commit()
        return jsonify( answer )

    # return render_template('index.html')

@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html', error='Error!', message='Something went wrong!')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    except:
        return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

    mesage = ''
    if request.method == 'POST' and 'user' in request.form and 'password' in request.form:
        userName = request.form['user']
        password = request.form['password'].encode('utf-8')

        try:
            cursor.execute('SELECT * FROM users WHERE name = \'{}\''.format(userName))
        except:
            return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

        user = cursor.fetchone()
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = user['id']
            session['user'] = user['name']
            mesage = 'Successful loggin!'
            return redirect(url_for('chat'))
        else:
            mesage = 'Wrong credentials!'
    return render_template('login.html', mesage = mesage)

@app.route('/logout', methods=['GET'])
def logout():
    session['loggedin'] = False
    session['id'] = ''
    session['user'] = ''
    return redirect(url_for('login'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    except:
        return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

    mesage = ''
    if request.method == 'POST' and 'user' in request.form and 'password' in request.form:
        user = request.form['user']
        password = request.form['password'].encode('utf-8')
        hashed_pwd = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        try:
            cursor.execute('SELECT * FROM users WHERE name = \'{}\''.format(user))
        except:
            return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

        account = cursor.fetchone()
        if account:
            mesage = 'The user already exists!'
        elif not user or not password:
            mesage = 'Please complete the form!'
        else:

            try:
                cursor.execute('INSERT INTO users VALUES (NULL, \'{}\', \'{}\')'.format(user, hashed_pwd))
                mysql.connection.commit()
            except:
                return render_template('error.html', error='Error in the database!', message='Something went wrong when trying to connect to the database!')

            mesage = 'Usuario creado!'
            # return redirect(url_for('login'))
    elif request.method == 'POST':
        mesage = 'Please complete the form!'
    return render_template('signin.html', mesage = mesage)

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
