# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
import time
import os
import sys
from fabric.colors import *

DEPLOY_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(DEPLOY_ROOT)
PROJECT_NAME = os.path.basename(PROJECT_ROOT)

# 取消默认-l参数
env.shell = "/bin/bash -c"

# 部署服务器ssh地址
env.hosts = [
    'root@192.168.33.104:22',
]

# 部署服务器ssh密码,建议用公钥认证
# env.passwords = {
#     'root@192.168.33.104:22': 'password',
# }

# 部署服务器角色定义
env.roledefs = {
    'staging': [env.hosts[0]],  # 角色名 ssh地址
    'testing': [env.hosts[0]],
}

# 部署角色对应git分支, 默认为master
branches = {
    'staging': 'staging',  # 角色名 分支名
    'testing': 'testing',
    'default': 'master',
}

# 部署服务器别名, 默认为角色名
aliases = {
    env.hosts[0]: 'vagrant',  # ssh地址 别名
}

# 角色域名配置用于检测服务是否启动成功
domain_configs = {
    'testing': {
        'domain': 'example.com',
        'prefix': 'api.',
        'port': 8080
    },
    'staging': {
        'domain': 'example.com',
        'prefix': 'api.',
        'port': 80
    },
}

data_root = '/data'  # 数据目录
git_root = '/data/gitroot'  # git仓库根目录
www_root = '/data/wwwroot'  # 网站根目录
log_root = '/data/logs'  # 日志根目录
app_root = '/data/approot'  # 应用根目录
docker_root = '/data/docker'  # docker数据目录

# 部署项目
projects = {
    PROJECT_NAME: {
        "local_path": PROJECT_ROOT,  # 本地地址
        "alive": '-H "Host: {prefix}{domain}" {host}:{port}',  # 检查状态
        "is_app": False,  # 是否app,默认false
        'roles': ['testing', 'staging'],  # 部署角色
    },
}

# ============ 以下不需要修改 ====================================

run_template = '''
    if [ -d "$app_dir" ]; then
        cd $app_dir
        unset GIT_DIR
        git checkout $branch -f
        git pull origin $branch
        if [ "$(docker-compose -f $branch.yml ps -q)" != "" ] ; then
            {run_service}
        else
            docker-compose -f $branch.yml up -d
        fi
    else
        echo "app_dir not exist,nothing to do"
    fi
'''

start_container = '''
            docker-compose -f $branch.yml stop
            docker-compose -f $branch.yml rm -f
            docker-compose -f $branch.yml up -d
'''

reload_container = '''
            docker-compose -f $branch.yml up -d
            docker-compose -f $branch.yml kill -s HUP
'''

pull_template = '''#!/bin/sh

while read oldrev newrev ref
do
    branch=`echo $ref | cut -d/ -f3`

    if [ "master" = "$branch" ]; then
        echo "master was pushed"
        app_dir={app_dir}
    else
        echo "$branch was pushed"
        app_dir="{app_dir}_$branch"
    fi

    %s

done
''' % run_template.format(run_service=reload_container)

first_run_template = '''#!/bin/sh
    app_dir="{app_dir}"
    branch="{branch}"
%s
''' % run_template.format(run_service=start_container)


def _get_domain():
    role = _get_current_role()
    if role in domain_configs.keys():
        return domain_configs[role]
    return domain_configs['default']


def _get_branch(role):
    if role in branches:
        return branches.get(role)
    else:
        return branches.get('default')


# # @task
# @parallel
def prepare():
    """
    开发环境准备： fab prepare:roles=staging
    生成环境准备： fab prepare:roles=production
    """
    check_docker()
    check_data_dir()
    check_app_git()
    add_local_git()
    push()
    check_app_dir()
    check_alive()


# # @task
@parallel
def deploy(project=None, role=None, is_check_service=True):
    # test(project)
    push(project, role)
    if is_check_service:
        check_alive()


# @task
@parallel
@roles('staging')
def s(project=None, is_reload=False):
    deploy_and_check(project=project, role=env.effective_roles[0], is_reload=is_reload)


# @task
@parallel
@roles('production')
def p(project=None, is_reload=False):
    deploy_and_check(project=project, role=env.effective_roles[0], is_reload=is_reload)


def deploy_and_check(project=None, is_reload=False, role=None):
    deploy(project=project, role=role if role else env.effective_roles[0],
           is_check_service=False if is_reload else True)
    if is_reload:
        reload_service(project)
        time.sleep(3)
        check_alive()


def install_docker():
    """
    安装docker
    :return:
    :rtype:
    """
    with settings(sudo_user="root", warn_only=True):
        # ubuntu 14.04
        result = sudo('dpkg -l | grep "linux-image-generic-lts-vivid"')
        if result.failed:
            print(blue("install linux-image-generic-lts-vivid, after this need to reboot, then rerun script"))

            if not confirm("Confirm?"):
                abort("Aborting at user request.")
            else:
                sudo('apt-get update -y && apt-get install -y linux-image-generic-lts-vivid')
                sudo('reboot')

            print(blue("after reboot, need to rerun the script"))
            sys.exit()

        result = sudo('dpkg -l | grep "docker-engine"')
        if result.failed:
            sudo('apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
            sudo(
                    ('echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" > '
                     '/etc/apt/sources.list.d/docker.list'))
            sudo('apt-get update -y && apt-get install -y docker-engine')

        mount_docker()


def mount_docker():
    """
    将docker数据存在数据分区
    :return:
    :rtype:
    """
    if sudo("test -d {dir}".format(dir=docker_root)).failed:
        sudo("mkdir -p {dir}".format(dir=docker_root))
        _check('rsync')
        sudo('service docker stop')
        sudo('rsync -aXS /var/lib/docker/.  /data/docker/')
        sudo('echo "/data/docker /var/lib/docker  none bind 0 0" >> /etc/fstab')
        sudo('mount –a')
        sudo('service docker start')


def _check(name):
    result = sudo("which {}".format(name))
    if result.failed:
        print("{name} not installed, try to install {name}".format(name=name))
        sudo("apt-get update -y && apt-get install -y {}".format(name))


def check_docker():
    check_user()
    # check is docker is installed
    with settings(sudo_user="git", warn_only=True):
        result = sudo("which docker")
        if result.failed:
            print("docker not installed, try to install docker")
            install_docker()

        result = sudo("docker info")
        if result.failed:
            who = sudo("whoami")
            # add user to docker group
            print("docker get version fail, add {who} user to docker group".format(who=who))
            with settings(sudo_user="root"):
                # not permission
                sudo("gpasswd -a git docker")
                # docker daemon down
                sudo("service docker restart")
    check_docker_compose()


def check_git():
    _check('git')


def check_user():
    """
    创建git用户用于发布
    :return:
    :rtype:
    """
    with settings(warn_only=True):
        # check git user is exist
        result = run("id -u git")
        if result.failed:
            # useradd git
            sudo("useradd -s /bin/bash -m git && gpasswd -a git docker")

        # check key is authorized
        key = local("cat ~/.ssh/id_rsa.pub", capture=True)
        if key.failed:
            local('ssh-keygen -q -t rsa -f ~/.ssh/id_rsa -N ""')
            key = local("cat ~/.ssh/id_rsa.pub", capture=True)
        # print key.stdout
        res = sudo('grep "{key}" /home/git/.ssh/authorized_keys'.format(key=key))
        if res.failed:
            sudo("mkdir -p /home/git/.ssh && chmod 700 /home/git/.ssh")
            sudo("touch /home/git/.ssh/authorized_keys && chmod 600 /home/git/.ssh/authorized_keys")
            sudo('echo "{key}" >> /home/git/.ssh/authorized_keys'.format(key=key))
            sudo("chown -R git:git /home/git/.ssh")


def check_data_dir():
    with settings(warn_only=True):
        for d in [data_root, git_root, www_root, log_root]:
            if sudo("test -d {dir}".format(dir=d)).failed:
                sudo("mkdir -p {dir}".format(dir=d))
                sudo("chown -R git:git {dir}".format(dir=d))


def check_app_git():
    check_git()
    with settings(sudo_user="git", warn_only=True):
        for project, items in projects.iteritems():
            if _get_current_role() in items.get('roles', env.roledefs.keys()):
                app_git = project + ".git"
                app_git_dir = "{git_root}/{app_git}".format(git_root=git_root, app_git=app_git)
                if sudo("test -d {app_git_dir}".format(app_git_dir=app_git_dir)).failed:
                    with cd(git_root):
                        sudo("git init --bare {app_git}".format(app_git=app_git))


def add_local_git():
    with settings(warn_only=True):
        for project, items in projects.iteritems():
            local_path = items.get('local_path')
            if local_path:
                with lcd(local_path):
                    role = _get_current_role()
                    remote_url = _get_remote_url(env.host, project)
                    if role and role in items.get('roles', env.roledefs.keys()):
                        name = aliases.get(env.host_string, role)
                        if local('git remote -v | grep "{name}\t{remote_url}"'.format(name=name, remote_url=remote_url),
                                 capture=True).failed:
                            if local('git remote -v | grep "{name}\t"'.format(name=name), capture=True).failed:
                                local("git remote add {name} {remote_url}".format(name=name, remote_url=remote_url))
                            else:
                                local("git remote set-url --add {name} {remote_url}".format(name=name,
                                                                                            remote_url=remote_url))


def _get_current_role():
    if len(env.effective_roles) > 0:
        return env.effective_roles[0]
    else:
        # 未定义角色默认取第一个
        for role in env.roledefs.keys():
            if env.host_string in env.roledefs[role]:
                return role

    print "host = {} not found in role define".format(env.host_string)
    return None


# @task
def push(project=None, role=None):
    if not role:
        role = _get_current_role()
    with settings(warn_only=True):
        for p, items in projects.iteritems():
            if project is None or p == project:
                local_path = items.get('local_path')
                if local_path and role in items.get('roles', env.roledefs.keys()):
                    with lcd(local_path):
                        branch = _get_branch(role)
                        name = aliases.get(env.host_string, role)
                        print "push {project} {role} to {host}".format(host=env.host, project=p, role=role)
                        local("git push {name} {branch}".format(name=name, branch=branch))


def check_app_dir():
    with settings(sudo_user="git", warn_only=True):
        with cd(www_root):
            for project, items in projects.iteritems():
                role = _get_current_role()
                if role in items.get('roles', env.roledefs.keys()):
                    app_dir = get_app_dir(project, items)
                    branch = _get_branch(role)
                    git_dir = '{git_root}/{project}.git'.format(git_root=git_root, project=project)
                    if app_dir and sudo("test -d %s" % app_dir).failed:
                        sudo("git clone --mirror {git_dir} {app_dir}/.git".format(git_dir=git_dir, app_dir=app_dir))
                        with cd(app_dir):
                            sudo("git config --bool core.bare false && git checkout {branch}".format(branch=branch))

    update_post_receive()


def get_app_dir(project, items, without_branch=False):
    if items.get('is_app') is True:
        app_dir = '{app_root}/{project}'.format(app_root=app_root, project=project)
    else:
        role = _get_current_role()
        if role in items.get('roles', env.roledefs.keys()):
            if without_branch:
                branch = ''
            else:
                branch = branches.get(role, '')
            app_dir = '{www_root}/{project}{branch}'.format(www_root=www_root, project=project,
                                                            branch='_{}'.format(branch) if branch else '')
        else:
            app_dir = ''
    return app_dir


# @task
def update_post_receive(project=None):
    with settings(user="git", warn_only=True):
        with cd(www_root):
            for p, items in projects.iteritems():
                role = _get_current_role()
                if role in items.get('roles', env.roledefs.keys()):
                    if project is None or project == p:
                        app_dir = get_app_dir(p, items)
                        branch = _get_branch(role)
                        if app_dir:
                            sudo(" cd {app_dir} && git pull origin {branch}".format(app_dir=app_dir, branch=branch))
                            git_dir = '{git_root}/{project}.git'.format(git_root=git_root, project=p)

                            post_receive = "{git_dir}/hooks/post-receive".format(git_dir=git_dir)

                            sudo("echo '{pull_template}' > {post_receive}".format(
                                    pull_template=pull_template.format(app_dir=get_app_dir(p, items, True),
                                                                       branch=branch),
                                    post_receive=post_receive))
                            sudo("chmod +x {post_receive}".format(post_receive=post_receive))

                            _first_run(app_dir, branch)


def _first_run(app_dir, branch):
    tmp_file = '/tmp/first_run.sh'
    sudo("echo '{run_template}' > {tmp_file}".format(
            run_template=first_run_template.format(app_dir=app_dir,
                                                   branch=branch),
            tmp_file=tmp_file
    ))
    sudo("chmod +x {tmp_file}".format(tmp_file=tmp_file))
    sudo(tmp_file)
    sudo('rm {tmp_file}'.format(tmp_file=tmp_file))


def _get_remote_url(host, project):
    return 'git@{host}:{git_root}/{project}.git'.format(host=host, git_root=git_root, project=project)


def test(project):
    with settings(warn_only=True):
        for p, items in projects.iteritems():
            if project is None or p == project:
                local_path = items.get('local_path')
                unittest = items.get('unittest')
                if unittest and local("test -d {local_path}/tests".format(local_path=local_path),
                                      capture=True).succeeded:
                    result = local(
                            'python -m unittest discover {local_path}/tests'.format(local_path=local_path),
                            capture=True)
                    if result.failed and not confirm("Tests failed. Continue anyway?"):
                        abort("Aborting at user request.")


def commit():
    local("git add -p && git commit")


# @task
def reload_service(project=None):
    with settings(warn_only=True):
        update_post_receive(project)


# @task
def check_alive():
    with settings(warn_only=True):
        time.sleep(2)
        for project, items in projects.iteritems():
            if items.get('is_app') is not True:
                domain_config = _get_domain()
                alive = items.get('alive')
                role = _get_current_role()
                if role in items.get('roles', env.roledefs.keys()):
                    if isinstance(alive, dict):
                        for url, status_code in alive.iteritems():
                            check_url = url.format(prefix=domain_config['prefix'], domain=domain_config['domain'],
                                                   port=domain_config['port'], host=env.host)
                            c = local(
                                    'curl -sL -w "%{http_code}"' + ' {check_url} -o /dev/null'.format(
                                            check_url=check_url),
                                    capture=True)
                            if int(c.stdout) != status_code:
                                print(red("curl {project} failed： status={status} ".format(project=project,
                                                                                           status=str(c.stdout))))
                            else:
                                print(green("deploy success!"))
                    else:
                        check_url = items.get('alive').format(prefix=domain_config['prefix'],
                                                              domain=domain_config['domain'],
                                                              port=domain_config['port'], host=env.host)
                        c = local(
                                'curl -sL -f -w "%{http_code}"' + ' {check_url} -o /dev/null'.format(
                                        check_url=check_url),
                                capture=True)
                        if c.failed:
                            print(red("curl {project} failed： status={status} ".format(project=project,
                                                                                       status=str(c.stdout))))
                        else:
                            print(green("deploy success!"))


def check_docker_compose():
    with settings(warn_only=True):
        result = sudo('which docker-compose')
        if result.failed:
            sudo(
                'curl -L https://get.daocloud.io/docker/compose/releases/download/1.6.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose')


def build(project=None):
    """
    更新镜像
    :param project:
    :type project:
    :return:
    :rtype:
    """
    with settings(sudo_user="git", warn_only=True):
        with cd(www_root):
            for p, items in projects.iteritems():
                role = _get_current_role()
                if role in items.get('roles', env.roledefs.keys()):
                    if project is None or project == p:
                        app_dir = get_app_dir(p, items)
                        if app_dir:
                            with cd(app_dir):
                                branch = _get_branch(role)
                                sudo("git pull origin {branch}".format(branch=branch))
                                sudo('docker-compose -f {env}.yml build'.format(env=role))
                                sudo(
                                        'docker-compose -f {env}.yml stop && docker-compose -f {env}.yml rm -f'.format(
                                                env=role))
        reload_service()


def rollback(project=None):
    """
    更新镜像
    :param project:
    :type project:
    :return:
    :rtype:
    """
    with settings(sudo_user="git", warn_only=True):
        with cd(www_root):
            for p, items in projects.iteritems():
                role = _get_current_role()
                if role in items.get('roles', env.roledefs.keys()):
                    if project is None or project == p:
                        app_dir = get_app_dir(p, items)
                        if app_dir:
                            with cd(app_dir):
                                sudo("git checkout HEAD~1 -f")
                                sudo('docker-compose -f {env}.yml up -d'.format(env=role))
                                sudo('docker-compose -f {env}.yml kill -s HUP'.format(env=role))
