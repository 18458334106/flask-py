from utils.sql import supabase
from flask import Blueprint,request, session
from utils.entity import r
user_bp = Blueprint('user', __name__, url_prefix='/user')
# 设置 session 密钥
"""----------------------------------------
                API: 用户登录
-------------------------------------------"""
@user_bp.route('/login', methods=['POST'])
def user_login():
    reqJSONData = request.get_json(silent=True)

    if not reqJSONData: return r(code=401, msg='注册失败, 请求参数为空')
    username = reqJSONData.get('username')
    password = reqJSONData.get('password')

    if not all([username, password]):
        return r(code=401, msg='登录, 缺少请求参数')

    user = supabase.table('sys_user').select('*').eq('username',username).eq('password',password).execute().data
    # 4. 用户不存在, 直接返回
    if not user:
        return r(code=404, msg='用户名或密码错误')
    else:
        session['user_info'] = user
        return r(msg='登录成功', data=user)
@user_bp.route('/list', methods=['POST','get'])
def user_list():
    userInfo = session.get('user_info')
    if not userInfo:
        return r(msg='暂未登录')
    else:
        user = supabase.table('sys_user').select('*').execute().data
        return user
