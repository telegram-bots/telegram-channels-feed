FROM debian:jessie-slim
RUN useradd telegram && mkdir -p /home/telegram/.telegram-cli/ && chown telegram /home/telegram/.telegram-cli
ENV TGCLI_VERSION 1222
# This could be even smaller if we disable Python (there's a bug preventing the configure flag from working currently)
RUN apt-get update -y && apt-get install -y --no-install-recommends netcat libreadline-dev libconfig-dev libssl-dev lua5.2 liblua5.2-dev libevent-dev libjansson-dev \
    libpython-dev make libbsd0 curl ca-certificates git gcc unzip && \
    curl -L "http://luarocks.org/releases/luarocks-2.4.2.tar.gz" -o ./luarocks-2.4.2.tar.gz && \
    tar -xzvf luarocks-2.4.2.tar.gz && \
    rm -f luarocks-2.4.2.tar.gz && \
    cd luarocks-2.4.2 && \
    ./configure && \
    make build && \
    make install && \
    make clean && \
    cd .. && \
    rm -rf luarocks-2.4.2 && \
    luarocks install lua-cjson && \
    luarocks install pgmoon && \
    luarocks install luasocket && \
    curl -L "https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64" -o /bin/dumb-init && \
    curl -L "https://valtman.name/files/telegram-cli-${TGCLI_VERSION}" -o /bin/telegram-cli && \
    chmod +x /bin/dumb-init /bin/telegram-cli && \
    apt-get purge -y ca-certificates curl gcc unzip git && apt-get autoremove -y && apt-get clean my room
WORKDIR /home/telegram
RUN mkdir -p /telegram/data/data && chmod -R 777 /telegram/data
COPY config.cfg /home/telegram/
COPY handler.lua /home/telegram/
EXPOSE 4458
ENTRYPOINT ["/bin/dumb-init", "--"]
CMD ["/bin/telegram-cli", "--json", "-P", "4458", "--accept-any-tcp", "--disable-readline", "--config", "/home/telegram/config.cfg"]
COPY docker-healthcheck /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck
HEALTHCHECK CMD ["docker-healthcheck"]
