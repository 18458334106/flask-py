from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
user_bp = Blueprint('user', __name__, url_prefix='/user')
@user_bp.route('/login', methods=['POST'])
def user_login():
    """用户登录
    ---
      tags:
          -  user
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
    loginForm = request.get_json(silent=True)
    if not all([loginForm.get('username'), loginForm.get('password')]):
        return r(code=401, msg='请输入正确的账号密码')
    user = (supabase.table('sys_user')
            .select('id,username,name')
            .eq('username',loginForm.get('username'))
            .eq('password',loginForm.get('password'))
            .execute()).data
    if not user:
        return r(code=401, msg='账号或密码错误')
    else:
        return r(code=200, data={'token':create_access_token(identity=user[0])},msg='登录成功')

@user_bp.route('/info', methods=['GET'])
@jwt_required()
def user_info():
    """获取用户信息
        ---
        tags:
          -  user
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
    userInfo = get_jwt_identity()
    if not userInfo:
        return r(msg='暂未登录')
    else:
        return r(msg='success',data=userInfo,code=200)

@user_bp.route('/list', methods=['GET'])
@jwt_required()
def user_list():
    """获取用户列表
    ---
    tags:
      -  user
    consumes:
      - multipart/form-data
    parameters:
      - name: Authorization
        in: header
        required: true
        description: 用户token
        type: string
      - name: username
        in: path
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
    userInfo = get_jwt_identity()
    if not userInfo:
        return r(msg='暂未登录')
    else:
        sql = supabase.table('sys_user').select('*')
        username = request.args.get('username')
        if username: sql.eq('username',username)
        user = sql.execute().data
        return r(msg='success',data=user,code=200)

@user_bp.route('/register', methods=['POST'])
def user_register():
    """用户注册
        ---
          tags:
              -  user
          consumes:
              - application/json
          parameters:
            - name: userForm
              in: body
              type: object
              required: true
              description: 用户注册
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
                  example: {"msg":"注册成功", "code":200}
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
    user_register = request.get_json(silent=True)
    if not all([user_register.get('username'),user_register.get('password')]):
        return r(code=401, msg='缺少账号或密码')
    else:
        res = (supabase.from_('sys_user').select('*')
                .eq('username', user_register.get('username'))
                .execute()).data
        if res:
            return r(code=401, msg='账号已被注册')
        else:
            user_register['name'] = user_register.get('username')
            sql = supabase.from_('sys_user').insert(user_register)
            res = sql.execute().data
            if res:
                return r(code=200, msg='注册成功')
            else:
                return r(code=401, msg='注册失败')