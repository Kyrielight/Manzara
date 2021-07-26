#!/bin/bash

docker run -d \
    --name "usagi12" \
    --log-opt max-size=1m \
    --log-opt max-file=1 \
    --restart always \
    usagi12

docker logs -f usagi12