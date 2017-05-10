FROM rabbitmq:3.6.9-alpine
RUN apk add --no-cache bash
COPY docker-healthcheck /usr/local/bin/
HEALTHCHECK CMD ["docker-healthcheck"]
