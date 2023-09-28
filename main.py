from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import openai
from dotenv import load_dotenv
import os

# Create the flask app
app = Flask( __name__ )

# Load the environment variables
load_dotenv()
openai.api_key = os.getenv( 'API_KEY' )
app.secret_key = os.getenv( 'SECRET_KEY' )
app.config[ 'MYSQL_HOST' ] = os.getenv( 'DB_HOST' )
app.config[ 'MYSQL_USER' ] = os.getenv( 'DB_USER' )
app.config[ 'MYSQL_PASSWORD' ] = os.getenv( 'DB_PASSWORD' )
app.config[ 'MYSQL_DB' ] = os.getenv( 'DB_DB' )

# Get the database driver
mysql = MySQL( app )
cursor = None

DB_ACTIONS = {
    'ADD_CHAT': 'ADD_CHAT',
    'GET_CHAT': 'GET_CHAT',
    'UPDATE_CHAT': 'UPDATE_CHAT',
    'ADD_USER': 'ADD_USER',
    'GET_USER': 'GET_USER'
}

# Error handling messages format
class ErrorMessage:
    def __init__( self, error, message ):
        self.error = error
        self.message = message

# Create the MySQL cursor or get the currently created one
def getCursor():
    try:
        return cursor or mysql.connection.cursor( MySQLdb.cursors.DictCursor )
    except:
        return ErrorMessage(
            'Error in the database!',
            'Something went wrong when connecting to the database.'
        )

# Queries runner
def runQuery( action, params ):
    cursor = getCursor()
    
    if( type( cursor ) is ErrorMessage ):
        return cursor

    try:
        if action == DB_ACTIONS[ 'ADD_CHAT' ]:
            cursor.execute( "INSERT INTO chats VALUES ({}, '{}', '{}')".format(
                params[ 'id' ],
                params[ 'question' ],
                params[ 'answer' ]
            ) )

            mysql.connection.commit()
            return

        if action == DB_ACTIONS[ 'GET_CHAT' ]:
            cursor.execute( 'SELECT * FROM chats WHERE id={}'.format(
                params[ 'id' ]
            ) )
            return cursor.fetchall()

        if action == DB_ACTIONS[ 'ADD_USER' ]:
            cursor.execute( "INSERT INTO users VALUES (NULL, '{}', '{}' )".format(
                params[ 'userName' ],
                params[ 'hashedPwd' ]
            ) )

            mysql.connection.commit()
            return

        if action == DB_ACTIONS[ 'GET_USER' ]:
            cursor.execute( "SELECT * FROM users WHERE name = '{}'".format(
                params[ 'userName' ]
            ) )

            return cursor.fetchone()

    except:
        return ErrorMessage(
            'Error in the database!',
            'Something went wrong in the database.'
        )

# Error rendering method
def renderError( errorMessage ):
    return render_template(
            'error.html',
            error = errorMessage.error,
            message = errorMessage.message
        )

@app.route( '/', methods=[ 'GET', 'POST' ] )
def chat():
    if not session.get( 'loggedin' ):
        return redirect(url_for( 'login' ) )

    id = session.get( 'id' )

    if request.method == 'GET':
        response = runQuery( DB_ACTIONS[ 'GET_CHAT' ], { 'id': id } )

        if( type( response ) is ErrorMessage ):
            return renderError( response )
        
        chat = response
        return render_template( 'index.html', chat = chat )

    if request.method == 'POST':
        print( 'POST' )
        data = request.get_json()
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[ {
                'role': 'user',
                'content': data[ 'question' ]
            } ]
        )
        answer = completion[ 'choices' ][ 0 ][ 'message' ][ 'content' ]

        response = runQuery( DB_ACTIONS[ 'ADD_CHAT' ], {
            'id': id,
            'question': data[ 'question' ],
            'answer': answer
        } )

        if( type( response ) is ErrorMessage ):
            return renderError( response )

        return jsonify( answer )

@app.route( '/error', methods=[ 'GET' ] )
def error():
    return render_template(
        'error.html',
        error = 'Error!',
        message = 'Something went wrong!'
    )

@app.route( '/login', methods=[ 'GET', 'POST' ] )
def login():
    mesage = ''
    if request.method == 'POST' and 'user' in request.form and 'password' in request.form:
        userName = request.form[ 'user' ]
        password = request.form[ 'password' ].encode( 'utf-8' )

        response = runQuery( DB_ACTIONS[ 'GET_USER' ], {
            'userName': userName
        } )
        
        if( type( response ) is ErrorMessage ):
            return renderError( response )
        
        user = response

        if user and bcrypt.checkpw(password, user[ 'password' ].encode( 'utf-8' ) ):
            session[ 'loggedin' ] = True
            session[ 'id' ] = user[ 'id' ]
            session[ 'user' ] = user[ 'name' ]
            mesage = 'Successful loggin!'
            return redirect(url_for( 'chat' ) )
        else:
            mesage = 'Wrong credentials!'

    return render_template( 'login.html', mesage = mesage )

@app.route( '/logout', methods=[ 'GET' ] )
def logout():
    session[ 'loggedin' ] = False
    session[ 'id' ] = ''
    session[ 'user' ] = ''
    return redirect(url_for( 'login' ) )

@app.route( '/signin', methods=[ 'GET', 'POST' ] )
def signin():
    mesage = ''
    if request.method == 'POST' and 'user' in request.form and 'password' in request.form:
        userName = request.form[ 'user' ]
        password = request.form[ 'password' ].encode( 'utf-8' )
        hashedPwd = bcrypt.hashpw(
            password,
            bcrypt.gensalt()
        ).decode( 'utf-8' )

        response = runQuery( DB_ACTIONS[ 'GET_USER' ], {
            'userName': userName
        } )

        if( type( response ) is ErrorMessage ):
            return renderError( response )

        account = response
        if account:
            mesage = 'The user already exists!'
        elif not userName or not password:
            mesage = 'Please complete the form!'
        else:
            response = runQuery( DB_ACTIONS[ 'ADD_USER' ], {
                'userName': userName,
                'hashedPwd': hashedPwd
            } )
            
            if( type( response ) is ErrorMessage ):
                return renderError( response )
        
            mesage = 'Usuer created!'
            return redirect( url_for( 'login' ) )

    elif request.method == 'POST':
        mesage = 'Please complete the form!'

    return render_template( 'signin.html', mesage = mesage )

@app.errorhandler( 404 )
def not_found( error ):
    return redirect( url_for( 'chat' ) )

if __name__ == '__main__':
    app.run( debug = True, port = 4000 )
