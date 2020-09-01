#!/bin/bash
#SBATCH --job-name=TestJob
#SBATCH --nodelist=pic51
sleep $(( ( RANDOM % 10 )  + 1 ))