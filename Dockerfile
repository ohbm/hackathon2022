FROM ruby:2.7-alpine3.15

RUN apk update
RUN apk add --no-cache build-base gcc cmake git
RUN gem update bundler && gem install bundler jekyll

ADD scripts/docker-start.sh /start
RUN chmod a+x /start
WORKDIR /code
CMD /start

EXPOSE 8000
EXPOSE 35729
