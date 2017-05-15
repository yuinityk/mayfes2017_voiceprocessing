aptremove () {
  if [[ `cat ffreeze.txt|grep ${1}` ]]; then
    echo initially installed
  else
    echo uninstall ${1}?
    read ans
    if [ ${ans} = 'y' ]; then
      sudo apt-get purge ${1}
    fi
  fi
}
pipremove () {
  if [[ `cat ffreeze.txt|grep ${1}` ]]; then
    echo initially installed
  else
    echo uninstall ${1}?
    read ans
    if [ ${ans} = 'y' ]; then
      sudo ${2} uninstall ${1}
    fi
  fi
}

aptremove sox
arr=("mercurial" "python3-dev" "python3-setuptools" "python3-numpy" "python3-opengl" "libav-tools" "libsdl-image1.2-dev" "libsdl-mixer1.2-dev" "libsdl-ttf2.0-dev" "libsmpeg-dev" "libsdl1.2-dev" "libportmidi-dev" "libswscale-dev" "libavformat-dev" "libavcodec-dev" "libtiff-dev" "libx11-6" "libx11-dev" "fluid-soundfont-gm" "timgm6mb-soundfont" "xfonts-base" "xfonts-100dpi" "xfonts-75dpi" "xfonts-cytillic" "fontconfig" "fonts-freefont-ttf")
len=$((${#arr[*]}-1))
for i in `seq 0 ${len}`
do
  aptremove ${arr[i]}
done
aptremove libmecav-dev
aptremove mecab
aptremove mecab-ipadic
aptremove mecab-ipadic-utf8
pipremove mecab-python3 pip3
aptremove open-jtalk
aptremove open-jtalk-mecab-naist-jdic
pipremove numpy pip
pipremove scipy pip
pipremove scikit-learn pip
echo 'Remove pygame,pyaudio by yourself.'
