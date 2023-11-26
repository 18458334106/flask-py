from flask import jsonify
"""
    前后端交互响应类
"""
class r(dict):
    def __init__(self, code=200, msg=None, data=None):
        super().__init__(code=code, msg=msg, data=data)

    def jsonify(self):
        return jsonify(self)
