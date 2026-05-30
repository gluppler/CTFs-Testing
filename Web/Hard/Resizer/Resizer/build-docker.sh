#!/bin/sh

docker build --tag=web-resizer . && \
docker run -p 5022:5000 --rm --name=web-resizer -it web-resizer
