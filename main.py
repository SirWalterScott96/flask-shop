from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lapo4kado4ka'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


@app.route('/')
def home():

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)