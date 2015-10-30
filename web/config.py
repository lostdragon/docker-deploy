# -*- coding: utf-8 -*-
import os

APP_MODE = os.getenv('APP_MODE', '')
APP_ROOT = os.path.abspath(os.path.dirname(__file__))

DATABASE = {
    'name': os.getenv('MYSQL_ENV_MYSQL_DATABASE', 'test'),
    'engine': 'MySQLDatabase',
    'user': os.getenv('MYSQL_ENV_MYSQL_USER', 'root'),
    'passwd': os.getenv('MYSQL_ENV_MYSQL_PASSWORD', os.getenv('MYSQL_ENV_MYSQL_ROOT_PASSWORD', '123456')),
    'host': os.getenv('MYSQL_PORT_3306_TCP_ADDR', '192.168.99.100'),
    'port': int(os.getenv('MYSQL_PORT_3306_TCP_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True,
    'use_unicode': True,
}
