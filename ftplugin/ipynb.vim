
if !has('pythonx')
    " exit if python3 is not available.
    " XXX: raise an error message here
    finish
end

echo "Hello World!"

pyxfile "/home/eric/.vim/bundle/vim-ipynb/ftplugin/python/vimipynbformmater.py"

