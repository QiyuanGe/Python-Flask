from flask import Flask, flash, render_template, request,redirect,url_for,session,g
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
debug = True                  
app.secret_key = 'secret_key_1'
db = ('user.db')

##before request
@app.before_request
def bofore_request():
    g.db = sqlite3.connect(db)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()


## login
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == "POST":
        name = request.form.get('username')
        password = request.form.get('userPassword')
        cursor = g.db.execute('select * from userinfo where User_name =? and User_password=?',[name,password])
        if cursor.fetchone() is not None:
            session['user'] = name
            flash('Login successfully')
            return redirect(url_for('index'))
        else:
            flash('NO such User!')
            return redirect(url_for("login"))
    return render_template('login.html')

## register part
##insert data to database
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method =='POST':
        username = request.form.get('username')
        password1 = request.form.get('userPassword')
        password2 = request.form.get('userRePassword')
        telephone = request.form.get('userPhone')
        email = request.form.get('userEmail')
        print(username,password1,password2)
        cur = g.db.cursor()
        cur.execute('select * from userinfo where User_name =?',[username])
        if  cur.fetchone is None:
            if password1 == password2:
                sql = 'insert into userinfo (User_name, User_password,Telephone,Email)''values(?,?,?,?)'
                data = (username,password1,telephone,email)
                cur.execute(sql,data)
                db.commit()
                flash ('Successfully registered')
                return redirect(url_for('login'))
        else:
            flash('Already have same username!')
            return render_template('register.html')
    return render_template('register.html')

## main page of website
@app.route('/Calculator',methods = ['GET','POST'])
def index():
    if request.method == "POST" :
        a = request.form['left']
        b = request.form['right']
        c = int(a)+int(b)
        return render_template('index.html',RESULT = str(c))
    return render_template('index.html')

if __name__ == 'main':
    app.run(debug=True)