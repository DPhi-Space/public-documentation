FROM busybox:latest

WORKDIR /app
COPY echo-test.sh .
RUN chmod +x /app/echo-test.sh

ENTRYPOINT [ "/app/echo-test.sh" ]
