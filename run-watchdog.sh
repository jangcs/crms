docker run --interactive \
           --tty \
           --rm \
           --name crms \
           --volume "$(pwd)"/crms-models:/crms-models \
           --mount type=bind,source="$(pwd)"/watchdog.env,target=/app/.env \
           -p 6537:6537 \
           crms:0.1 
