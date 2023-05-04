docker run --interactive \
           --tty \
           --rm \
           --name crms \
           --network=host \
           --volume "$(pwd)"/crms-models:/crms-models \
           --mount type=bind,source="$(pwd)"/watchdog.env,target=/app/.env \
           -p 6537:6537 \
           crms-agent:0.9 
