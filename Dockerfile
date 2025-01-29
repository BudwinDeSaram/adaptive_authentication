# BUILD
FROM alpine:3.18

RUN set -ex && \
    apk --no-cache --update add \
    sudo libstdc++ cmake g++ gcc bash git linux-headers libpthread-stubs make \
    libpq python3-dev py3-pip py3-wheel

RUN addgroup -S appgroup && adduser -S 10005 -G appgroup

WORKDIR /flexfringe

COPY . ./

# Build flexfringe
RUN make clean all

WORKDIR /app

COPY authenticator/main.py ./

RUN mkdir -p /home/flexfringe/model && \
    chown -R 10005:appgroup /home/flexfringe /app /flexfringe

RUN pip install flask user-agents flask-cors pymongo[srv]==3.12

USER 10005

WORKDIR /home/flexfringe
COPY . .
RUN cp /flexfringe/flexfringe . 

EXPOSE 8080

ENTRYPOINT ["python3", "authenticator/main.py"]
