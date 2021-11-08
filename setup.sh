sudo apt update
sudo apt install vim screen htop git golang haskell-platform firefox curl zsh

echo "
caption string \"%{03} \"
rendition so =00
startup_message off

focus
screen -t \"zsh\" zsh
split -v
focus
screen -t \"htop\" htop
focus
" > ~/.screenrc

echo "
set showtabline=0
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab smarttab

syntax on
autocmd BufWritePre * :%s/\s\+$//e
" > ~/.vimrc
