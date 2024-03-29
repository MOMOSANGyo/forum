import datetime
import time

from flask import Blueprint, render_template, sessions, session, Response, request, redirect, current_app, url_for
from .VerfiCode import VerfiCode
from App.model import *
import hashlib
import re,os

bbs=Blueprint('bbs',__name__)

# @bbs.before_request
# def is_login():
#     if request.path.rstrip('/')=='/':
#         return
#     elif not session.get('username'):
#         return redirect(url_for('index'))

# @bbs.route('/')
# def index():
#     return render_template('index.html')

allowlogin={}
allownum=0

@bbs.route('/')
@bbs.route('/<int:cid>')
@bbs.route('/<int:cid>/<int:xid>')#php技术交流/程序人生
def index (cid=0,xid=0):


    name=request.args.get('username')
    mm=request.args.get('password')
    user=User.query.filter(User.username==name).all()

    md5_obj = hashlib.md5()
    md5_obj.update(str(mm).encode('utf-8'))
    passwd = md5_obj.hexdigest()
    num = db.session.query(Detail_t).count()
    nnum = Detail_t.query.filter(Detail_t.classid==xid).count()
    person =db.session.query(User).count()
    newperson =User.query.order_by(-User.uid).first()
    n_time=str(datetime.datetime.now()).split(' ')[0]
    ttime=0
    detail=Detail_t.query.filter(Detail_t.classid==xid).all()
    if len(detail):
        for d in detail:
            if str(d.addtime) ==n_time:
                ttime=ttime+1

    banzhu = User.query.filter(User.uid==5).first()


    allBK = Category.query.filter(Category.parentid == 0).all()

    if passwd:
        if len(user)!=0:
            localname=user[0].username
            global allownum
            # allowlogin[localname] = allownum
            last=str(user[0].lasttime).split(' ')[0]
            if user[0].allowlogin == 1:
                return render_template('notice3.html', **{
                    'allBk': allBK
                })
            if user[0].password==passwd:
                allownum=0
                allowlogin[localname]=allownum
                if last!=n_time:
                    user[0].grade=user[0].grade+2
                    db.session.add(user[0])
                    db.session.commit()
                session['username'] = name
                session['picture'] = user[0].picture
                session['grade'] = user[0].grade
                session['udertype'] =user[0].udertype
                user[0].lasttime =datetime.datetime.now()
                db.session.add(user[0])
                db.session.commit()
            else:
                if allowlogin.get(localname):
                    allownum+=1
                    allowlogin[localname]=allownum
                else:
                    allownum=1
                    allowlogin[localname]=allownum
                a=user[0].regip
                print(a,type(a))
                if allownum==3:
                    c = Closeip(
                        ip=a,
                        addtime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    db.session.add(c)
                    db.session.commit()
                    user[0].allowlogin=1
                    db.session.add(user[0])
                    db.session.commit()




    post=Detail_t.query.all()
    user1=User.query.all()


    if xid == 0:
        if cid == 0:
            bz = Category.query.filter(Category.parentid == cid).all()
        else:
            bz = Category.query.filter(Category.cid == cid).all()
        # 所有大版块
        # allBk = Category.query.filter(Category.parentid == 0).all()
        # 小版块
        smallbz = Category.query.filter(Category.parentid != 0).all()
        return render_template('index.html', **{
            'category': bz,
            'allBk': allBK,
            'smalls': smallbz,
            'iid':cid,
            'id':xid,
            'ppost':post,
            'user1':user1,
            'num':num,
            'person':person,
            'newperson':newperson,
            'nnum':nnum,
            'ttime':ttime,
            'banzhu':banzhu
        })
    else :

        # allBK = Category.query.filter(Category.parentid == 0).all()
        smallbz = Category.query.filter(Category.parentid != 0).all()
        BK = Category.query.filter(Category.parentid == cid).all() #allBK
        data = Category.query.filter(Category.cid==xid).all()
        # for n in range(3):
        #     print(allBK[n].classname)
        list=[]
        for ank in allBK:
            if ank.cid == cid:
                list.append(ank)
                for ak in smallbz:
                    if ak.cid == xid:
                        list.append(ak)
        return render_template('index.html',**{
            'allBk': allBK,
            'smalls': smallbz,
            'bk':BK,
            'da':data,
            'iid':cid,
            'id':xid,
            'li':list,
            'ppost': post,
            'user1':user1,
            'num':num,
            'person':person,
            'newperson':newperson,
            'nnum':nnum,
            'ttime':ttime,
            'banzhu':banzhu
        })


@bbs.route('/quit')
def quit():
    session['username']=''
    return redirect('/')

@bbs.route('/yzm')
def yzm():

    vc= VerfiCode()
    res = vc.output()
    session['yzm']=vc.code
    response = Response()
    response.status_code = 200
    response.headers['content-type']='image/jpeg'
    response.data = res
    return response


@bbs.route('/register')
def zhuce():
    allBK = Category.query.filter(Category.parentid == 0).all()

    return render_template('zhuce.html',**{
                    'allBk': allBK
                })


@bbs.route('/yanzheng',methods=['GET','POST'])
def yanzheng():
    name=request.form.get('username')
    mm = request.form.get('password')
    mn = request.form.get('repassword')

    md5_obj = hashlib.md5()
    md5_obj.update(str(mm).encode('utf-8'))
    passwd = md5_obj.hexdigest()


    email=request.form.get('mail')
    yzm=request.form.get('yzm')
    na=User.query.filter(User.username==str(name)).all()
    ml=re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',str(email))
    yz=session.get('yzm')
    ip=request.remote_addr

    list=[]
    if len(na)!=0:
        list.append("用户名重复")
    if len(str(name))<3 or len(str(name))>12:
        list.append('用户长度不符合要求')
    if re.match(r'^\d+$',str(mm)):
        list.append("密码格式不能为纯数字")
    if mm != mn:
        list.append("两次输入密码不一致")
    else:
        if len(str(mm))<3 or len(str(mm))>12:
            list.append('密码长度不符合要求')
    if not ml:
        list.append('邮箱格式错误')
    if yz!=yzm:
        list.append("验证码错误")
    length=len(list)
    if length==0 :
        user=User()
        user.username=name
        user.password=passwd
        user.email=email
        user.udertype=0
        user.grade=50
        user.regtime= datetime.datetime.now()
        user.lasttime = datetime.datetime.now()
        user.picture = "index/images/avatar_blank.gif"
        user.regip= str(ip)
        user.allowlogin = 0
        db.session.add(user)
        db.session.commit()
    session['zhuce']=1


    allBK = Category.query.filter(Category.parentid == 0).all()
    return render_template('notice.html',**{
        'li':list,
        'len':length,
        'allBk': allBK
    })






    # return render_template('zhuce.html')

@bbs.route('/getpass')
def getpass():
    allBK = Category.query.filter(Category.parentid == 0).all()
    return render_template('getpass.html',**{
                    'allBk': allBK
                })

@bbs.route('/reyanzheng',methods=['GET','POST'])
def reyanzheng():
    name=request.form.get('username')
    email=request.form.get('mail')
    na = User.query.filter(User.username == str(name)).all()
    yzm = request.form.get('yzm')
    yz = session.get('yzm')
    res = User.query.filter(User.username == str(name), User.email == str(email)).first()
    title = ""
    n=0
    if res:
        if yz ==yzm:
            title = "找回密码成功，已发送到您的邮箱"
            n=1
        else:
            title = '验证码输入错误'
    else:
        title = "查询不到用户信息，请查看输入是否有误"
        n=0
    allBK = Category.query.filter(Category.parentid == 0).all()
    return render_template('notice1.html',**{
        'speak':title,
        'num':n,
        'allBk': allBK
    })


@bbs.route('/sset/<ss>',methods=['GET','POST'])
def sset(ss=''):
    allBK = Category.query.filter(Category.parentid == 0).all()

    if ss == 'touxiang':
        user = User.query.filter(User.username == session['username']).first()
        # print(session['username'])
        if request.method == 'POST':
            # 获取文件上传对象
            obj = request.files.get('photo')
            if obj:
                # obj.filename 上传文件名
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], obj.filename)
                print(path)
                obj.save(path)
                user = User.query.filter(User.username == session['username']).first()
                # 相对于static的路径
                user.picture = "upload/" + obj.filename
                db.session.add(user)
                db.session.commit()
                # return "上传成功"
                session['picture'] = user.picture
                return render_template('sset.html', picture=user.picture,**{
                    'allBk': allBK
                })
            # return "上传失败"
            return render_template('sset.html', picture=user.picture,**{
                    'allBk': allBK
                })
        # user = User.query.filter(User.username == session['username']).first()


        return render_template('sset.html', picture=user.picture,ss='touxiang',**{
                    'allBk': allBK
                })
        # return render_template("sset.html",ss='touxiang')
    if ss=='ziliao':
        year =request.form.get('birthyear')
        month =year =request.form.get('birthmonth')
        day =year =request.form.get('birthday')
        user = User.query.filter(User.username == session['username']).first()
        user.realname=request.form.get('realname')
        user.sex=request.form.get('sex')
        user.place=request.form.get('place')
        user.qq=request.form.get('qq')
        user.birthday=str(year)+str(month)+str(day)
        db.session.add(user)
        db.session.commit()
        return render_template('sset.html',ss="ziliao",**{
                    'allBk': allBK
                })

    if ss == 'qianming':
        qm=request.form.get('content')
        user = User.query.filter(User.username == session['username']).first()
        user.autograph=qm
        db.session.add(user)
        db.session.commit()
        return render_template("sset.html",ss='qianming',**{
                    'allBk': allBK
                })
    if ss == 'anquan':
        return render_template('sset.html',ss='anquan',**{
                    'allBk': allBK
                })

@bbs.route('/rereyanzheng',methods=['GET','POST'])
def rereyanzheng():
    old = request.form.get('oldpassword')
    user = User.query.filter(User.username == session['username']).first()
    mm = request.form.get('newpassword')
    mn = request.form.get('newpassword2')
    email = request.form.get('emailnew')
    problem = request.form.get('questionidnew')
    answer = request.form.get('answernew')
    ml = re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', str(email))

    md5_obj = hashlib.md5()
    md5_obj.update(str(old).encode('utf-8'))
    passwd = md5_obj.hexdigest()

    list = []
    if passwd != user.password:
        list.append("旧密码验证失败")
    if mm != mn:
        list.append("两次密码输入不一致")
    if not ml:
        list.append("邮箱格式错误")

    if mm:

        if re.match(r'^\d+$',str(mm)):
            list.append("密码格式不能为纯数字")
    else:
        mm=old

    length = len(list)
    allBK = Category.query.filter(Category.parentid == 0).all()
    if length == 0:
        md5_obj = hashlib.md5()
        md5_obj.update(str(mm).encode('utf-8'))
        passw = md5_obj.hexdigest()

        user.password = passw
        user.email = email
        user.problem = problem
        user.result = answer

        db.session.add(user)
        db.session.commit()
        return redirect('/sset/anquan')
    else:
        return render_template('notice2.html', **{
            'len': length,
            'li': list,
            'allBk': allBK
        })

@bbs.route('/fatie/<int:cid>/<int:xid>',methods=['GET','POST'])
def fatie(cid,xid):
    # cid 大板块id
    # xid 小板块id
    if session.get('username'):
        allBK = Category.query.filter(Category.parentid == 0).all()
        dbk = Category.query.filter(Category.cid == cid).first()
        xbk = Category.query.filter(Category.cid == xid).first()

        return render_template('fatie.html',**{
            'allBk': allBK,
            'dbk':dbk,
            'xbk':xbk
                    })
    else:
        return redirect('/')
@bbs.route('/p_post/<int:cid>/<int:xid>',methods=['GET','POST'])
def p_post(cid,xid):
    allBK = Category.query.filter(Category.parentid == 0).all()
    dbk = Category.query.filter(Category.cid == cid).first()
    xbk = Category.query.filter(Category.cid == xid).first()
    subject = request.form.get('subject')
    content = request.form.get('content')
    user = User.query.filter(User.username == session['username']).first()
    d = Detail_t(
        authorid=user.uid,
        title=subject,
        content=content,
        addtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0],
        addip=user.regip,
        classid=xbk.cid,
        replycount=0,
        hits=0,
        isdel=0,
        ishot=0
    )
    user.grade=user.grade+2
    session['grade']=session['grade']+2
    db.session.add(user)
    db.session.commit()
    db.session.add(d)
    db.session.commit()
    dd=Detail_t.query.order_by(-Detail_t.id).first().id
    return redirect('/huitie/{}/{}/{}'.format(dbk.cid,xbk.cid,dd))
    # return render_template('tiezi.html',**{
    #     'allBk': allBK,
    #     'dbk':dbk,
    #     'xbk':xbk,
    #     'dd':dd
    #             })
    # return redirect('/fatie/{}/{}'.format(dbk.cid,xbk.cid)) #改成帖子内部
#
# @bbs.route('/tiezi/<int:cid>/<int:xid>/<int:id>')
# def tiezi(cid,xid,id):
#     # cid:大板块id
#     # xid:小板块id
#     # id:帖子id
#     allBK = Category.query.filter(Category.parentid == 0).all()
#     dbk = Category.query.filter(Category.cid == cid).first()
#     xbk = Category.query.filter(Category.cid == xid).first()
#     # tie = Detail_t.query.filter(Detail_t.id == id).first()
#     # user = User.query.filter(User.uid==tie.authorid).first()
#     return redirect('/huitie/')
#     return render_template('tiezi.html',**{
#         'allBk': allBK,
#         'dbk':dbk,
#         'xbk':xbk
#         # 'tie':tie,
#         # 'user':user
#                 })

@bbs.route('/huitie/<int:cid>/<int:xid>/<int:id>',methods=['GET','POST'])
def huitie(cid,xid,id,pingid=0):

    if session.get('username'):

        allBK = Category.query.filter(Category.parentid == 0).all()
        dbk = Category.query.filter(Category.cid == cid).first()
        xbk = Category.query.filter(Category.cid == xid).first()
        tie = Detail_t.query.filter(Detail_t.id == id).first()
        #当前回帖的帖子id 所属的板块id
        user = User.query.filter(User.username==session['username']).first()
        #回帖人

        reply = request.form.get('message')
        if reply:
            if tie.replycount+1:
                tie.replycount=int( tie.replycount)+1
                d=Detail_h(
                    tid =id,
                    authorid=user.uid,
                    content=reply,
                    addtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                    isdisplay=0
                )

                db.session.add(d)
                db.session.commit()


        louid = Detail_t.query.filter(Detail_t.id==id).first()
        louzhu=User.query.filter(User.uid==louid.authorid).first()

        # huifu=Detail_h.query.all()
        tie.hits = tie.hits+1
        db.session.add(tie)
        db.session.commit()

        dd = Detail_h.query.filter(Detail_h.tid==id).all()
        uuser =User.query.all()

        return render_template('tiezi.html',**{
            'allBk': allBK,
            'dbk':dbk,
            'xbk':xbk,
            'tie':tie,
            'dd':dd,
            'user':louzhu,
            'uuser':uuser
                    })
    else:
        return redirect('/')


