from utils.sql import supabase
from flask import Blueprint,request, session
from utils.entity import r
from flask_jwt_extended import jwt_required
user_message_bp = Blueprint('user_message', __name__, url_prefix='/user_message')

@user_message_bp.route('/get_messageList', methods=['GET'])
def getMessageList():
    result = supabase.table('user_message').select('*').execute()
    return r(msg='获取成功', data=result.data)