from flask import Flask, flash, render_template, request,redirect,url_for,make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
class Config(object):
    ##sqlachemy config
    SQLALCHEMY_DATABASE_URI = 'mysql://Qiyuan:mysql@127.0.0.1:3306/Users'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
app.config.from_object(Config)
db = SQLAlchemy(app)
app.secret_key = 'admain'

## database model
class Role(db.Model):
    # user's role
    __tablename__ = 'tbl_roles'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(32),unique = True)
    users = db.relationship("User", backref="role")

class User(db.Model):
    #user's information
    __table__name = 'tbl_usersinformation'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(64),unique = True)
    password = db.Column(db.String(128),unique = False)
    role_id = db.Column(db.Integer,db.ForeignKey("tbl_roles.id"))


if __name__ == 'main':
    db.create_all()
    app.run(debug=True)

## login
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        name = request.form.get('username')
        passwd = request.form.get('userPassword')
        if name == 'Cloud' and passwd == '123456' :
            return redirect(url_for('index'))
        else:
            return render_template("login.html")

## main page of website
@app.route('/Calculator',methods = ['GET','POST'])
def index():
    if request.method == "POST" :
        a = request.form['left']
        b = request.form['right']
        c = int(a)+int(b)
        return render_template('index.html',RESULT = str(c))
    return render_template('index.html')
