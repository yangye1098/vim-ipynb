
if !has('pythonx')
    " exit if python3 is not available.
    " XXX: raise an error message here
    finish
end


pyxfile /home/eric/.vim/bundle/vim-ipynb/ftplugin/python/vimipynbformmater.py
pyx << EOF
import sys
sys.path.append("/home/eric/.vim/bundle/vim-ipynb/ftplugin/python/")
from vimjupyterapp import VimJupyterApp
from vimjupytershellwrapper import *
vim_jupyter_app = VimJupyterApp()
vim_jupyter_app.initialize()
vim_jupter_shell = vim_jupyter_app.shell
EOF




"map <buffer><localleader>r :call MatRun() <cr><cr>
"map <buffer><localleader>c :call MatRunCell()  <cr><cr>
"map <buffer><localleader>g :call MatRunCellAdvanced()  <cr><cr>
nmap <buffer><space> :pyx run_line(vim_jupyter_shell)  <cr>
"map <buffer><f5> :call MatRunExtern() <cr><cr>
"map <buffer><localleader>p :call MatDisp()  <cr><cr>
"map <buffer><localleader>h :call MatHelp()  <cr><cr>
"map <buffer><localleader>s :call MatShowFig()  <cr><cr><cr>
"map <buffer><localleader>a :call MatRunAboveLines()  <cr><cr>
"map <buffer><localleader>d :call MatRunDownToNextCell()  <cr><cr>


