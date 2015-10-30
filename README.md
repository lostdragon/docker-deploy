## docker+git发布版本

### 开发

- 本地安装docker和docker-compose
- 本地环境`docker-compose -f development.yml up -d`
- 容器带ssh,可以用帐号root密码password进入容器

### 部署

- 迁出代码到本地
    `git clone xxx.git`

- 进入deploy目录安装fabric依赖
    `pip install -r requirement.txt`

- 根据实际情况修改fabfile.py文件， 然后运行
    `fab prepare`

- 之后要部署到staging只要执行
    `git push staging master`
