sudo yum update
sudo yum install ec2-instance-connect
sudo yum install stress-ng -y
sudo yum install htop -y
sudo yum install python3-pip -y

sudo yum install gcc jemalloc-devel openssl-devel tcl tcl-devel clang wget
sudo wget http://download.redis.io/redis-stable.tar.gz
sudo tar xvzf redis-stable.tar.gz
cd redis-stable
sudo CC=clang make BUILD_TLS=yes

src/redis-cli -h redis-oss-cache.ef1kkf.ng.0001.use1.cache.amazonaws.com -p 6379