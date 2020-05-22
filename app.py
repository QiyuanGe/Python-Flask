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
def days(str1, str2):
    num = 0
    return num
## login
@app.route('/', methods = ['GET','POST'])
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
            session['Side_number'] = Side_number
            session['Side_change'] = Side_number
            db.commit()
            return redirect(url_for('index'))
        else:
            flash('NO such User!')
            return redirect(url_for("login"))
    return render_template('login.html')

@app.context_processor
def mycontext():
    usern = session.get('username')
    userid = session.get('userID')
    Side_number = session.get('Side_number')
    if usern and userid and Side_number:
        return {'username': usern, "userID": userid,"Side_num":Side_number}
    else:
        return {}

def loginFirst(func):
    @wraps(func)
    def wrappers(*args, **kwargs):
        if not session.get('username'):
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
        Username = session.get('username')
        ID = session.get('userID')
        Side_number = session.get('Side_number')
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
                return render_template('index.html')
            else:
                Side_number = result3[1]
                Task_name= result3[2]
                Activity_time = result3[3]
                Activity_type= result3[4]
                Sum_time = result3[5]
                session['Sum_time'] = Sum_time
                Sum_hour = int(Sum_time/60/60)
                Sum_min = int(Sum_time/60)-Sum_hour*60
                Sum_second = Sum_time - Sum_hour*60*60-Sum_min*60
            print(Side_number,Task_name, Activity_time, Activity_type,Sum_time)
            return render_template('index.html',Side_number = Side_number,Task_name=Task_name,Activity_time=Activity_time,Actyvity_type=Activity_type,Sum_hour=Sum_time,Sum_min=Sum_min,Sum_second=Sum_second)
        else:
            Sum_timeNew = 0
            session['Side_number'] = Side_number
            session['time_end'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(session.get('time_start'))
            print(session.get('time_end'))
            time_start = datetime.strptime(session['time_start'],"%Y-%m-%d %H:%M:%S")
            time_end =  datetime.strptime(session['time_end'],"%Y-%m-%d %H:%M:%S")
            working_time = (time_end - time_start).seconds
            Activity_time = session.get('time.end')
            Sum_timeNew = working_time + session['Sum_time'] 
            print(session['Sum_time'])
            print(Sum_timeNew)
            c = db.cursor()
            c.execute('update task set Activity_time=? where User_ID=? and Side_number=?',(Activity_time,ID,Side_number))
            c.execute('update task set Sum_time=? where User_ID=? and Side_number=?',(Sum_timeNew,ID,Side_number))
            db.commit()
            return render_template('index.html')
            return redirect(url_for('index'))
        

@app.route('/endTask',methods = ['GET','POST'])
@loginFirst
def endTask():
        ID = session.get('userID')
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

@app.route('/submit',methods = ['GET','POST'])
def submit():
    return redirect(url_for('index'))

@app.route('/upgradeNewtask',methods =['GET','POST'])
@loginFirst
def upgradeNewtask():
    if request.method =='POST':
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
            print(data)
            ###   this code doesn't work ...... from here
            cur.execute(sql,data)
            db.commit()
            #### end here
            return render_template('upgrade.html')
            ####   this code doesn't work.... from here
            return redirect(url_for('index'))
            ####   end here
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
        Username = session.get('username')
        User_ID = session.get('userID')
        Side_numNow = session.get('Side_num')
        Side_numChange = request.form.get('Side_num')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(User_ID,Side_numChange))
        if cur.fetchone() == None and Side_numChange != 6:
            sql = 'update task set Side_number=? where User_Id=? and Side_number=?'
            c = (Side_numChange,User_ID,Side_numNow)
            cur1 = db.cursor()
            #### this code doesn't work..... 
            cur1.execute(sql,c)
            db.commit()
            return render_template('upgrade.html')
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
        Username = session.get('username')
        User_ID = session.get('userID')
        Side_number = request.form.get('Side_number')
        Task_nameChange = request.form.get('Task_name')
        cur = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur.execute(sql,(User_ID,Side_number))
        if cur.fetchone() == None:
            if Task_nameChange == None:
                flash('Please enter new task name!')
                return render_template('upgrade.html')
            else:
                sql = 'update task set Task_name=? where User_Id=? and Side_number=?'
                c = (Task_nameChange,User_ID,Side_number)
                cur1 = db.cursor()
                #### this code doesn't work
                cur1.execute(sql,c)
                db.commit()
                return render_template('upgrade.html')
                #### and this also.....
                return redirect(url_for('index'))
        elif cur.fetchone() != None :
            flash('This task already exited! Please change another name!')
            return render_template('upgrade.html')
    return render_template('upgrade.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))  

@app.route('/changeSide_number')
def change():
    session['Side_change'] =  random.randint(1,5)  
    return redirect(url_for('index'))

if __name__ == 'main':
    app.run(debug = True, host='0.0.0.0', port=5000)
    db.close()