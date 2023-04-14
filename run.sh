docker run --interactive \
           --tty \
           --rm \
           --name crms \
           --volume "$(pwd)"/models:/models \
           crms-agent:0.9 \
           /usr/local/bin/crms pull git@github.com:jangcs/model_v4.git -t /models/model_v4 
