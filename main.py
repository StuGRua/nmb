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
from mail_sender import *
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
    create_time = db.Column(db.DateTime,nullable=True)#注册时间
    active_time = db.Column(db.DateTime,nullable=True)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(256), nullable=True)
    password_cmp = db.Column(db.String(50),nullable=True)#用于登陆时比对
    kookies = db.Column(db.String(10),nullable=True,default='00000000')
    admin = db.Column(db.Boolean,default=False)
    confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.Integer,default=0)
    oldkookies = db.Column(db.Text,nullable=True)
    fav_color = db.Column(db.String(10),nullable=True,default='000000')#用的是RGB标识
    def __init__(self,username,password,email,password_hash,confirmed=False,kookies='00000000',admin=False,avatar=0,fav_color='000000'):
        self.username = username
        self.password = password
        self.email = email
        self.create_time = datetime.datetime.now()
        self.active_time = datetime.datetime.now()
        self.password_hash = password_hash
        self.password_cmp = md5(password)
        self.kookies = kookies
        self.admin = admin
        self.confirmed = confirmed
        self.avatar = avatar
        self.oldkookies = '#'
        self.fav_color = fav_color
#待增加验证登陆时专门的密码验证加密方式，前端向后端发起ajax请求，后端返回salt，前端加密提交数据与后端比对
#待增加注册时间记录
#增加fav_color
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
    avatar = db.Column(db.Integer,default=0)
    withpic = db.Column(db.Boolean,default=False)
    pic_route = db.Column(db.String(100),nullable=True)
    ider = db.Column(db.String(256),nullable=True)#唯一识别符，用来反查主键
    replies = db.Column(db.Integer,nullable=True)#head=True的post的回复数，回复+=1
    def __init__(self,poster,head,next,title,content,section='main',withpic=False,pic_route='null',replies=0):
        self.poster = poster
        self.head = head
        self.next = next
        self.avatar = User.query.filter(User.kookies==poster).first().avatar
        self.post_time=datetime.datetime.now()
        self.title = title
        self.content = content
        self.section = section
        self.withpic = withpic
        self.pic_route = pic_route
        self.ider = md5(content+str(int(time.time())))
        self.replies = replies
#增加replies属性，用于head=True的统计

def checklogin():
    if session.get('account') != None:
        return False#已登陆
    return True#未登陆
def checkkookie():
    email = session.get('account')
    if User.query.filter(User.email==email).first().kookies != '00000000':
        return False#已有有效kookie
    return True#没有有效kookie
def check_confirmation():
    email = session.get('account')
    if User.query.filter(User.email == email).first().confirmed == True:
        return False#y已通过验证
    return True#未通过验证

@app.route('/api/<kw>')
def api(kw):
    print(kw)
    if kw == 'timestamp':
        return str(int((time.time())))
    if kw == 'datetime':
        return str(datetime.datetime.now())
    if kw == 'confirmation':
        psw_pash = request.values.get('code')#现在确认码是密码HASH
        User.query.filter(User.password_hash==psw_pash).update({'confirmed':True})
        try:
            db.session.commit()
            return redirect(url_for('home',confirmation_ok=1))
        except Exception as e:
            db.session.rollback()
            print(e)
            return return500('邮件验证失败')
    return return404()

@app.route('/',methods=['GET','POST'])
def home():
    nologin = request.values.get('nologin')
    tenposts = posts.query.filter(posts.head==True).order_by(-posts.post_time).all()
    return render_template('view/portal.html',tenposts=tenposts,userip = request.remote_addr,datetime=datetime.datetime.now(),\
        loginform=loginform(),signinform=signinform(),nologin=str(nologin))
'''
def getpic():
    pic = request.files.get('pic')
    if pic != None:#先检查文件类型
        suffix = pic.filename.split('.')[-1]
        if suffix != 'jpg' or 'png' or 'gif':
            return 0
        picname'''
@app.route('/new',methods=['POST'])
def newpost():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    if checkkookie():
        return redirect(url_for('homepage',nokookie=1))
    if check_confirmation():
        return redirect(url_for('homepage',no_confirmation=1))
    form = new_post_form()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        section = form.section.data
        pic = request.files.get('pic')
        if pic != None:#先判断图的后缀是不是要的
            picname = pic.filename.split('.')
            suffix = picname[-1].lower().strip()
            if not (suffix=='gif' or suffix=='jpg' or suffix=='png'):
                print('weeeeeeeeee')
                pic = None#图不对就不要
        if pic != None:#有图
            post = posts(poster=session.get('kookie'),head=True,next=0,title=title,content=content,section=section,withpic=True)
            try:
                db.session.add(post)
                db.session.commit()
                ider = posts.query.filter(posts.ider==md5(content+str(int(time.time())))).first().id
                try:
                    print(ider,'we have pic here')
                    suffix = pic.filename.split('.')[-1]
                    route = 'static/uploads/'+str(ider)+'.'+suffix
                    pic.save(route) #图片名就是POST ID
                    try:
                        posts.query.filter(posts.id == ider).update({'pic_route':route})
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        return return500('保存图片路径或保存图时出错')
                    #print('file saved', filename)
                except Exception as e:
                    print(e)
                return redirect(url_for('homepage',postok=1))
            except Exception as e:
                db.session.rollback()
                print(e)
                #return redirect(url_for('home'))
                return return500()
        else:#没图
            print('没图')
            post = posts(poster=session.get('kookie'),head=True,next=0,title=title,content=content,section=section,withpic=False)
            try:
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('homepage',postok=1))
            except Exception as e:
                db.session.rollback()
                print(e)
                #return redirect(url_for('home'))
                return return500()
    else:
        print('no validate====================')
        return return500()
@app.route('/comment/<post_id>',methods=['POST'])
def comment(post_id):
    #print(post_id)#id:给【ID】这个串评论
    identifier = md5(str(time.time()))
    if checklogin():
        return redirect(url_for('home',nologin=1))
    if checkkookie():
        return redirect(url_for('homepage',nokookie=1))
    if check_confirmation():
        return redirect(url_for('homepage',no_confirmation=1))
    form = comment_form()
    if form.validate_on_submit():
        content = form.content.data
        pic = request.files.get('pic')
        if pic != None:#先判断图的后缀是不是要的
            picname = pic.filename.split('.')
            print(picname)
            suffix = picname[-1].lower().strip()
            print(suffix)
            if not (suffix=='gif' or suffix=='jpg' or suffix=='png'):
                print('weeeeeeeeee')
                pic = None#图不对就不要
        if pic !=None:
            print('we have pic')
            section = posts.query.filter(posts.id==post_id).first().section
            post = posts(poster=session.get('kookie'),head=False,next=0,title=identifier,content=content,section=section,withpic=True)
            try:
                db.session.add(post)
                db.session.commit()
                newid = posts.query.filter(posts.title==identifier).first().id
                next_id = posts.query.filter(posts.id==post_id).first().next
                while next_id != 0:
                    temp = posts.query.filter(posts.id==next_id).first().next
                    if temp == 0:
                        break
                    else:
                        next_id = temp
                if posts.query.filter(posts.id==post_id).first().next==0:
                    next_id = post_id
                posts.query.filter(posts.id == next_id).update({'next': newid})
                replies = posts.query.filter(posts.id==post_id).first().replies+1#增加回复数
                posts.query.filter(posts.id == post_id).update({'replies':replies})
                try:
                    db.session.commit()
                    print('comment ok')
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    return return500()
                print('=============================')
                ider = posts.query.filter(posts.ider==md5(content+str(int(time.time())))).first().id
                print('----------------------',ider)
                try:
                    print(ider,'we have pic here')
                    suffix = pic.filename.split('.')[-1]
                    route = 'static/uploads/'+str(ider)+'.'+suffix
                    pic.save(route) #图片名就是POST ID
                    try:
                        posts.query.filter(posts.id == ider).update({'pic_route':route})
                        db.session.commit()    
                    except Exception as e:
                        print(e)
                        return return500('保存图片路径或保存图时出错')
                    #print('file saved', filename)
                except Exception as e:
                    print(e)
                    return redirect(request.referrer)
            except Exception as e:
                db.session.rollback()
                print(e)
                return return500()
        else:
            section = posts.query.filter(posts.id==post_id).first().section
            post = posts(poster=session.get('kookie'),head=False,next=0,title=identifier,content=content,section=section,withpic=False)
            try:
                db.session.add(post)
                db.session.commit()
                newid = posts.query.filter(posts.title==identifier).first().id
                next_id = posts.query.filter(posts.id==post_id).first().next
                while next_id != 0:
                    temp = posts.query.filter(posts.id==next_id).first().next
                    if temp == 0:
                        break
                    else:
                        next_id = temp
                if posts.query.filter(posts.id==post_id).first().next==0:
                    next_id = post_id
                posts.query.filter(posts.id == next_id).update({'next': newid})
                replies = posts.query.filter(posts.id==post_id).first().replies+1#增加回复数
                posts.query.filter(posts.id == post_id).update({'replies':replies})
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


    return redirect(request.referrer)
@app.route('/viewpost/<id>',methods=['GET','POST'])
def viewpost(id):#id是headpost的主键
    form = comment_form()
    allposts = []
    next_id=0
    result=User.query.filter(User.email==session.get('account')).first()
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

    return render_template('view/viewpost.html',form=form,post=post,allposts=allposts,len_of_all_posts = len(allposts),result=result,loginform=loginform(),signinform=signinform())


@app.route('/changeavatar/<avtid>',methods=['GET','POST'])
def changeavt(avtid):
    if checklogin():
        return redirect(url_for('home',nologin=1))
    if check_confirmation():
        return redirect(url_for('homepage',no_confirmation=1))
    account = session.get('account')
    kookie = User.query.filter(User.email==account).first().kookies
    User.query.filter(User.email == account).update({'avatar':avtid})
    try:
        db.session.commit()
        try:
            posts.query.filter(posts.poster==kookie).update({'avatar':avtid})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return return500()
    except Exception as e:
        db.session.rollback()
        print(e)
        return return500()
    return redirect(url_for('homepage'))
@app.route('/newkookie',methods=['GET','POST'])
def newkookie():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    if check_confirmation():
        return redirect(url_for('homepage',no_confirmation=1))
    account = session.get('account')
    kookie = cookie(User.query.filter(User.email==account).first().username)
    result = User.query.filter(User.email == account).update({'kookies': kookie})
    try:
        db.session.commit()
        try:
            oldkookie = str(User.query.filter(User.email==account).first().oldkookies)
            oldkookie += (kookie+'-')
            User.query.filter(User.email==account).update({'oldkookies':oldkookie})#保存历史kookie
            db.session.commit()
            session['kookie'] = kookie#s设置新kookie
        except Exception as e:
            db.session.rollback()
            print(e)
            return return500()
    except Exception as e:
        db.session.rollback()
        print(e)
        return return500()
    return redirect(request.referrer)


@app.route('/home',methods=['GET','POST'])
def homepage():
    if checklogin():
        return redirect(url_for('home',nologin=1))
    email=session.get('account')
    result = User.query.filter(User.email == email).first()
    if result==None:
        return redirect(url_for('home',nologin=1))
    session['kookie'] = result.kookies
    allposts = posts.query.filter(posts.head==True).order_by(-posts.post_time).all()
    return render_template('view/home.html',result=result,newpostform=new_post_form(),\
                           allposts = allposts,section='时间线')


@app.route('/section/<section_name>',methods=['GET','POST'])
def viewsection(section_name):
    if checklogin():
        return redirect(url_for('home',nologin=1))
    email=session.get('account')
    result = User.query.filter(User.email == email).first()
    if result==None:
        return redirect(url_for('home',nologin=1))
    relposts = posts.query.filter(posts.section == section_name).filter(posts.head==True).order_by(-posts.post_time).all()
    return render_template('view/home.html',result=result,newpostform=new_post_form(),\
                           allposts = relposts,section=section_name)


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
        email = form.name.data#其实是email
        password = form.password.data
        #print(username,password)
        result = User.query.filter(User.email==email).first()#唯一辨识符
        if result == None:
            return redirect(url_for('home',err=1))
        elif result.password == password:
            session['account']=result.email
            session['kookies']=result.kookies
            session['avatar']=result.avatar
            return redirect(url_for('homepage'))
        else:
            return redirect(url_for('home',err=1))
    else:
        return redirect(url_for('home',novalidation=1))

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
        #print(username, psw1, email)
        if psw1 != psw2:
            print('密码与确认密码不同')
            return redirect(url_for('home',err=1))
        try:
            newuser = User(username=username,password=psw1,email=email,password_hash=md5(psw1),confirmed=False,admin=False)
            db.session.add(newuser)
            db.session.commit()
            session['account']=email
            session['kookies']='00000000'
            psw_hash = User.query.filter(User.email==email).first().password_hash
            if not psw_hash:
                return return500('psw_hash is None') 
            try:
                sender(email,'http://www.ftmagic.xyz:6060/api/confirmation?code='+psw_hash)
            except Exception as e:
                print(e)
                return return500('邮件发送失败')
            return redirect(url_for('homepage'))
        except Exception as e:
            db.session.rollback()
            print(e)
            return redirect(url_for('home',signin_error=1))
    else:
        return redirect(url_for('home',novalidation=1))


if __name__ == '__main__':
    #db.drop_all()
    db.create_all()
    app.run(host='0.0.0.0', port=6060,debug=True)