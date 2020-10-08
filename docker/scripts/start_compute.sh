#!/usr/bin/bash

# TODO: #20 ugly workaround of forcing munge to run as root ... check later
# Run munge deamon
echo "Starting munge deamon"
# Copy existing key in .secret
cp /secrets/munge-key /etc/munge/munge.key
/sbin/munged --force
munge -n
munge -n | unmunge
remunge

# Launch slurmd
echo "Starting slurmd"
slurmd -f /etc/slurm/slurm.conf

tail -f /dev/null
