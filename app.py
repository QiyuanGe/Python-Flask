from flask import Flask, flash, render_template, request, redirect, url_for, session, g
from flask_socketio import SocketIO,send,emit
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import time
from datetime import datetime
from functools import wraps 
import config
from threading import Lock

app = Flask(__name__)   
async_mode = None  
app.config.from_object(config)  
db = sqlite3.connect('G:/pythonproject/env/user.db', check_same_thread=False)

## login
@app.route('/', methods = ['GET','POST'])
def login():
    if request.method == "POST":
        ID = request.form.get('userID')
        name = request.form.get('username')
        password = request.form.get('userPassword')
        Side_num = request.form.get('Side_num') ## off work
        cur = db.cursor()
        cur.execute('select * from UserInformation where User_name =? and Password=? and User_ID=?',[name,password,ID])
        if cur.fetchone() is not None:
            session['ID'] = ID
            session['user'] = name
            session.parameter = True
            if Side_num == 0:
                flash ("Please connect to your arduino!")
                db.commit()
                return redirect(url_for('login'))
            else:
                session['Side_num'] = Side_num
                session.parameter = True
                db.commit()
                return redirect(url_for('index'))
        else:
            flash('NO such User!')
            return redirect(url_for("login"))
    return render_template('login.html')

@app.context_processor
def mycontext():
    usern = session.get('user')
    userid = session.get('ID')
    Side_num = session.get('Side_num')
    if usern and userid:
        return {'username': usern, "userID": userid,"Side_num":Side_num}
    else:
        return {}

def loginFirst(func):
    @wraps(func)
    def wrappers(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)    
    return wrappers

## register part
##insert data to database
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method =='POST':
        userID = request.form.get('userID')
        username = request.form.get('username')
        password1 = request.form.get('userPassword')
        password2 = request.form.get('userRePassword')
        print(username,password1,password2)
        cur = db.cursor()
        cur.execute('select * from UserInformation where User_name =? and User_ID =?',[username,userID])
        if  cur.fetchone() is None:
            if password1 == password2:
                sql = 'insert into UserInformation (User_ID, User_name, Password)''values(?,?,?)'
                data = (userID,username,password1)
                cur.execute(sql,data)
                flash ('Successfully registered')
                return redirect(url_for('login'))
            else:
                flash('Please enter same password!')
        else:
            flash('Already have same username!')
            return render_template('register.html')
    return render_template('register.html')

## main page of website
@app.route('/index',methods = ['GET','POST'])
@loginFirst
def index():
        Username = session.get('user')
        ID = session.get('ID')
        Side_num = session.get('Side_num')
        Task_name = []
        time_now = time.strftime("%Y-%m-%d %X", time.localtime())
        Activity_time = []
        Activity_type = []
        Sum_time = []
        cur = db.cursor()
        cur.execute('select * from task where Side_number =? and User_ID =?',[Side_num,ID])
        result3 = cur.fetchone()
        if result3 == None:
            flash('Please enter a new task!')
            return render_template('index.html',Side_num = Side_num,Task_name=Task_name,Activity_time=Activity_time,Actyvity_type=Activity_type,Sum_time=Sum_time)
        else:
            print(result3)
            Side_num = result3[2]
            Task_name= result3[3]
            Activity_time = result3[4]
            Activity_type= result3[5]
            Sum_time = result3[6] +time_now-Activity_time
            Activity_time = time_now
            cur.execute('update task set Activity_time=? where User_ID=? and Side_number=?',(Activity_time,ID,Side_num))
            cur.execute('update task set Sum_time=? where User_ID=? and Side_number=?',(Sum_time,ID,Side_num))
            db.commit()
            print(Side_num,Task_name, Activity_time, Activity_type,Sum_time)
            return render_template('index.html',Side_num = Side_num,Task_name=Task_name,Activity_time=Activity_time,Actyvity_type=Activity_type,Sum_time=Sum_time)

@app.route('/endTask',methods = ['GET','POST'])
@loginFirst
def endTask():
        ID = session.get('ID')
        Side_num = session.get('Side_num')
        cur = db.cursor()
        c = ('end',ID,Side_num)
        sql = 'update task set Activity_type=? where User_ID=? and Side_number=?'
        cur.execute(sql,c)
        db.commit()
        c = (7,ID,Side_num)
        sql = 'update task set Side_number=? where User_ID=? and Side_number=?'
        cur.execute(sql,c)
        db.commit()
        return redirect(url_for('index'))

@app.route('/upgradeNewtask',methods =['GET','POST'])
@loginFirst
def upgradeNewtask():
    if request.method =='POST':
        Username = session.get('user')
        ID = session.get('ID')
        task_name = request.form.get('Task_name')
        Side_number = request.form.get('Side_number')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(ID,Side_number))
        if cur.fetchone() == None and Side_number != 6:
            sql = 'insert into task (User_ID,Side_number,Task_name, Activity_time,Activity_type)''values(?,?,?,?,?)'
            Activity_time = time.strftime("%Y-%m-%d %X", time.localtime())
            Activity_type = 'upgrade'
            data = (ID,Side_number,task_name,Activity_time,Activity_type)
            print(data)
            cur.execute(sql,data)
            db.commit()
            return redirect(url_for('index'))
        elif cur.fetchone() != None and Side_number != 6:
            flash("Already have a task! Please change side!")
            return render_template('upgrade.html')
        elif Side_number == 6:
            flash('Miontor is off work!')
            return render_template('upgrade.html')
    return render_template('upgrade.html')


@app.route('/upgradeSide_num',methods =['GET','POST'])
@loginFirst
def upgradeSide_num():
    if request.method =='POST':
        Username = session.get('user')
        User_ID = session.get('ID')
        Side_numNow = session.get('Side_num')
        Side_numChange = request.form.get('Side_num')
        Task_name = []
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(User_ID,Side_numChange))
        if cur.fetchone() == None and Side_numChange != 6:
            sql = 'update task set Side_number=? where User_Id=? and Side_number=?'
            c = (Side_numChange,User_ID,Side_numNow)
            cur.execute(sql,c)
            db.commit()
            session['Side_num'] = Side_numChange
            return redirect(url_for('index'))
        elif cur.fetchone() != None and Side_numChange != 6:
            flash('This side of tube already got a task! Please change another side!')
            return render_template('upgrade.html')
        elif Side_numChange == 6:
            flash('Miontor is off work!')
            return render_template('upgrade.html')
    return render_template('upgrade.html')

@app.route('/upgradeTask_name',methods =['GET','POST'])
@loginFirst
def upgradeTask_name():
    if request.method =='POST':
        Username = session.get('user')
        User_ID = session.get('ID')
        Side_num = session.get('Side_num')
        Task_nameChange = request.form.get('Task_name')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(User_ID,Side_num))
        if cur.fetchone() == None:
            sql = 'update task set Task_name=? where User_Id=? and Side_number=?'
            c = (Task_nameChange,User_ID,Side_num)
            cur.execute(sql,c)
            db.commit()
        elif cur.fetchone() != None :
            flash('This task already exited! Please change another name!')
            return render_template('upgrade.html')
    return render_template('upgrade.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))  

if __name__ == 'main':
    app.run(debug = True, host='0.0.0.0', port=5000)
    db.close()