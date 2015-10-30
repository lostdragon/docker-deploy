# -*- coding: utf-8 -*-

from playhouse.flask_utils import FlaskDB

db = FlaskDB()


def init_app(app):
    db.init_app(app)
