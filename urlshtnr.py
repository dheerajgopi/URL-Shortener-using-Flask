#!flask/bin/python

#imports
import sqlite3
from random import choice
from flask import Flask, request, g, redirect, url_for, render_template

#config
DATABASE = 'db/urls.db'

#creating Flask app instance
app = Flask(__name__)
app.config.from_object(__name__)

#connecting with db
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#home page
@app.route('/')
def home():
    return render_template('home.html')

#shorten the url
@app.route('/shorten_url', methods = ['POST'])
def shorten_url():
    url_input = request.form['url_input']
    # checking if given url is already present in db
    cur = g.db.execute('select short_url from urls where real_url=?', (url_input,))
    sht_url = cur.fetchone()
    if sht_url:
        return render_template('home.html', short_url = "localhost:5000/"+sht_url[0])
    else:
        # creating new short url if url not present in db
        done = False
        while not done:
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
            randchars = ""
            for i in range(5):  # generating random chars for short url
                randchars = randchars + choice(chars)
            short_url_full = "localhost:5000/" + randchars
            short_url = randchars
            try:
                g.db.execute('insert into urls (short_url, real_url) values (?, ?)', [short_url, url_input])
                g.db.commit()
                done = True
            except:
                done = False
        return render_template('home.html', short_url = short_url_full)

@app.route('/<short_url>')
def redirect_url(short_url):
    cur = g.db.execute('select real_url from urls where short_url=?', (short_url,))
    url = cur.fetchone()
    redirected_url = url[0]
    return redirect(redirected_url)
    
    
if __name__ == '__main__':
    app.run(debug = True)
