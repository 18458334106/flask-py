from flask import Flask
from flask_cors import CORS
from utils.entity import r

from api.user.user import user_bp
# 创建 Flask 实例
app = Flask(__name__)
app.register_blueprint(user_bp)

CORS(app, supports_credentials=True,resources=r'/*')

@app.route('/', methods=['GET'])
def hello():
    return r(code=200, msg='服务器访问成功!')

if __name__ == '__main__':
    app.run()