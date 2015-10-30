# -*- coding: utf-8 -*-
""" 程序入口
"""
from flask import Flask

import config
import extensions


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    extensions.init_app(app)
    return app
