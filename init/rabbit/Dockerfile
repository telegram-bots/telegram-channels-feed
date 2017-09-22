FROM rabbitmq:3.6.12-management-alpine
RUN apk add --no-cache bash
COPY docker-healthcheck /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck
HEALTHCHECK CMD ["docker-healthcheck"]
