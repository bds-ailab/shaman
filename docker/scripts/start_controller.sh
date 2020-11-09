#!/usr/bin/bash
# Copyright 2020 BULL SAS All rights reserved
# TODO change _ in - for better compliance with shell conventions

# TODO: #20 ugly workaround of forcing munge to run as root ... check later
# Run munge deamon
echo "Starting munge deamon"
/sbin/munged --force
munge -n
munge -n | unmunge
remunge
# Copy key into secret volume to be used again by compute nodes
cp /etc/munge/munge.key /secrets/munge-key

# Launch slurmctld
echo "Starting slurmctld"
slurmctld -f /etc/slurm/slurm.conf

tail -f /dev/null