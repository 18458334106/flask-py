from utils.sql import supabase
from flask import Blueprint
from utils.entity import r
examples_bp = Blueprint('examples', __name__, url_prefix='/examples')

@examples_bp.route('/list')
def getList():
    """获取examples列表
        ---
        tags:
          - examples
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
    res = supabase.table('examples').select("*").execute().data
    return r(code=200,data=res)
