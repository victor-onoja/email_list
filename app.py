from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

app = Flask(__name__, static_folder='static')
CORS(app)

def init_db():
    with sqlite3.connect('subscribers.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS subscribers
            (email TEXT PRIMARY KEY,
             signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        ''')
        conn.commit()

init_db()

@app.route('/')
def serve_html():
    return send_from_directory('static', 'index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        with sqlite3.connect('subscribers.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
            conn.commit()
        return jsonify({'message': 'Successfully subscribed'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already subscribed'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/subscribers', methods=['GET'])
def get_subscribers():
    try:
        with sqlite3.connect('subscribers.db') as conn:
            c = conn.cursor()
            c.execute('SELECT email, signup_date FROM subscribers ORDER BY signup_date DESC')
            subscribers = [{'email': row[0], 'signup_date': row[1]} for row in c.fetchall()]
        return jsonify(subscribers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)