aptinst () {
  if [[ `dpkg -l|grep ${1}` ]]; then
    str=${1}'/'${2}
    echo ${1} already installed
    echo ${str}>>ffreeze.txt
  else
    echo install ${1}?
    read ans
    if [ ${ans} = 'y' ]; then
      sudo ${2} install ${1}
    fi
  fi
}
pipinst () {
  if [[ `${2} list|grep ${1}` ]]; then
    str=${1}'/'${2}
    echo ${1} already installed
    echo ${str}>>ffreeze.txt
  else
    echo install ${1}?
    read ans
    if [ ${ans} = 'y' ]; then
      sudo ${2} install ${1}
    fi
  fi
}

sudo apt-get update
#install pip
aptinst python-pip apt
aptinst python3-pip apt
pip install --upgrade pip
pip3 install --upgrade pip
#install sox
aptinst sox apt-get
#install PyAudio
#wget https://pypi.python.org/packages/ab/42/b4f04721c5c5bfc196ce156b3c768998ef8c0ae3654ed29ea5020c749a6b/PyAudio-0.2.11.tar.gz#md5=7e4c88139284033f67b4336c74eda3b8
#tar xzvf PyAudio-0.2.11.tar.gz
#cd PyAudio-0.2.11
#sudo python3 setup.py build
#sudo python3 setup.py install
#cd ..
#sudo rm -rf PyAudio-0.2.11
#sudo rm PyAudio-0.2.11.tar.gz
#install pygame (and dependent packages)
arr=("mercurial" "python3-dev" "python3-setuptools" "python3-numpy" "python3-opengl" "libav-tools" "libsdl-image1.2-dev" "libsdl-mixer1.2-dev" "libsdl-ttf2.0-dev" "libsmpeg-dev" "libsdl1.2-dev" "libportmidi-dev" "libswscale-dev" "libavformat-dev" "libavcodec-dev" "libtiff5-dev" "libx11-6" "libx11-dev" "fluid-soundfont-gm" "timgm6mb-soundfont" "xfonts-base" "xfonts-100dpi" "xfonts-75dpi" "xfonts-cytillic" "fontconfig" "fonts-freefont-ttf")
len=$((${#arr[*]}-1))
for i in `seq 0 ${len}`
do
  aptinst ${arr[i]} apt-get
done
#hg clone https://bitbucket.org/pygame/pygame
#cd pygame
#sudo python3 setup.py build
#sudo python3 setup.py install
#cd ..
#rm -rf pygame
#install mecab
aptinst libmecab-dev apt-get
aptinst mecab apt-get
aptinst mecab-ipadic apt-get
aptinst mecab-ipadic-utf8 apt-get
pipinst mecab-python3 pip3
#install jtalk
aptinst open-jtalk apt-get
aptinst open-jtalk-mecab-naist-jdic apt-get
#aptinst hts-voice-nitech-jp-atr503-m001 apt-get
#install numpy,scipy,scikit-learn
pipinst numpy pip
pipinst scipy pip
pipinst scikit-learn pip
#clone repositories
#git clone https://github.com/yuinityk/ShiritoriAI.git
#git clone https://github.com/yuinityk/CocktailParty.git
