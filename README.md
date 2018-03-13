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
