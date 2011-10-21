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

syn match dmslDirective /[%#.][a-zA-Z0-9\-_]*/he=e-1 contains=dmslTag
syn match dmslTag contained "[a-zA-Z0-9]"

syn match dmslFormat "{.*}"

syn match dmslAttr "\[.*\]" contains=dmslAttrKey,dmslAttrValue,dmslFormat
syn match dmslAttrKey contained /[a-zA-Z0-9]*=/he=e-1,me=e-1
syn match dmslAttrValue contained /=[a-zA-Z0-9\./"\ \:\-\;\,]*/hs=s+1

syn match dmslPython /^\ *[:a-z].*$/ contains=dmslPythonStatement,dmslPythonRepeat,dmslPythonConditional,dmslPythonException,dmslPythonOperator,dmslPythonString
syn keyword dmslPythonStatement contained break continue del return as pass raise global assert lambda yield with nonlocal False None True
syn keyword dmslPythonRepeat contained for while
syn keyword dmslPythonConditional contained if elif else
syn keyword dmslPythonException contained try except finally
syn keyword dmslPythonOperator contained and is in not or
syn match dmslPythonString contained /\'.*\'/

hi def link dmslAttr Identifier
hi def link dmslAttrKey Type
hi def link dmslAttrValue String
hi def link dmslDirective Special
hi def link dmslTag Label
" hi def link dmslPython Macro
hi def link dmslFormat Macro
hi dmslPython ctermbg=17
"hi dmslFormat ctermfg=79
hi dmslPythonStatement ctermfg=39 ctermbg=17
hi dmslPythonRepeat ctermfg=39 ctermbg=17
hi dmslPythonConditional ctermfg=39 ctermbg=17
hi dmslPythonException ctermfg=39 ctermbg=17
hi dmslPythonOperator ctermfg=39 ctermbg=17
hi dmslPythonString ctermfg=51 ctermbg=17
