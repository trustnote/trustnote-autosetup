#setup ubuntu env
apt-get update
apt-get install -y apt-transport-https
apt-get install -y ca-certificates
apt-get install -y curl
apt-get install -y apt-transport-https
apt-get install -y software-properties-common
apt-get install -y gcc
apt-get install -y g++
apt-get install -y make
apt-get install -y git
apt remove -y python*
apt install -y python3
update-alternatives --install /usr/bin/python python /usr/bin/python3 150
apt-get update

#setup nodejs env
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
apt-get install -y nodejs
apt-get install -y build-essential
apt-get install sqlite3
#npm i -g npm #do not excute this upgrade, this will make "npm install sqlite3" failed, and current version is 5.6.0
npm install -g pm2