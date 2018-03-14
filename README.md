sudo yum update -y

sudo yum install -y docker

sudo yum install -y git

sudo service docker start

sudo usermod -a -G docker ec2-user

sudo curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` -o /usr/bin/docker-compose

sudo chmod +x /usr/bin/docker-compose

git clone https://github.com/lorenzoranucci/Sentimantic.git





# Sentimantic

cd Sentimantic

git submodule init

git submodule update

wget https://repo.continuum.io/archive/Anaconda2-5.1.0-Linux-x86_64.sh

chmod +x Anaconda2-5.1.0-Linux-x86_64.sh

./Anaconda2-5.1.0-Linux-x86_64.sh --yes

export PATH=~/anaconda2/bin:$PATH

conda create -n py2Env python=2.7 anaconda

source activate py2Env

conda install numba

pip install --requirement python-package-requirement.txt

source set_env.sh
