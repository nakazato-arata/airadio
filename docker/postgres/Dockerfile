FROM postgres:16.1-bookworm

# タイムゾーン
ENV TZ Asia/Tokyo


# コンテナソースパス定義
ENV SRV_HOME /var/postgres-srv

WORKDIR ${SRV_HOME}

# OSでの必要なツールをインストール
RUN apt-get update \
    && apt-get install -y \
    less \
    vim \
    locales
 
# 日本語化
RUN localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8
ENV LANG ja_JP.UTF-8

# Nuxtで使うツール
RUN apt-get upgrade -y
