from flask import Flask, flash, render_template, request, redirect, url_for, session, g
import sqlite3
import time
import random
from datetime import datetime
from functools import wraps 
import config
from threading import Lock

app = Flask(__name__) 
app.config.from_object(config)  
db = sqlite3.connect('G:/pythonproject/env/user.db', check_same_thread=False)

## make sure the user has logined
@app.before_request
def login_required():
    if request.path in ['/login','/register']: 
        return None
    user=session.get('userID')  
    if not user:                 
        return redirect('/login')
    return None

## login
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == "POST":
        ID = request.form.get('userID')
        name = request.form.get('username')
        password = request.form.get('userPassword')
        Side_number = request.form.get('Side_number') 
        cur = db.cursor()
        cur.execute('select * from UserInformation where User_name =? and Password=? and User_ID=?',[name,password,ID])
        if cur.fetchone() is not None:
            session['userID'] = ID
            session['username'] = name
            session.parameter = True
            if Side_number != None:
                session['Side_number'] = Side_number
                session['Side_change'] = Side_number
                session.permanent = True
                db.commit()
                return redirect(url_for('index'))
            else:
                return('Please connect to your task monitor!')
                return redirect(url_for('login'))
        else:
            flash('NO such User!')
            return redirect(url_for("login"))
    return render_template('login.html')

@app.context_processor
def mycontext():
    username = session.get('username')
    userid = session.get('userID')
    Side_number = session.get('Side_number')
    if username and userid and Side_number:
        return {'username': username, "userID": userid,"Side_num":Side_number}
    else:
        return {}




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
                db.commit()
                flash ('Successfully registered')
                return redirect(url_for('login'))
            else:
                flash('Please enter same password!')
        else:
            flash('Already have same username!')
            return render_template('register.html')
    return render_template('register.html')

## main page of website
@app.route('/',methods = ['GET','POST'])
def index():
        Username = session.get('username')
        ID = session.get('userID')
        Side_number = session.get('Side_number')
        session['Sum_time'] = 0
        if session.get('Side_change') == session.get('Side_number'):
            print(Side_number)
            session['time_start'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cur = db.cursor()
            cur.execute('select * from task where  User_ID =? and Side_number = ?',[ID,Side_number])
            result3 = cur.fetchone()
            print(result3)
            if result3 == None:
                flash('Please enter a new task!')
                db.commit()
                return render_template('index.html',Side_number = Side_number,Task_name='',Activity_time='',Actyvity_type='',Sum_hour=0,Sum_min=0,Sum_second=0)
            else:
                Task_name= result3[2]
                Activity_time = result3[3]
                Activity_type= result3[4]
                session['Sum_time'] = result3[5]
                print(session.get('Sum_time'))
                Sum_hour = int(session.get('Sum_time')/60/60)  ##hours
                Sum_min = int(session.get('Sum_time')/60)-Sum_hour*60   ## minutes
                Sum_second = session.get('Sum_time') - Sum_hour*60*60-Sum_min*60  ##seconds
                print(Side_number,Task_name, Activity_time, Activity_type,session.get('Sum_time'))
                return render_template('index.html',Side_number = Side_number,Task_name=Task_name,Activity_time=Activity_time,Actyvity_type=Activity_type,Sum_hour=Sum_hour,Sum_min=Sum_min,Sum_second=Sum_second)
        else:
            Sum_timeNew = 0   ### start calculate the last task's sum time
            session['Side_number'] = session.get('Side_numberChange')
            session['time_end'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(session.get('time_start'))
            print(session.get('time_end'))
            time_start = datetime.strptime(session['time_start'],"%Y-%m-%d %H:%M:%S")
            time_end =  datetime.strptime(session['time_end'],"%Y-%m-%d %H:%M:%S")
            working_time = (time_end - time_start).seconds
            Activity_time = session.get('time_end')
            Sum_timeNew = working_time + session.get('Sum_time') 
            print(session['Sum_time'])
            print(Sum_timeNew)
            c = db.cursor()
            c.execute('update task set Activity_time=? where User_ID=? and Side_number=?',(Activity_time,ID,Side_number))
            c.execute('update task set Sum_time=? where User_ID=? and Side_number=?',(Sum_timeNew,ID,Side_number))
            db.commit()
            return render_template('index.html')
        
@app.route('/endTask',methods = ['GET','POST'])
def endTask():
    if request.method == "POST":
        ID = session.get('userID')
        Side_num = session.get('Side_num')
        cur = db.cursor()
        c = ('end',ID,Side_num)
        sql = 'update task set Activity_type=? where User_ID=? and Side_number=?'
        cur.execute(sql,c)
        db.commit()
        cur1 = db.cursor()
        c = (7,ID,Side_num)
        sql = 'update task set Side_number=? where User_ID=? and Side_number=?'
        c.execute(sql,c)
        db.commit()
        return redirect(url_for('index'))


@app.route('/upgradeNewtask',methods =['GET','POST'])
def upgradeNewtask():
    if request.method =='GET':
        return render_template('upgradeNewtask.html')
    else:
        Username = session.get('username')
        ID = session.get('userID')
        task_name = request.form.get('Task_name')
        Side_number = request.form.get('Side_number')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(ID,Side_number))
        if cur.fetchone() == None and Side_number != 6:
            sql = 'insert into task (User_ID,Side_number,Task_name, Activity_time,Activity_type,Sum_time)''values(?,?,?,?,?,?)'
            Activity_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            Activity_type = 'upgrade'
            Sum_time = 0
            data = (ID,Side_number,task_name,Activity_time,Activity_type,Sum_time)
            cur.execute(sql,data)
            db.commit()
            flash ('Successfully upgrade a new task!')
            return redirect(url_for('index'))
        elif cur.fetchone() != None and Side_number != 6:
            flash("Already have a task! Please change side!")
            return render_template('upgradeNewtask.html')
        elif Side_number == 6:
            flash('Miontor is off work!')
            return render_template('upgradeNewtask.html')
    return render_template('upgradeNewtask.html')


@app.route('/upgradeSide_num',methods =['GET','POST'])
def upgradeSide_num():
    if request.method =='GET':
        return render_template('upgradeSide_number.html')
    else:
        Username = session.get('username')
        User_ID = session.get('userID')
        Task_name = request.form.get('Task_name')
        Side_numChange = request.form.get('Side_number')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(User_ID,Side_numChange))
        if cur.fetchone() == None and Side_numChange != 6:
            sql = 'update task set Side_number=? where User_Id=? and Task_name=?'
            c = (Side_numChange,User_ID,Task_name)
            print(c)
            cur1 = db.cursor()
            cur1.execute(sql,c)
            db.commit()
            flash ('Successfully changed the side number !')
            return redirect(url_for('index'))
        elif cur.fetchone() != None and Side_numChange != 6:
            flash('This side of tube already got a task! Please change another side!')
            return render_template('upgradeSide_number.html')
        elif Side_numChange == 6:
            flash('Miontor is off work!')
            return render_template('upgradeSide_number.html')
    return render_template('upgradeSide_number.html')

@app.route('/upgradeTask_name',methods =['GET','POST'])
def upgradeTask_name():
    if request.method =='GET':
        return render_template('upgradeTaskname.html')
    else:
        Username = session.get('username')
        User_ID = session.get('userID')
        Side_number = request.form.get('Side_number')
        Task_nameChange = request.form.get('Task_name')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Task_name=?'
        cur.execute(sql,(User_ID,Task_nameChange))
        if cur.fetchone() == None:
            if Task_nameChange == None:
                flash('Please enter new task name!')
                return render_template('upgradeTaskname.html')
            else:
                sql = 'update task set Task_name=? where User_Id=? and Side_number=?'
                c = (Task_nameChange,User_ID,Side_number)
                print(c)
                cur1 = db.cursor()
                cur1.execute(sql,c)
                db.commit()
                flash ('Successfully changed the task name!')
                return redirect(url_for('index'))
        else:
            flash('This task already exited! Please change another name!')
            return render_template('upgradeTaskname.html')
    return render_template('upgradeTaskname.html')
    
@app.route('/logout')
def logout():
            ID =session.get('userID') 
            Side_number = session.get('Side_number') 
            Sum_timeNew = 0   ### start calculate the last task's sum time
            session['Side_number'] = session.get('Side_numberChange')
            session['time_end'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(session.get('time_start'))
            print(session.get('time_end'))
            time_start = datetime.strptime(session['time_start'],"%Y-%m-%d %H:%M:%S")
            time_end =  datetime.strptime(session['time_end'],"%Y-%m-%d %H:%M:%S")
            working_time = (time_end - time_start).seconds
            Activity_time = session.get('time_end')
            Sum_timeNew = working_time + session.get('Sum_time') 
            print(session['Sum_time'])
            print(Sum_timeNew)
            c = db.cursor()
            c.execute('update task set Activity_time=? where User_ID=? and Side_number=?',(Activity_time,ID,Side_number))
            c.execute('update task set Sum_time=? where User_ID=? and Side_number=?',(Sum_timeNew,ID,Side_number))
            db.commit()
            session.clear()
            return redirect(url_for('login'))  

@app.route('/changeSide_number')
def change():
    session['Side_change'] =  random.randint(1,5) 
    print(session.get('username'))
    return redirect(url_for('index'))

if __name__ == 'main':
    app.run(debug = True, host='0.0.0.0', port=5000)
    db.close()