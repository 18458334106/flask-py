from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
import aiohttp,base64
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import requests

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
        async with session.get('https://ai.app.taxplus.cn/api/getParams') as resp:
            result = await resp.json()
            key = result['data']['key']
            img = result['data']['img']
            async with session.post('http://slider-capture-crop.focusinyou.cn',data={
                "img": img
            }) as resp1:
                value = await resp1.text()
                return r(code=200,data=value)
            #     value = int(value['result']) - 25
            #     async with session.post('https://ai.app.taxplus.cn/Api/sendCode.html',data={
            #         "key":key,
            #         "value":value,
            #         "phone":phone
            #     }) as resp2:
            #         res = await resp2.json()
            #         code1 = res['data']['code']
                    # return r(code=200,data=code1)

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

@users_bp.route('/aaaa',methods=['GET'])
async def aaaa():
    res = requests.get('http://38.6.216.31:1234/1.php')
    return r(code=200,data=res.json())