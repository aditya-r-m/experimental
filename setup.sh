if grep -qEi "arch" /proc/version &> /dev/null ; then
    pacman -Syu git go haskell-language-server vim tmux
fi

if grep -qEi "ubuntu" /proc/version &> /dev/null ; then
    sudo apt update && sudo apt upgrade && sudo apt install git golang haskell-platform vim tmux
fi

echo "
set -g default-terminal \"screen-256color\"
unbind C-b
set -g prefix C-a
set-hook -g -t 0 after-new-session \"splitw -h -p 40 \\\"ghci\\\" \; selectp -t 0\"
" | tee ~/.tmux.conf

echo "
set showtabline=0
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab smarttab

syntax on
autocmd BufWritePre * :%s/\s\+$//e
" | tee ~/.vimrc

