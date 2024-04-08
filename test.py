from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# Головна сторінка
@app.route('/')
def index():
    return 'Welcome to the main page!'

# Перша сторінка
@app.route('/page1')
def page1():
    return 'This is page 1 <a href="/page2">Go to page 2</a>'

# Друга сторінка
@app.route('/page2')
def page2():
    # Перевірка, чи є referrer
    referrer = request.referrer
    if referrer:
        return f'You came from: {referrer}'
    else:
        return 'You came directly to this page'

if __name__ == '__main__':
    app.run(debug=True)
