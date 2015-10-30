# -*- coding: utf-8 -*-
""" 程序入口
"""
from flask import Flask

import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    return app
