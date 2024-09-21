from flask import Blueprint
from utils.entity import r
import requests

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