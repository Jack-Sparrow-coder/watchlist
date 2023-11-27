from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/home')

def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'