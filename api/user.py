from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
from flask_apscheduler import APScheduler

user_bp:Blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/login',methods=['POST'])
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
    username:str = args.get('username') or None
    password:str = args.get('password') or None
    sql = supabase.table('user').select('*')
    responses = (sql.eq('username',username)
           .eq('password',password)).execute()
    data = responses.data or None
    if data == None:
        return r('401','用户名或密码错误')
    else:
        return r('200','登录成功',create_access_token(identity=data[0]))

@user_bp.route('/list',methods=['GET'])
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

@user_bp.route('/info',methods=['GET'])
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
