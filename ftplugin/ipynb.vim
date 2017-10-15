
if !has('pythonx')
    " exit if python3 is not available.
    " XXX: raise an error message here
    finish
end


pyx << EOF
import sys
sys.path.append("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python/")
from vimjupyterapp import VimJupyterApp
from vimjupytershellwrapper import *
from vimipynbformmater import VimIpynbFormmater
formmater =  VimIpynbFormmater()
vim_jupyter_app = VimJupyterApp()
vim_jupyter_app.initialize()
vim_jupyter_shell = vim_jupyter_app.shell
formmater.from_ipynb()
EOF

au BufWritePost *.ipynb call ToIpynb()
au Quitpre * call ShutDownKernel(1)

function! FromIpynb()
    pyx formmater.from_ipynb()
endfunction

function! ToIpynb()
    pyx formmater.to_ipynb()
endfunction

function! IpynbRunLine()
    ToIpynb()
    echom "Run Line!"
    pyx run_line(vim_jupyter_shell)
endfunction

function! ShutDownKernel(silent)
    if silent == 1
        pyx shutdown_silent(vim_jupyter_shell)
    else
        pyx shutdown_verbose(vim_jupyter_shell)
    endif
endfunction

function! ShutDownKernel()
    pyx shutdown_silent(vim_jupyter_shell)

endfunction

"map <buffer><localleader>r :call MatRun() <cr><cr>
"map <buffer><localleader>c :call MatRunCell()  <cr><cr>
"map <buffer><localleader>g :call MatRunCellAdvanced()  <cr><cr>
nmap <buffer><space> :call IpynbRunLine()  <cr>
"map <buffer><f5> :call MatRunExtern() <cr><cr>
"map <buffer><localleader>p :call MatDisp()  <cr><cr>
"map <buffer><localleader>h :call MatHelp()  <cr><cr>
"map <buffer><localleader>s :call MatShowFig()  <cr><cr><cr>
"map <buffer><localleader>a :call MatRunAboveLines()  <cr><cr>
"map <buffer><localleader>d :call MatRunDownToNextCell()  <cr><cr>


