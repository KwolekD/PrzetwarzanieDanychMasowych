FROM alpine:3.22

ARG FONT=slant

ENV FONT=$FONT

RUN apk add --no-cache figlet

ADD whale.txt /

ENTRYPOINT ["sh", "-c", "cat /whale.txt && figlet -f \"$FONT\" \"$@\"", "banner"]

CMD ["Witaj w PDM!"]
