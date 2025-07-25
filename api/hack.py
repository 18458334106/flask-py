from flask import Blueprint,request
from utils.entity import r
import requests
from utils.sql import supabase

hack_bp: Blueprint = Blueprint('hack', __name__, url_prefix='/hack')

import random, string
def generate_random_email(num_chars=10):
    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=num_chars))
    domain_name = 'example.com'
    return f"{random_name}@{domain_name}"

def generate_password():
    # 生成包含大小写字母的字符串
    letters = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))
    # 生成6位数字字符串
    digits = ''.join(str(random.randint(0, 9)) for _ in range(9))
    # 拼接字母和数字
    password = letters + digits
    # 打乱密码字符串，确保随机性
    return password

@hack_bp.route('/login',methods=['GET'])
def login():
    res = requests.post('https://ai.interface.taxplus101.com/Login/dologin',data={
        'name': generate_random_email(),
        'password': generate_password()
    },headers={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'referer': 'https://ai.taxplus101.com',
        'origin': 'https://ai.taxplus101.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    })
    return r(res.json())

@hack_bp.route('/loginCallback',methods=['POST'])
def loginCallback():
    """登录回调
        ---
          tags:
              -  用户
          consumes:
              - application/json
          parameters:
            - name: loginCallbackForm
              in: body
              type: object
              required: true
              schema:
                properties:
                  platform:
                    type: string
                  platform_user_id:
                    type: string
                  value:
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
    args = request.get_json()
    
    # 获取参数
    platform = args.get('platform')
    platform_user_id = args.get('platform_user_id')
    value = args.get('value')
    
    # 参数验证
    if not platform or not platform_user_id:
        return r(code=400, msg="platform 和 platform_user_id 不能为空")
    
    try:
        # 查询是否已存在该用户
        existing_user = supabase.table('hacker').select('*').eq('platform', platform).eq('platform_user_id', platform_user_id).execute()
        
        if existing_user.data:
            # 用户已存在，更新用户的 value 值
            update_result = supabase.table('hacker').update({'value': value}).eq('platform', platform).eq('platform_user_id', platform_user_id).execute()
            
            if update_result.data:
                return r(code=200, msg="用户信息已更新", data=update_result.data[0])
            else:
                return r(code=500, msg="用户信息更新失败")
        else:
            # 用户不存在，插入新用户
            new_user = {
                'platform': platform,
                'platform_user_id': platform_user_id,
                'value': value
            }
            
            insert_result = supabase.table('hacker').insert(new_user).execute()
            
            if insert_result.data:
                return r(code=200, msg="用户创建成功", data=insert_result.data[0])
            else:
                return r(code=500, msg="用户创建失败")
                
    except Exception as e:
        return r(code=500, msg=f"数据库操作失败: {str(e)}")