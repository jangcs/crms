docker run --interactive \
           --tty \
           --rm \
           --name crms \
           --volume "$(pwd)"/models:/models \
           --mount type=bind,source="$(pwd)"/watchdog.env,target=/app/.env \
           crms:0.1 
