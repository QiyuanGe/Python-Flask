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
    if request.path in ['/login','/register','/Connection_check']: 
        return None
    user=session.get('userID')  
    if not user:     
        flash('PLease login to your account!')            
        return redirect('/login')
    return None

## login
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == "POST":
        ID = request.form.get('userID')
        name = request.form.get('username')
        password = request.form.get('userPassword')
        cur = db.cursor()
        cur.execute('select * from UserInformation where User_name =? and Password=? and User_ID=?',[name,password,ID])
        print(ID,name,password)
        result = cur.fetchone()
        print(result)
        if result is not None:
            session['userID'] = ID
            session['username'] = name
            session.parameter = True
            session['Side_number']= result[3]
            session['time_start'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            return redirect(url_for("index"))
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
                sql = 'insert into UserInformation (User_ID, User_name, Password,Side_number_now)''values(?,?,?)'
                data = (userID,username,password1,6)
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

##check if the ARduino connect
@app.route('/Connection_check',methods = ['GET','POST'])
def Connection_check():
    userID = request.form.get('Arduino_ID')
    Side_number = request.form.get('Side_number')
    cur = db.cursor()
    cur.execute('select * from UserInformation where User_ID =?',[userID])
    result=cur.fetchone()
    if result == None:
        return('Please register your User information!')
    else:
        c = (Side_number,userID)
        sql = 'update Userinformation set Side_number_now = ? where User_ID = ?'
        cur.execute(sql,c)
        db.commit()
        return ('Successfully change the side of tube!')

## main page of website
@app.route('/',methods = ['GET','POST'])
def index():
        Username = session.get('username')
        ID = session.get('userID')
        cur1 = db.cursor()
        cur1.execute('select * from Userinformation where User_ID =?',[ID])
        result1 = cur1.fetchone()
        session['Side_number_now'] = result1[3]
        session['Sum_time'] = 0
        print(session.get('Side_number_now'),session.get('Side+number'))
        if session.get('Side_number_now')==6:
            flash('Please connect to your monitor and refresh the page!')
            return render_template('index.html',Side_number = 'Off working now!',Task_name='',Activity_time='',Actyvity_type='',Sum_hour=0,Sum_min=0,Sum_second=0)
        else:
            if session.get('Side_number') ==session.get('Side_number_now'):
                print(session.get('Side_number'))
                session['time_start'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                cur2 = db.cursor()
                cur2.execute('select * from task where  User_ID =? and Side_number = ?',[ID,session.get('Side_number')])
                result2 = cur2.fetchone()
                print(result2)
                if result2 == None:
                    flash('Please enter a new task!')
                    db.commit()
                    return render_template('index.html',Side_number = session.get('Side_number'),Task_name='',Activity_time='',Actyvity_type='',Sum_hour=0,Sum_min=0,Sum_second=0)
                else:
                    Task_name= result2[2]
                    Activity_time = result2[3]
                    Activity_type= result2[4]
                    session['Sum_time'] = result2[5]
                    print(session.get('Sum_time'))
                    Sum_hour = int(session.get('Sum_time')/60/60)  ##hours
                    Sum_min = int(session.get('Sum_time')/60)-Sum_hour*60   ## minutes
                    Sum_second = session.get('Sum_time') - Sum_hour*60*60-Sum_min*60  ##seconds
                    print(session.get('Side_number'),Task_name, Activity_time, Activity_type,session.get('Sum_time'))
                    return render_template('index.html',Side_number = session.get('Side_number'),Task_name=Task_name,Activity_time=Activity_time,Actyvity_type=Activity_type,Sum_hour=Sum_hour,Sum_min=Sum_min,Sum_second=Sum_second)
            else:
                session['Side_number'] = session.get('Side_number_now')
                Sum_timeNew = 0   ### start calculate the last task's sum time
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
                cur3 = db.cursor()
                cur3.execute('update task set Activity_time=? where User_ID=? and Side_number=?',(Activity_time,ID,session.get('Side_number')))
                cur3.execute('update task set Sum_time=? where User_ID=? and Side_number=?',(Sum_timeNew,ID,session.get('Side_number')))
                db.commit()
                return render_template('index.html')
        
@app.route('/endTask',methods = ['GET','POST'])
def endTask():
    if request.method == "GET":
        ID = session.get('userID')
        Side_num = session.get('Side_number')
        cur1 = db.cursor()
        c1 = ('end',ID,Side_num)
        print(c1)
        sql = 'update task set Activity_type=? where User_ID=? and Side_number=?'
        cur1.execute(sql,c1)
        db.commit()
        cur2 = db.cursor()
        c2 = (7,ID,Side_num)
        print(c2)
        sql = 'update task set Side_number=? where User_ID=? and Side_number=?'
        cur2.execute(sql,c2)
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
        cur1 = db.cursor()
        sql ='select * from task where User_ID=? and Side_number=?'
        cur1.execute(sql,(User_ID,Side_numChange))
        if cur1.fetchone() == None and Side_numChange != 6:
            sql = 'update task set Side_number=? where User_Id=? and Task_name=?'
            c = (Side_numChange,User_ID,Task_name)
            print(c)
            cur2 = db.cursor()
            cur2.execute(sql,c)
            db.commit()
            flash ('Successfully changed the side number !')
            return redirect(url_for('index'))
        elif cur1.fetchone() != None and Side_numChange != 6:
            flash('This side of tube already got a task! Please change another side!')
            return render_template('upgradeSide_number.html')
        elif Side_numChange == 6:
            flash('This side is off work side! PLease choose another one!')
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
        cur1 = db.cursor()
        sql ='select * from task where User_ID=? and Task_name=?'
        cur1.execute(sql,(User_ID,Task_nameChange))
        if cur1.fetchone() == None:
            if Task_nameChange == None:
                flash('Please enter new task name!')
                return render_template('upgradeTaskname.html')
            else:
                sql = 'update task set Task_name=? where User_Id=? and Side_number=?'
                c = (Task_nameChange,User_ID,Side_number)
                print(c)
                cur2 = db.cursor()
                cur2.execute(sql,c)
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
            cur = db.cursor()
            cur.execute('update task set Activity_time=? where User_ID=? and Side_number=?',(Activity_time,ID,Side_number))
            cur.execute('update task set Sum_time=? where User_ID=? and Side_number=?',(Sum_timeNew,ID,Side_number))
            db.commit()
            session.clear()
            return redirect(url_for('login'))  


if __name__ == 'main':
    app.run(debug = True, host='0.0.0.0', port=5000)
    db.close()