FROM openjdk:8-jdk-alpine
ENV JAVA_OPTS=""
ENV VERSION="0.0.1"
VOLUME /tmp
RUN mkdir /code/
WORKDIR /code
ADD . /code/
RUN ./gradlew --no-daemon clean build && rm -rf $HOME/.gradle
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar build/libs/sender-$VERSION.jar"]
