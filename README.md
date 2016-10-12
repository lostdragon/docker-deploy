## docker+git发布版本

### 开发

- 本地安装docker和docker-compose
- 本地环境`docker-compose -f development.yml up -d`
- 容器带ssh,可以用帐号root密码password进入容器

### 部署

- 迁出代码到本地
    `git clone git@git.coding.net:lostdragon/docker-deploy.git`

- 本机安装fabric依赖
     `pip install fabric`

- 在deploy目录根据实际情况修改fabfile.py文件， 然后运行
    `fab prepare`  # 如果一台服务器部署多个分支,默认只部署第一个分支
    如果需要指定角色/分支可以加参数 
    `fab prepare:roles=staging`

- 之后要部署到主机别名为vagrant的staging只要执行
    `git push vagrant staging`

- 在deploy目录回滚到上次发布
    `fab rollback`
    
### 重启说明

重启是发HUP信号给容器,容器会自动发给容器内第一个进程,如果容器内的进程不支持HUP信号或者运行多个进程则需要用supervisor管理: 

- 目前用到几个支持HUP信号进程:
  `uwsgi supervisor nginx` 
  
- redis忽略HUP信号

### python项目依赖
- 依赖放在项目home目录和代码一起提交,部署到服务器时不需要再更新镜像.

### 目录说明

        + deploy  部署目录
            - fabfile.py  fab部署脚本
            - requirements.txt  部署依赖文件
        + dev  开发docker镜像构建目录
            - Dockerfile  docker镜像构建文件
        + home  python模块安装目录
        + nginx  nginx配置目录

        + web  应用目录
        - .gitignore  git忽略文件
        - development.yml  开发环境docker compose部署文件
        - README.md  当前说明文件
        - staging.yml  仿真环境docker compose部署文件
        - testing.yml  测试环境docker compose部署文件
