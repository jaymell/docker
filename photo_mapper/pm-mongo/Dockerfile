FROM centos
RUN yum install -y epel-release
RUN yum install -y mongodb-server.x86_64
RUN mkdir -p /data/db
EXPOSE 27017
ENTRYPOINT ["/usr/bin/mongod"]
