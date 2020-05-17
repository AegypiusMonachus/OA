from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

import decimal, datetime, time
def alchemyencoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
