## docker+git发布版本

### 部署

- 迁出代码到本地
    `git clone xxx.git`

- 进入deploy目录安装fabric依赖
    `pip install -r requirement.txt`

- 根据实际情况修改fabfile.py文件， 然后运行
    `fab prepare`

- 之后要部署到staging只要执行
    `git push staging master`
