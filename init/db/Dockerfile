FROM postgres:9.6.2-alpine
ADD schema.sql /docker-entrypoint-initdb.d/
HEALTHCHECK CMD ["pg_isready"]
