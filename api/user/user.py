from utils.sql import supabase
from flask import Blueprint,request, session
from utils.entity import r
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
user_bp = Blueprint('user', __name__, url_prefix='/user')
@user_bp.route('/login', methods=['POST'])
def user_login():
    """用户登陆
    ---
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
    reqJSONData = request.get_json(silent=True)
    print(reqJSONData)
    if not reqJSONData: return r(code=401, msg='请输入正确的账号密码')
    username = reqJSONData.get('username')
    password = reqJSONData.get('password')

    if not all([username, password]):
        return r(code=401, msg='请输入正确的账号密码')

    user = supabase.table('sys_user').select('username,password').eq('username',username).eq('password',password).execute().data
    # 4. 用户不存在, 直接返回
    if not user:
        return r(code=404, msg='账号或密码错误')
    else:
        access_token = create_access_token(identity=user[0])  # 创建token
        session['user_info'] = user
        return r(msg='登录成功', data={'token': access_token})

@user_bp.route('/info', methods=['GET'])
@jwt_required()
def user_info():
    """获取用户信息
        ---
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
    return r(msg='',data={"username":userInfo['username'],"name":userInfo['name'],"id":userInfo['id']})

@user_bp.route('/list', methods=['GET'])
@jwt_required()
def user_list():
    """获取用户列表
    ---
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
        user = supabase.table('sys_user').select('*').execute().data
        return user