# 第一阶段：构建阶段
FROM python:3.10.11-alpine AS builder

# 安装必要的构建依赖
RUN apk add --no-cache --virtual .build-deps gcc musl-dev openssl-dev coreutils
COPY requirements.txt ./
# 安装 Python 包
RUN pip install --no-cache-dir -r requirements.txt
# 清理编译依赖
RUN apk del --purge .build-deps && \
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

# 第二阶段：运行阶段
FROM python:3.10.11-alpine

# 设置环境变量
ENV TZ=Asia/Shanghai \
    DOCKER_MODE=1 \
    PYTHONUNBUFFERED=1
# 安装必要的运行依赖
RUN apk add --no-cache \
    mariadb-connector-c \
    tzdata \
    mysql-client \
    git && \
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 设置默认工作目录
WORKDIR /app

# 复制构建阶段的输出
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 克隆项目代码并清理不需要的文件
RUN git clone https://github.com/moonfogs/Sakura_embyboss . && \
    rm -rf ./image

# 设置启动命令
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
