FROM rabbitmq:3.6.9-alpine
RUN rabbitmq-plugins enable rabbitmq_management
RUN apk add --no-cache bash
COPY docker-healthcheck /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck
HEALTHCHECK CMD ["docker-healthcheck"]
