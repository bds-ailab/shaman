#!/usr/bin/bash
# Copyright 2020 BULL SAS All rights reserved

mkdir -p ~/.ssh
chmod 0700 ~/.ssh
ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N "" -C "$(whoami)@$(hostname)-$(date -I)"
cat ~/.ssh/id_rsa.pub > ~/.ssh/authorized_keys
chmod 0640 ~/.ssh/authorized_keys
cat <<EOT >> ~/.ssh/config
Host *
StrictHostKeyChecking no
UserKnownHostsFile /dev/null
LogLevel QUIET
EOT
chmod 0644 ~/.ssh/config

