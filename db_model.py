from datetime import datetime
from . import db

# generates database column functions
id_column = lambda **kwargs: db.Column(db.Integer, primary_key=True,
                                       **kwargs)
str_column = lambda length, **kwargs: db.Column(db.String(length=length, **kwargs))
timestamp_column = lambda **kwargs: db.Column(db.DateTime,
                                              default=datetime.utcnow, index=True, **kwargs)


class MessageTable(db.Model):
    id = id_column()
    body = str_column(200)
    name = str_column(30)
    timestamp = timestamp_column()
