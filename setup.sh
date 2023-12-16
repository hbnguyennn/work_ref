#!/bin/bash

c_time=`date +"%Y_%m_%d_%H%M%S"`

echo $c_time
bk_place=${HOME}/dotfiles_bk_${c_time}
mkdir -p ${bk_place}

for word in vimrc tmux.conf ctags  
do
   echo $word
   if [ -f ${HOME}/.${word} ]; then
      mv -v ${HOME}/.${word} ${bk_place}
   fi
   cp -v ${word} ${HOME}/.${word}
done


