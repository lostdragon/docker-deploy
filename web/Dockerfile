FROM index.alauda.cn/library/python:2.7

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --allow-external --no-cache-dir -i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com -r requirements.txt
