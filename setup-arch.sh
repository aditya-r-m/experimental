pacman -Syu vim tmux git go haskell-language-server

echo "

unbind C-b
set -g prefix C-a
set-hook -g -t 0 after-new-session \"splitw -h -p 40 \\\"ghci\\\" \; selectp -t 0\"

" > ~/.tmux.conf

echo "

set showtabline=0
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab smarttab

syntax on
autocmd BufWritePre * :%s/\s\+$//e

function! g:StopMatchParen ()
    if exists(\":NoMatchParen\")
        :NoMatchParen
    endif
endfunction

augroup plugin_initialize
    autocmd!
    autocmd VimEnter * call StopMatchParen()
augroup END

" > ~/.vimrc
