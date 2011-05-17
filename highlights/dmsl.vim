" Vim syntax file
" Language: Damsel
" Maintainer: Daniel Skinner
" Latest Revision: 16 May 2011
"
" To install, add the following two lines to ~/.vimrc
" au BufRead,BufNewFile *.dmsl set filetype=dmsl
" au! Syntax dmsl source /path/to/dmsl.vim

if exists("b:current_syntax")
  finish
endif

syn match dmslDirective "[%#\.][a-zA-Z0-9]*" contains=dmslTag
syn match dmslTag contained "[a-zA-Z0-9]*"

syn match dmslAttr "\[.*\]" contains=dmslAttrKey,dmslAttrValue
syn match dmslAttrKey contained /[a-zA-Z0-9]*=/he=e-1,me=e-1
syn match dmslAttrValue contained /=[a-zA-Z0-9"\ ]*/hs=s+1

hi def link dmslAttr Identifier
hi def link dmslAttrKey Type
hi def link dmslAttrValue String
hi def link dmslDirective Special
hi def link dmslTag Label
