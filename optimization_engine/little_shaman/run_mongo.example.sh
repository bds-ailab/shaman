# This is an example bash script to launch a docker image which launches 
# a mongo database.
# To use this script, you must change the path to the volume in order to
# make the data persistent.
# Also, to deal with access rights, the UID of the user with the proper rights
# on the persistent data folder must be speficied under the -u flag.
# It can be found for a given user by using the command id -u <username>.

docker run --name mongo-shaman \
  # The path to the persistent data
  -v /home_nfs/roberts/shaman_data/db_data:/data/db \
  # The UID of the user 
  -u 16214 \
  --restart=always \
  -p 27017:27017 \
  --detach \
  mongo:3.4
