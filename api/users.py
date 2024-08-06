from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
import aiohttp,base64
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from io import BytesIO
from PIL import Image
from utils.utils import img_simi
from chaojiying import Chaojiying_Client

users_bp:Blueprint = Blueprint('users', __name__, url_prefix='/users')
@users_bp.route('/login', methods=['POST'])
def login():
    """用户登录
        ---
          tags:
              -  用户
          consumes:
              - application/json
          parameters:
            - name: loginForm
              in: body
              type: object
              required: true
              description: 账号密码
              schema:
                properties:
                  username:
                    type: string
                  password:
                    type: string
          requestBody:
            description: body
            required: true
            content:
              application/json:
                schema:
                  example: {"token":TOKEN}
          responses:
            200:
              description: 成功
              schema:
                properties:
                  code:
                    type: integer
                  msg:
                    type: string
                  data:
                    type: object
            401:
              description: 失败
    """
    args = request.get_json()
    sql = supabase.table('users').select('*')
    responses = (sql.eq('username', args['username'])
                 .eq('password', args['password'])).execute()
    data = responses.data or None
    if data == None:
        return r('401', '用户名或密码错误')
    else:
        return r('200', '登录成功', create_access_token(identity=data[0]))

@users_bp.route('/register', methods=['POST'])
def register():
    """用户注册
        ---
          tags:
              -  用户
          consumes:
              - application/json
          parameters:
            - name: loginForm
              in: body
              type: object
              required: true
              description: 账号密码
              schema:
                properties:
                  username:
                    type: string
                  password:
                    type: string
          requestBody:
            description: body
            required: true
            content:
              application/json:
                schema:
                  example: {"token":TOKEN}
          responses:
            200:
              description: 成功
              schema:
                properties:
                  code:
                    type: integer
                  msg:
                    type: string
                  data:
                    type: object
            401:
              description: 失败
    """
    args = request.get_json()
    responses = supabase.table('users').select('*').eq('username', args['username']).execute()
    data = responses.data or None
    if data:
        return r('401', '账号已存在')
    else:
        args['nickname'] = args['username']
        sql = supabase.table('users').insert(args).execute()
        return r('200', '注册成功', args)

@users_bp.route('/list',methods=['GET'])
@jwt_required()
def list():
    """获取用户列表
    ---
    tags:
      -  用户
    consumes:
      - multipart/form-data
    parameters:
      - name: Authorization
        in: header
        required: true
        description: 用户token
        type: string
      - name: username
        in: path,query
        required: false
        description: 用户名
        type: string
    responses:
      200:
        description: 成功
        schema:
          properties:
            code:
              type: integer
            msg:
              type: string
            data:
              type: object
      401:
        description: 失败
    """
    args = request.args.to_dict()
    sql = supabase.table('users').select('*')
    if args:
        for key in args:
            if key and args[key]: sql = sql.eq(key,args[key])
    responses = sql.execute()
    return r(code=200,data=responses.data)

@users_bp.route('/info',methods=['GET'])
@jwt_required()
def info():
    """获取用户信息
    ---
    tags:
      -  用户
    consumes:
      - multipart/form-data
    parameters:
      - name: Authorization
        in: header
        required: true
        description: 用户token
        type: string
    responses:
      200:
        description: 成功
        schema:
          properties:
            code:
              type: integer
            msg:
              type: string
            data:
              type: object
      401:
        description: 失败
    """
    return r(msg='获取用户信息成功', data=get_jwt_identity(), code=200)

@users_bp.route('/sendMsg',methods=['GET'])
async def sendMsg():
    """发送短信验证码
    ---
    tags:
      -  用户
    consumes:
      - multipart/form-data
    parameters:
      - name: phone
        in: path,query
        required: true
        description: 手机号
        type: string
    responses:
      200:
        description: 成功
        schema:
          properties:
            code:
              type: integer
            msg:
              type: string
            data:
              type: object
      401:
        description: 失败
    """
    phone = request.args.to_dict().get('phone')
    sql = supabase.table('users').select('*').execute()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64, verify_ssl=False)) as session:
        async with session.post('https://webapi.kangruijk.com/admin/sys/sysadmin/sendMsgCode',data={
            'userPhone': phone
        }) as resp:
            async with session.get('http://154.12.30.80:90/randIp.php') as resp1:
                return r(code=200, data={
                    'resp': await resp.text(),
                    'resp1': await resp1.text(),
                })
        # async with session.get('http://154.12.30.80:90/send2.php') as resp:
        #     async with session.post('https://ai.applet.taxplus.cn/Api/sendCode.html',data={'phone':phone}) as resp1:
        #         async with session.post('https://ai.taxplus.cn/send/register_send.html',data={'phone':phone}) as resp2:
        #             return r(code=200, data={
        #                 'resp': await resp.text(),
        #                 'resp1': await resp1.text(),
        #                 'resp2': await resp2.text()
        #             })


# pkmmwvplgnmiebgg
@users_bp.route('/sendEmailMsg',methods=['GET'])
def sendEmailMsg():
    """发送邮箱验证码
    ---
    tags:
      -  用户
    consumes:
      - multipart/form-data
    parameters:
      - name: email
        in: path,query
        required: true
        description: 邮箱
        type: string
    responses:
      200:
        description: 成功
        schema:
          properties:
            code:
              type: integer
            msg:
              type: string
            data:
              type: object
      401:
        description: 失败
    """
    email = request.args.to_dict().get('email')
    sql = supabase.table('users').select('*').execute()
    # 创建 SMTP 对象
    smtp = smtplib.SMTP()
    # 发件人邮箱地址
    sendAddress = '2418671097@qq.com'
    # 发件人授权码
    password = 'pkmmwvplgnmiebgg'
    # 连接服务器
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)

    # 登录邮箱
    loginResult = server.login(sendAddress, password)

    # 构造MIMEText对象，参数为：正文，MIME的subtype，编码方式
    message = MIMEText('atukoon 邮件发送测试...', 'plain', 'utf-8')
    message['From'] = Header("Your Father <2418671097@qq.com>")  # 发件人的昵称 用英文不报错
    message['To'] = Header(f'Son <{email}>')  # 收件人的昵称  用英文不报错
    message['Subject'] = Header('你妈死了，臭婊子', 'utf-8')  # 定义主题内容

    server.sendmail('2418671097@qq.com', email, message.as_string())
    return r(code=200, msg='success', data=None)

@users_bp.route('/sendMsgAuto',methods=['GET'])
async def sendMsgAuto():
    """发送短信验证码
    ---
    tags:
      -  用户
    consumes:
      - multipart/form-data
    parameters:
      - name: phone
        in: path,query
        required: true
        description: 手机号
        type: string
    responses:
      200:
        description: 成功
        schema:
          properties:
            code:
              type: integer
            msg:
              type: string
            data:
              type: object
      401:
        description: 失败
    """
    phone = request.args.to_dict().get('phone')
    sql = supabase.table('users').select('*').execute()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64, verify_ssl=False)) as session:
        async with session.get('https://ai.app.taxplus.cn/api/getParams') as resp:
            data = await resp.json()
            result = data['data']
            # 去除base64数据的前缀
            prefix, data = result['img'].split(',', 1)
            # 解码base64数据
            decoded_data = base64.b64decode(data)
            # 使用BytesIO将字节数据转为文件对象
            image_file = BytesIO(decoded_data)
            # 使用PIL创建图片
            image = Image.open(image_file)
            bg = image.crop([0, 0, 340, 190])
            bg.save('bg.png')
            target = image.crop([4, 196, 56, 246])
            target.save('target.png')
            chaojiying = Chaojiying_Client('18458334106', 'Zhaojc2002@', '961726')
            im = open('bg.png', 'rb').read()
            re = chaojiying.PostPic(im, 9101)
            value = int(re['pic_str'].split(',')[0]) - 25
            async with session.post('https://ai.app.taxplus.cn/Api/sendCode.html',data={
                'value': value,
                'key': result['key'],
                'phone': phone
            }) as resp1:
                ddd = await resp1.json()
                code = ddd['data']['code']
                return r(code=200,data=code,msg='success')
