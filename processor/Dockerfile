FROM openjdk:8-jdk-alpine
ENV JAVA_OPTS=""
ENV VERSION="0.0.1"
VOLUME /tmp
ADD build/libs/processor-$VERSION.jar app.jar
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar /app.jar"]
