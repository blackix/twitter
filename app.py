import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_db():
    conn = sqlite3.connect('tweets.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tweet TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            image_path TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id INTEGER NOT NULL,
            parent_reply_id INTEGER,
            name TEXT NOT NULL,
            reply TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            FOREIGN KEY(tweet_id) REFERENCES tweets(id),
            FOREIGN KEY(parent_reply_id) REFERENCES replies(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    username = request.cookies.get('username')
    
    if request.method == 'POST':
        if 'name' in request.form:
            username = request.form['name']
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('username', username)
            return resp
        
        tweet = request.form['tweet']
        date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        image_path = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
        
        conn = sqlite3.connect('tweets.db')
        c = conn.cursor()
        c.execute('INSERT INTO tweets (name, tweet, date_posted, image_path) VALUES (?, ?, ?, ?)', (username, tweet, date_posted, image_path))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('tweets.db')
    c = conn.cursor()
    c.execute('SELECT id, name, tweet, date_posted, image_path FROM tweets ORDER BY date_posted DESC')
    tweets = c.fetchall()
    tweets_with_replies = []
    
    for tweet in tweets:
        c.execute('''
            SELECT id, name, reply, date_posted, parent_reply_id FROM replies 
            WHERE tweet_id = ? ORDER BY date_posted ASC
        ''', (tweet[0],))
        replies = c.fetchall()
        tweets_with_replies.append((tweet, replies))
    
    conn.close()
    
    return render_template('index.html', tweets=tweets_with_replies, username=username, get_reply_author=get_reply_author)

@app.route('/reply/<int:tweet_id>', methods=['POST'])
def reply(tweet_id):
    username = request.cookies.get('username')
    reply = request.form['reply']
    parent_reply_id = request.form.get('parent_reply_id')
    date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect('tweets.db')
    c = conn.cursor()
    c.execute('INSERT INTO replies (tweet_id, parent_reply_id, name, reply, date_posted) VALUES (?, ?, ?, ?, ?)', (tweet_id, parent_reply_id, username, reply, date_posted))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

def get_reply_author(reply_id):
    conn = sqlite3.connect('tweets.db')
    c = conn.cursor()
    c.execute('SELECT name FROM replies WHERE id = ?', (reply_id,))
    author = c.fetchone()[0]
    conn.close()
    return author

if __name__ == '__main__':
    app.run(debug=True)
