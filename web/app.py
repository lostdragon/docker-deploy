# -*- coding: utf-8 -*-

from factory import create_app

app = create_app()


@app.route('/')
def index():
    return 'ok, i am master'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
