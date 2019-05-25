from flask import Flask,request,render_template,redirect,url_for,session,jsonify
import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
import pymysql
import datetime
from forms import loginform,signinform,new_post_form,comment_form
from errors import *
from enc import *
import time
from cookiemaker import *
from utilities import *
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:aA_iul453_bB@127.0.0.1:3306/nmb0"
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

class posts(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True,unique=True)#主键，辨识
    poster = db.Column(db.String(10),nullable=True)#发布者的kookie
    head = db.Column(db.Boolean,default=False)#是否是第一条
    next = db.Column(db.Integer,nullable=True,default=0)#下一条
    post_time = db.Column(db.DateTime,nullable=True)#生成时间
    title = db.Column(db.Text,nullable=True)#标题
    content = db.Column(db.Text,nullable=True)#内容
    section = db.Column(db.String(40),nullable=True,default='main')#板块
    def __init__(self,poster,head,next,title,content,section='main'):
        self.poster = poster
        self.head = head
        self.next = next
        self.post_time=datetime.datetime.now()
        self.title = title
        self.content = content
        self.section = section


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
@app.route('/new',methods=['POST'])
def newpost():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    form = new_post_form()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        section = form.section.data
        print(title,content)
        post = posts(poster=session.get('kookie'),head=True,next=0,title=title,content=content,section=section)
        try:
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            #return redirect(url_for('home'))
            return return500()
        return redirect(url_for('homepage',postok=1))
    else:
        print('no validate====================')
        return return500()
@app.route('/comment/<post_id>',methods=['POST'])
def comment(post_id):
    print(post_id)#id:给【ID】这个串评论
    identifier = md5(str(time.time()))
    if checklogin():
        return redirect(url_for('home',nologin=1))
    form = comment_form()
    if form.validate_on_submit():
        content = form.content.data
        print(content)
        section = posts.query.filter(posts.id==post_id).first().section

        post = posts(poster=session.get('kookie'),head=False,next=0,title=identifier,content=content,section=section)
        try:
            db.session.add(post)
            db.session.commit()
            newid = posts.query.filter(posts.title==identifier).first().id
            next_id = posts.query.filter(posts.id==post_id).first().next
            while next_id != 0:
                temp = posts.query.filter(posts.id==next_id).first().next
                if temp == 0:
                    break;
                else:
                    next_id = temp
            if posts.query.filter(posts.id==post_id).first().next==0:
                next_id = post_id
            posts.query.filter(posts.id == next_id).update({'next': newid})
            try:
                db.session.commit()
                print('comment ok')
                return redirect(request.referrer)
            except Exception as e:
                db.session.rollback()
                print(e)
                return return500()
        except Exception as e:
            db.session.rollback()
            print(e)
            return return500()
    else:
        print('no validate====================')
        return return500()


    return 'ok'
@app.route('/viewpost/<id>',methods=['GET','POST'])
def viewpost(id):#id是headpost的主键
    form = comment_form()
    allposts = []
    next_id=0
    post = posts.query.filter(posts.id==id).first()
    if post == None:
        return return404()
    posterkookie = post.poster
    #posteravatar = User.query.filter(User.kookies == posterkookie).first().avatar
    allposts.append(post)#将一楼加至list
    next_id = post.next#每一楼的id
    while next_id !=0:
        nextpost = posts.query.filter(posts.id==next_id).first()
        allposts.append(nextpost)
        next_id = nextpost.next

    return render_template('viewpost.html',form=form,post=post,allposts=allposts,len_of_all_posts = len(allposts))


@app.route('/changeavatar/<avtid>',methods=['GET','POST'])
def changeavt(avtid):
    if checklogin():
        return redirect(url_for('home',nologin=1))
    account = session.get('account')
    result = User.query.filter(User.email == account).update({'avatar':avtid})
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return return500()
    return redirect(url_for('homepage'))
@app.route('/newkookie',methods=['GET','POST'])
def newkookie():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    username = session.get('username')
    account = session.get('account')
    kookie = cookie(username)
    result = User.query.filter(User.email == account).update({'kookies': kookie})
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return return500()
    return redirect(url_for('homepage'))


@app.route('/home',methods=['GET','POST'])
def homepage():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    username=session.get('username')
    result = User.query.filter(User.username == username).first()
    kookies=result.kookies
    avatar = result.avatar
    account = result.email
    session['account'] = account
    session['kookie'] = kookies
    avatarhref = '\static/avatars/'+str(avatar)+'.jpg'
    allposts = posts.query.filter(posts.head==True).order_by(-posts.post_time).all()
    return render_template('portal.html',username=username,kookies=kookies,\
                           avatarhref=avatarhref,account=account,newpostform=new_post_form(),\
                           allposts = allposts)
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
    app.run(host='0.0.0.0', port=6060,debug=True)