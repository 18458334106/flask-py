from utils.sql import supabase
from flask import Blueprint,request, session
from utils.entity import r
from flask_jwt_extended import jwt_required
import os
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

@user_message_bp.route('/upload', methods=['POST'])
def upload():
    """上传文件保存至本地
        ---
        tags:
          - upload
        consumes:
          - multipart/form-data
        parameters:
            - name: file
              required: false
              in: formData
              type: file
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
    file = request.files['file']
    if file:
        filename = file.filename
        # 获取当前工作目录
        current_dir = os.getcwd()
        # 拼接文件保存的路径
        save_path = os.path.join(current_dir, 'uploads', filename)
        # 保存文件
        file.save(save_path)
        return r(code=200,msg='上传成功', data={'filename': filename})