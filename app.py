from flask import Flask
from flask_cors import CORS
from utils.entity import r
from api.user.user import user_bp
from api.message.message import user_message_bp
from api.examples.examples import examples_bp
from api.socketio.socketio import socketio,socket_bp
from utils.swagger import Swagger
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
from utils.sql import supabase

# 创建 Flask 实例
app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(user_message_bp)
app.register_blueprint(socket_bp)
app.register_blueprint(examples_bp)

CORS(app, supports_credentials=True,resources=r'/*')
app.config['JWT_SECRET_KEY'] = 'focusInYou' #jwt密钥 可自定义
jwt = JWTManager(app) #实例化
Swagger(app)
socketio.init_app(app,cors_allowed_origins="*")
@app.route('/', methods=['GET'])
def hello():
    return r(code=200, msg='服务器访问成功!')

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return r(code=401, msg='过期的token')

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return r(code=401, msg='无效token')

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return r(code=401, msg='您还未登陆')

class Config(object):  # 创建配置，用类
    # 任务列表
    JOBS = [
        {  # 第二个任务，每隔5S执行一次
            'id': 'job2',
            'func': '__main__:sql_task',  # 方法名
            'trigger': 'interval',  # interval表示循环任务
            'days': 1
        }
    ]


def sql_task():
    res = supabase.table('user').select("*").execute().data
    print(res)

app.config.from_object(Config())

if __name__ == '__main__':
    # app.run(debug=True)
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    socketio.run(app,debug=True,host='0.0.0.0',port=5001,allow_unsafe_werkzeug=True)