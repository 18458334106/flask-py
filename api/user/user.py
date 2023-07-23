from utils.mysql import db

"""--------------------------------------
            定义 MySQL 用户的映射类
-----------------------------------------"""

class User(db.Model):
    __tablename__ = "sys_user"
    id = db.Column(db.Integer, name='id', primary_key=True)
    name = db.Column(db.String, name='username', unique=True)
    password = db.Column(db.String, name='password')

    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password
        }
