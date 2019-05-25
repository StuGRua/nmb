from flask import Flask,request,render_template,redirect,url_for,session,jsonify
import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import pymysql
import datetime
from forms import loginform,signinform
from errors import *
from enc import *
import time
from cookiemaker import *
from utilities import *
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@127.0.0.1:3306/nmb0"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='wtfwtf'
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=True)
    password = db.Column(db.String(40), nullable=True)
    email = db.Column(db.String(80), nullable=True, unique=True)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(256), nullable=True)
    kookies = db.Column(db.String(10),nullable=True,default='00000000')
    admin = db.Column(db.Boolean,default=False)
    confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.Integer,default=0)
    def __init__(self,username,password,email,password_hash,confirmed=False,kookies='00000000',admin=False,avatar=0):
        self.username = username
        self.password = password
        self.email = email
        self.password_hash = password_hash
        self.kookies = kookies
        self.admin = admin
        self.confirmed = confirmed
        self.avatar = avatar


def checklogin():
    if session.get('username') != None:
        return False
    return True
@app.route('/api/<kw>/')
def api(kw):
    if kw == 'timestamp':
        return str(int((time.time())))
    if kw == 'datetime':
        return str(datetime.datetime.now())
    return return404()

@app.route('/',methods=['GET','POST'])
def home():
    ip = request.remote_addr
    return render_template('home.html',userip = ip,datetime=datetime.datetime.now(),loginform=loginform(),signinform=signinform())
@app.route('/home',methods=['GET','POST'])
def homepage():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    username=session.get('username')
    result = User.query.filter(User.username == username).first()
    kookies=result.kookies
    avatar = result.avatar
    avatarhref = '\static/avatars/'+str(avatar)+'.png'
    return render_template('portal.html',username=username,kookies=kookies,avatarhref=avatarhref)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home',logout=1))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return return500()
    form = loginform()
    if form.validate_on_submit():
        username = form.name.data#其实是email
        password = form.password.data
        #print(username,password)
        result = User.query.filter(User.email==username).first()
        if result == None:
            return redirect(url_for('home',err=1))
        elif result.password == password:
            session['username']=result.username
            session['kookies']=result.kookies
            session['avatar']=result.avatar
            return redirect(url_for('homepage'))
        else:
            return redirect(url_for('home',err=1))
    else:
        return redirect(url_for('home',err=1))

@app.route('/signin',methods=['GET','POST'])
def signin():
    if request.method == 'GET':
        return return500()
    form = signinform()
    if form.validate_on_submit():
        username = form.name.data
        psw1 = form.password1.data
        psw2 = form.password2.data
        email = form.email.data
        print(username, psw1, email)
        if psw1 != psw2:
            print('密码与确认密码不同')
            return redirect(url_for('home',err=1))
        try:
            newuser = User(username=username,password=psw1,email=email,password_hash=md5(psw1),confirmed=False,admin=False)
            db.session.add(newuser)
            db.session.commit()
            session['username']=username
            return redirect(url_for('homepage'))
        except Exception as e:
            db.session.rollback()
            print(e)
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home',err=1))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)