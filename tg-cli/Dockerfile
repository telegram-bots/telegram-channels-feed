FROM debian:jessie-slim
RUN useradd telegram && mkdir -p /home/telegram/.telegram-cli/ && chown telegram /home/telegram/.telegram-cli
ENV TGCLI_VERSION 1222
ENV LUAROCKS_VERSION 2.4.2
ENV LUAJIT_VERSION 2.1.0-beta3
# This could be even smaller if we disable Python (there's a bug preventing the configure flag from working currently)
RUN apt-get update -y && apt-get install -y --no-install-recommends libreadline-dev libconfig-dev libssl-dev \
    lua5.2 liblua5.2-dev libevent-dev libjansson-dev libpython-dev make libbsd0 curl ca-certificates netcat git gcc unzip && \
    curl -L "https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64" -o /bin/dumb-init && \
    curl -L "https://valtman.name/files/telegram-cli-${TGCLI_VERSION}" -o /bin/telegram-cli && \
    chmod +x /bin/dumb-init /bin/telegram-cli
# LuaJIT, LuaRocks and modules
COPY amqp-2.0-1.rockspec /home/telegram
RUN curl -L "http://luajit.org/download/LuaJIT-${LUAJIT_VERSION}.tar.gz" -o ./LuaJIT-${LUAJIT_VERSION}.tar.gz && \
    tar -xzvf LuaJIT-${LUAJIT_VERSION}.tar.gz && rm -f LuaJIT-${LUAJIT_VERSION}.tar.gz && \
    cd LuaJIT-${LUAJIT_VERSION} && \
    make install && make clean && ln -sf luajit-${LUAJIT_VERSION} /usr/local/bin/luajit \
    cd .. && rm -rf LuaJIT-${LUAJIT_VERSION} && \
    curl -L "http://luarocks.org/releases/luarocks-${LUAROCKS_VERSION}.tar.gz" -o ./luarocks-${LUAROCKS_VERSION}.tar.gz && \
    tar -xzvf luarocks-${LUAROCKS_VERSION}.tar.gz && rm -f luarocks-${LUAROCKS_VERSION}.tar.gz && \
    cd luarocks-${LUAROCKS_VERSION} && \
    ./configure && make build && make install && make clean && \
    cd .. && rm -rf luarocks-${LUAROCKS_VERSION} && \
    luarocks install lua-cjson && luarocks install /home/telegram/amqp-2.0-1.rockspec
# Cleanup
RUN apt-get purge -y ca-certificates curl gcc unzip git && apt-get autoremove -y && apt-get clean my room
WORKDIR /home/telegram
RUN mkdir -p /telegram/data/data && chmod -R 777 /telegram/data
COPY files/config.cfg /home/telegram/
COPY files/handler.lua /home/telegram/
EXPOSE 4458
ENTRYPOINT ["/bin/dumb-init", "--"]
CMD ["/bin/telegram-cli", "--json", "-P", "4458", "--accept-any-tcp", "--disable-readline", "--config", "/home/telegram/config.cfg"]
COPY docker-healthcheck /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck
HEALTHCHECK CMD ["docker-healthcheck"]
