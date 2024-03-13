from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import jwt_required,get_jwt_identity
user_message_bp = Blueprint('message', __name__, url_prefix='/message')
@user_message_bp.route('/list', methods=['GET'])
def getList():
    """获取用户留言列表
        ---
        tags:
          - message
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
    result = supabase.table('message').select('*').execute()
    return r(code=200, data=result.data)

@user_message_bp.route('/add', methods=['GET'])
@jwt_required()
def addMessage():
    """添加用户留言
        ---
        tags:
          - message
        parameters:
          - name: Authorization
            in: header
            required: true
            description: 用户token
            type: string
          - name: message
            in: path
            required: true
            description: 用户留言
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
        message = request.args.get('message')
        result = supabase.table('message').insert({"message":message,"username":userInfo.get('name'),"userId":userInfo.get('id')}).execute()
        return r(code=200,msg='添加成功')

@user_message_bp.route('/del', methods=['GET'])
@jwt_required()
def delMessage():
    """删除用户留言
        ---
        tags:
          - message
        parameters:
          - name: Authorization
            in: header
            required: true
            description: 用户token
            type: string
          - name: id
            in: path
            required: true
            description: 留言id
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
    messageId = request.args.get('messageId')
    result = supabase.table('message').delete().eq("id",messageId).execute()
    return  r(code=200,msg='删除成功')