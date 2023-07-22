from flask import Flask, request, session
from typing import List
from utils.mysql import db
from api.user.user import User
from utils.utils import model_list_to_dict  # 自定义的 utils 工具包
import pymysql
from utils.entity import r

# 创建 Flask 实例
app = Flask(__name__)

"""----------------------------------------
                初始化 Flask 
-------------------------------------------"""
# 初始化数据库
pymysql.install_as_MySQLdb()
# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:123456@localhost:3306/flaskPy"
# 解决中文乱码
app.config['JSON_AS_ASCII'] = False
# 关闭
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 设置 session 密钥
app.config['SECRET_KEY'] = 'I LIKE U'
# 初始化数据库
db.init_app(app)


"""----------------------------------------
                API: 初始化
-------------------------------------------"""
@app.route('/', methods=['GET'])
def hello():
    return r(code=200, msg='服务器访问成功!')

"""----------------------------------------
                API: 用户登录
-------------------------------------------"""
@app.route('/login', methods=['POST'])
def user_login():
    reqJSONData = request.get_json(silent=True)  # 允许 请求体的 raw 为空
    # 1. 处理请求参数为空
    if not reqJSONData: return r(code=401, msg='注册失败, 请求参数为空')
    username = reqJSONData.get('username')
    password = reqJSONData.get('password')

    # 2. 处理请求参数缺少
    if not all([username, password]):
        return r(code=401, msg='登录, 缺少请求参数')
    # 3. 验证账号和密码
    user = User.query.filter_by(name=username,password=password).first()
    # 4. 用户不存在, 直接返回
    if not user:
        return r(code=404, msg='用户名或密码错误')
    else:
        # 5. 保存用户状态到 session
        session['user_info'] = user.dict()
        return r(msg='登录成功', data=user.dict())

if __name__ == '__main__':
    app.run()

