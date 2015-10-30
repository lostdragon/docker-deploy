FROM linxiaoya_web:latest

RUN echo "deb http://mirrors.163.com/debian/ jessie main non-free contrib\n"\
"deb http://mirrors.163.com/debian/ jessie-updates main non-free contrib\n"\
"deb http://mirrors.163.com/debian/ jessie-backports main non-free contrib\n"\
"deb-src http://mirrors.163.com/debian/ jessie main non-free contrib\n"\
"deb-src http://mirrors.163.com/debian/ jessie-updates main non-free contrib\n"\
"deb-src http://mirrors.163.com/debian/ jessie-backports main non-free contrib\n"\
"deb http://mirrors.163.com/debian-security/ jessie/updates main non-free contrib\n"\
"deb-src http://mirrors.163.com/debian-security/ jessie/updates main non-free contrib" > /etc/apt/sources.list

RUN apt-get update && apt-get install -y openssh-server && apt-get autoremove

RUN mkdir -p /var/run/sshd && sed -i "s/UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config && sed -i "s/UsePAM.*/UsePAM no/g" /etc/ssh/sshd_config && sed -i "s/PermitRootLogin.*/PermitRootLogin yes/g" /etc/ssh/sshd_config
RUN echo 'root:password' | chpasswd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]