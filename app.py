from flask import Flask
from flask_cors import CORS
from utils.entity import r
from api.users import users_bp
from api.chat import socketio,chat_bp
from api.hack import hack_bp
from utils.swagger import Swagger
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler

# 创建 Flask 实例
app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(hack_bp)

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

if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    socketio.run(app,debug=True,host='0.0.0.0',port=5001,allow_unsafe_werkzeug=True)