from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
from flask_apscheduler import APScheduler
import requests,aiohttp
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
    sql = supabase.table('user').select('*')
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
    sql = supabase.table('user').select('*')
    async with aiohttp.ClientSession() as session:
    #     async with session.get('http://154.12.30.80:90/send.php') as res:
    #         print(res.content,'res')
    #         async with session.get('http://154.12.30.80:90/send2.php') as resp:
    #             print(resp.content, 'resp')
        async with session.post('https://ai.applet.taxplus.cn/Api/sendCode.html',data={'phone':phone}) as resp1:
            print(resp1.content,'resp1')
            async with session.post('https://api.yesmax.com.cn/api/Send/phoneSend',data={'phone': phone}) as resp2:
                print(resp2.content, 'resp2')
                return r(code=200,data=None)