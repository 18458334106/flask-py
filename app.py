import random
from flask import Flask
from flask_cors import CORS
from utils.entity import r
from api.users import users_bp
import requests
# from api.message.message import user_message_bp
# from api.examples.examples import examples_bp
from api.chat import socketio,chat_bp
from utils.swagger import Swagger
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
from utils.sql import supabase

# 创建 Flask 实例
app = Flask(__name__)
app.register_blueprint(users_bp)
# app.register_blueprint(user_message_bp)
app.register_blueprint(chat_bp)
# app.register_blueprint(examples_bp)

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
            'id': 'job1',
            'func': '__main__:sql_task',  # 方法名
            'trigger': 'interval',  # interval表示循环任务
            # 'days': 1
            'seconds': 10
        }
    ]

phonesArr = [
	'19928282288',
	'15907570757',
	'19927777772',
	'13929131914',
	'15918141319',
	'13211191413',
	'13433191319',
	'19928282228',
	'15918186668',
	'19927777770',
	'19927777727',
	'18718718718',
	'13433143931',
	'19928282868',
	'13929193149',
	'15975755666',
	'18823497888',
	'13924541319',
	'13929191431',
	'15916191413',
	'13433141941',
	'13433191913',
	'13433141419',
	'13433144113',
	'15918191413',
	'13433139493',
	'13534349431',
	'19924131314',
	'13392241319',
	'18923149131',
	'13927729331',
	'13927729931',
	'13211141931',
	'13928254913',
	'13823491913',
	'13827772272',
	'18824899998',
	'13528991319',
	'13528914131',
	'18824899666'
]
def sql_task():
    url = 'https://api.yesmax.com.cn/api/Send/phoneSend'
    index = int(random.random() * 10)
    print(index,phonesArr[index])
    # res = requests.post(url,{ 'phone': phonesArr[index] })
    res = requests.post(url,{ 'phone': '18458334106' })
    print(res.content)
    return
    # res = supabase.table('user').select("*").execute().data
    # print(111)

app.config.from_object(Config())

if __name__ == '__main__':
    # app.run(debug=True)
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    socketio.run(app,debug=True,host='0.0.0.0',port=5001,allow_unsafe_werkzeug=True)