" set filttype detect for .ipynb
augroup filetypedetect
    au BufRead,BufNewFile *.ipynb setfiletype ipynb.pandoc
augroup END

