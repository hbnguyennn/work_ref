set nocompatible
syntax enable

set scrolloff=1
set t_Co=256
set background=dark

set hlsearch
set cursorline

set nu
set noerrorbells
set novisualbell
set ts=3
set expandtab

set sw=2
set ls=2
set autoread 
set ai
set cmdheight=2
set showmatch
set mat=2
set cd=,,

set nobackup
set statusline=%<%f%h%h%m%r%=%{&ff}\ %l,%c%V\ %P

set mouse=a
set tags=./tags,tags;

set nowrap
set formatoptions-=t
set tw=0

augroup filetypedetect
  autocmd BufRead,BufNewFile *.V       set ft=verilog
  autocmd BufRead,BufNewFile *.bv      set ft=verilog
  autocmd BufRead,BufNewFile *.vh      set ft=verilog
  autocmd BufRead,BufNewFile *.sv      set ft=systemverilog
  autocmd BufRead,BufNewFile *.svh     set ft=systemverilog
  autocmd BufRead,BufNewFile *.sv.kpp  set ft=systemverilog
  autocmd BufRead,BufNewFile *.sv      set ft=systemverilog
  autocmd BufRead,BufNewFile *.src     set ft=asm
  autocmd BufRead,BufNewFile *.io      set ft=iskeyword+=[,],.
augroup END

:map <C-j> :vertical resize -5<CR>
:map <C-k> :resize +5<CR>
:map <C-i> :resize -5<CR>
:map <C-l> :vertical resize +5<CR>

set tags=./tags,tags;
map <C-\> :vsp<CR>:exec("tag ".expand("<cword>"))<CR>
map <C-p> : sp<CR>:exec("tag ".expand("<cword>"))<CR>
map <C-t> :tab split<CR>:exec("tag ".expand("<cword>"))<CR>
