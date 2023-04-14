docker run --interactive \
           --tty \
           --rm \
           --name crms \
           --volume "$(pwd)"/models:/models \
           --mount type=bind,source="$(pwd)"/cloudrobotai-owner-e5ca3becb1d7.json,target=/app/cloudrobotai-owner-e5ca3becb1d7.json \
           --env GOOGLE_APPLICATION_CREDENTIALS=/app/cloudrobotai-owner-e5ca3becb1d7.json \
           crms-agent:0.9 \
           /usr/local/bin/crms pull git@github.com:jangcs/model_v4.git -t /models/model_v4 
