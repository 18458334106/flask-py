from utils.sql import supabase
from flask import Blueprint,request
from utils.entity import r
from flask_jwt_extended import jwt_required,get_jwt_identity
user_message_bp = Blueprint('user_message', __name__, url_prefix='/user_message')
@user_message_bp.route('/get_messageList', methods=['GET'])
def getMessageList():
    """获取用户留言列表
        ---
        tags:
          - user_message
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
    result = supabase.table('user_message').select('*').execute()
    return r(code=200,msg='获取成功', data=result.data)

@user_message_bp.route('/add_message', methods=['GET'])
@jwt_required()
def addMessage():
    """添加用户留言
        ---
        tags:
          - user_message
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
        result = supabase.table('user_message').insert({"message":message,"username":userInfo.get('name')}).execute()
        return r(code=200,msg='添加成功')

@user_message_bp.route('/del_message', methods=['GET'])
@jwt_required()
def delMessage():
    """删除用户留言
        ---
        tags:
          - user_message
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
    result = supabase.table('user_message').delete().eq("id",messageId).execute()
    return  r(code=200,msg='删除成功')