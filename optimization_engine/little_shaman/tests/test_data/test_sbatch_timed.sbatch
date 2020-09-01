#!/bin/bash
#SBATCH --job-name=TestJob
#SBATCH --ntasks=3
time (
hostname
)