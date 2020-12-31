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
import urllib
from utilities import *
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://StuG:x74rtw05@localhost:3306/nmb0"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='wtfwtf'
visited_ip=[]
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=True)
    password = db.Column(db.String(40), nullable=True)
    email = db.Column(db.String(80), nullable=True, unique=True)
    create_time = db.Column(db.DateTime,nullable=True)#注册时间
    active_time = db.Column(db.DateTime,nullable=True)#上次活动时间
    active_ip = db.Column(db.String(50),nullable=True)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(256), nullable=True)
    password_cmp = db.Column(db.String(50),nullable=True)#用于登陆时比对
    kookies = db.Column(db.String(10),nullable=True,default='00000000')
    admin = db.Column(db.Boolean,default=False)
    confirmed = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.Integer,default=0)
    oldkookies = db.Column(db.Text,nullable=True)
    fav_color = db.Column(db.String(10),nullable=True,default='000000')#用的是RGB标识
    cited = db.Column(db.Text,nullable=True)
    def __init__(self,username,password,email,active_ip,password_hash,confirmed=False,kookies='00000000',admin=False,avatar=0,fav_color='000000',cited=''):
        self.username = username
        self.password = password
        self.email = email
        self.create_time = datetime.datetime.now()
        self.active_time = datetime.datetime.now()
        self.active_ip = active_ip
        self.password_hash = password_hash
        self.password_cmp = md5(password)
        self.kookies = kookies
        self.admin = admin
        self.confirmed = confirmed
        self.avatar = avatar
        self.oldkookies = '#'
        self.fav_color = fav_color
        self.cited = cited
#待增加验证登陆时专门的密码验证加密方式，前端向后端发起ajax请求，后端返回salt，前端加密提交数据与后端比对
class posts(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True,unique=True)#主键，辨识
    poster = db.Column(db.String(10),nullable=True)#发布者的kookie
    poster_ip = db.Column(db.String(50),nullable=True)
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
    topped = db.Column(db.Boolean,default=False)
    update_time = db.Column(db.DateTime,nullable=True)#最后更新时间，由reply控制更新
    no_show = db.Column(db.Boolean,nullable=True)#是否展示在时间线上
    def __init__(self,poster,poster_ip,head,next,title,content,section='main',withpic=False,pic_route='null',replies=0,topped=False,update_time=datetime.datetime.now(),no_show=False):
        self.poster = poster
        self.poster_ip = poster_ip
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
        self.topped = topped
        self.update_time = datetime.datetime.now()
        self.no_show = no_show
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
def checkip(ip):
    with urllib.request.urlopen('http://ip.ws.126.net/ipquery?ip='+ip) as f:
        data = f.read()
        data = data.decode('gbk')
        #print('Status:', f.status, f.reason)
        #for k, v in f.getheaders():
            #print('%s: %s' % (k, v))
        print('Data:', data)
        #print(type(data))
        #start = data.find('city:"')
        #coma = data.find(',')
        #print(data[start:coma],'123123')
    return data
@app.route('/api/<kw>')
def api(kw):
    #print(kw)
    if kw == 'timestamp':
        return str(int((time.time())))
    if kw == 'datetime':
        return str(datetime.datetime.now())
    if kw == 'harmony':
        return render_template('test/index.html')
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
    if kw== 'visited_ip':
        result = []
        for ip in visited_ip:
            result.append(str('ip:'+ip+checkip(ip)))
        return str(result)
    if kw == 'power_fee':
        room_id = request.values.get('id')
        print(room_id)
        return getfee(room_id)
    return return404()

@app.route('/',methods=['GET','POST'])
def home():
    nologin = request.values.get('nologin')
    if request.remote_addr not in visited_ip:
        visited_ip.append(request.remote_addr)
    topped_posts = posts.query.filter(posts.topped==True).order_by(-posts.update_time).all()
    tenposts = posts.query.filter(posts.head==True).filter(posts.topped==False).filter(posts.no_show==False).order_by(-posts.update_time).all()
    return render_template('view/portal.html',topped_posts = topped_posts,tenposts=tenposts,userip = request.remote_addr,datetime=datetime.datetime.now(),\
        loginform=loginform(),signinform=signinform(),nologin=str(nologin))

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
        content = form.content.data.replace('\n','<br>')
        section = form.section.data
        show_post = form.no_show.data
        if show_post == '1':
            no_show = False
        if show_post == '0':
            no_show = True
        pic = request.files.get('pic')
        if pic != None:#先判断图的后缀是不是要的
            picname = pic.filename.split('.')
            suffix = picname[-1].lower().strip()
            if not (suffix=='gif' or suffix=='jpg' or suffix=='png' or suffix == 'jpeg'):
                #print('weeeeeeeeee')
                pic = None#图不对就不要
        if pic != None:#有图
            post = posts(poster=session.get('kookie'),poster_ip=request.remote_addr,head=True,next=0,title=title,content=content,section=section,withpic=True,no_show=no_show)
            try:
                db.session.add(post)
                db.session.commit()
                ider = posts.query.filter(posts.ider==md5(content+str(int(time.time())))).first().id
                try:
                    #print(ider,'we have pic here')
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
            #print('没图')
            post = posts(poster=session.get('kookie'),poster_ip=request.remote_addr,head=True,next=0,title=title,content=content,section=section,withpic=False,no_show=no_show)
            try:
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('homepage',postok=1))
            except Exception as e:
                db.session.rollback()
                print(e)
                #return redirect(url_for('home'))
                return return500('db error')
    else:
        #print('no validate====================')
        return return500('no validate')
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
        content = form.content.data.replace('\n','<br>')
        pic = request.files.get('pic')
        cited_id = parse_cited(content)
        if cited_id != None:#把引用的id替换成链接
            content = content.replace(str('>>>'+cited_id+'|||'),str('<a href=\"/viewpost/'+cited_id+'\">'+'>'+cited_id+'|'+'</a>'))
        if pic != None:#先判断图的后缀是不是要的
            picname = pic.filename.split('.')
            #print(picname)
            suffix = picname[-1].lower().strip()
            #print(suffix)
            if not (suffix=='gif' or suffix=='jpg' or suffix=='png' or suffix == 'jpeg'):
                #print('weeeeeeeeee')
                pic = None#图不对就不要
        if pic !=None:
            #print('we have pic')
            section = posts.query.filter(posts.id==post_id).first().section
            post = posts(poster=session.get('kookie'),poster_ip=request.remote_addr,head=False,next=0,title=identifier,content=content,section=section,withpic=True,update_time=datetime.datetime.now())
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
                posts.query.filter(posts.id == post_id).update({'update_time':datetime.datetime.now()})#更新时间
                try:
                    db.session.commit()
                    #print('comment ok')
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    return return500()
                #print('=============================')
                ider = posts.query.filter(posts.ider==md5(content+str(int(time.time())))).first().id
                #print('----------------------',ider)
                try:
                    #print(ider,'we have pic here')
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
            post = posts(poster=session.get('kookie'),poster_ip=request.remote_addr,head=False,next=0,title=identifier,content=content,section=section,withpic=False,update_time=datetime.datetime.now())
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
                posts.query.filter(posts.id == post_id).update({'update_time':datetime.datetime.now()})#更新时间
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
        return return500('no validate')


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
    allposts.append(post)#将一楼加至list
    next_id = post.next#每一楼的id
    while next_id !=0:
        nextpost = posts.query.filter(posts.id==next_id).first()
        allposts.append(nextpost)
        next_id = nextpost.next
    return render_template('view/viewpost.html',form=form,post=post,allposts=allposts,len_of_all_posts = len(allposts),result=result,loginform=loginform(),signinform=signinform())
@app.route('/delpost/<id>',methods=['GET','POST'])
def delpost(id):
    if checklogin():
        return redirect(url_for('home',nologin=1))
    account = session.get('account')
    this_user = User.query.filter(User.email==account).first()
    this_post = posts.query.filter(posts.id==id).first()
    poster_kookie = this_post.poster
    if this_user.kookies == poster_kookie or this_user.admin == True:
        next_id = this_post.next#找出指向的下一个postid
        if this_post.head == True:#是头就把头移除了，等效于整体移除
            db.session.delete(this_post)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
                return return500(str(e))
            return redirect(url_for('homepage',deleteok=1))
        else:
            last_post = posts.query.filter(posts.next==id).first().id#找出上一个指向该post的id
            db.session.delete(this_post)
            posts.query.filter(posts.id==last_post).update({'next':next_id})
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
                return return500(e)
            return redirect(request.referrer)
    else:
        return return500('无权限进行本操作')


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
    if request.remote_addr not in visited_ip:
        visited_ip.append(request.remote_addr)
    if checklogin():
        return redirect(url_for('home',nologin=1))
    nokookie=None
    email=session.get('account')
    topped_posts = posts.query.filter(posts.topped==True).order_by(-posts.update_time).all()
    result = User.query.filter(User.email == email).first()
    if result==None:
        return redirect(url_for('home',nologin=1))
    session['kookie'] = result.kookies
    if result.kookies == '00000000':
        nokookie=1
    allposts = posts.query.filter(posts.head==True).filter(posts.topped==False).filter(posts.no_show==False).order_by(-posts.post_time).all()
    return render_template('view/home.html',result=result,newpostform=new_post_form(),\
                           allposts = allposts,topped_posts=topped_posts,section='时间线',no_confirmation=request.values.get('no_confirmation'),nokookie = nokookie)

@app.route('/gg',methods=['GET','POST'])
def gg():
    return render_template('view/gg.html')


@app.route('/section/<section_name>',methods=['GET','POST'])
def viewsection(section_name):
    if checklogin():
        return redirect(url_for('home',nologin=1))
    email=session.get('account')
    result = User.query.filter(User.email == email).first()
    if result==None:
        return redirect(url_for('home',nologin=1))
    relposts = posts.query.filter(posts.section == section_name).filter(posts.head==True).order_by(-posts.update_time).all()
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
        print(email,password)
        result = User.query.filter(User.email==email).first()#唯一辨识符
        if result == None:
            return redirect(url_for('home',err=1))
        elif result.password == password:
            session['account']=result.email
            session['kookies']=result.kookies
            session['avatar']=result.avatar
            active_ip=request.remote_addr
            User.query.filter(User.email==email).update({'active_ip':active_ip})
            try:
                db.session.commit()
            except Exception as e:
                print(e)
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
            newuser = User(username=username,password=psw1,email=email,active_ip=request.remote_addr,password_hash=md5(psw1),confirmed=False,admin=False)
            db.session.add(newuser)
            db.session.commit()
            session['account']=email
            session['kookies']='00000000'
            psw_hash = User.query.filter(User.email==email).first().password_hash
            if not psw_hash:
                return return500('psw_hash is None')
            try:
                sender(email,'localhost:6060/api/confirmation?code='+psw_hash)
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
    app.run(host='localhost', debug=True ,port=6060,threaded=True)