#   使用的镜像（本地已有，build 不联网）
FROM python:3.12-slim
#   工作目录：之后所有命令的起点，也是容器的起始目录
WORKDIR /app
#   把代码复制进镜像（漏了这行，镜像里就没有程序）
COPY log_analyze.py .
#   镜像维护者（MAINTAINER 已弃用，改用 LABEL）
LABEL maintainer="zhangdexiang"
#   指定容器启动时执行的命令
ENTRYPOINT ["python","log_analyze.py"]
#   脚本默认参数（相对 WORKDIR，即 /app/access.log）
CMD ["access.log"]
