
if !has('pythonx')
    " exit if python3 is not available.
    " XXX: raise an error message here
    finish
end



pyx << EOF
import sys
vim_jupyter_path = "/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python/"
sys.path.append(vim_jupyter_path)
from vimjupyterlaunch import launch
launch()
EOF


au BufWritePost *.ipynb pythonx formmater.to_ipynb()
au Quitpre * pythonx shutdown_silent(vim_jupyter_shell)

if g:ipynb_convert_on_start == 1
    pythonx formmater.from_ipynb()
endif


noremap  <Plug>(FromIpynb)              :pythonx formmater.from_ipynb()<CR>
noremap  <Plug>(ToIpynb)                :pythonx formmater.to_ipynb()<CR>
noremap  <Plug>(ConnectToPreviousKernel):pythonx launch(existing="*.json")<CR>
noremap  <Plug>(ConnectToKernel)        :pythonx launch(existing=)<CR>
noremap  <Plug>(StartKernel)            :pythonx launch()<CR>
noremap  <Plug>(KernelShutdown)         :pythonx shutdown_verbose(vim_jupyter_shell)<CR>
noremap  <Plug>(KernelRestart)          :pythonx restart(vim_jupyter_shell)<CR>
noremap  <Plug>(RunCell) ()             :pythonx run_cell(vim_jupyter_shell, )<CR>
noremap  <Plug>(RunCurrentCell)         :pythonx run_cell_under_cursor(vim_jupyter_shell, down=False)<CR>
noremap  <Plug>(RunCurrentCellDown)     :pythonx run_cell_under_cursor(vim_jupyter_shell, down=True)<CR>
noremap  <Plug>(RunLine)                :pythonx run_line(vim_jupyter_shell)<CR>
noremap  <Plug>(RunAll)                 :pythonx run_all(vim_jupyter_shell)<CR>
noremap  <Plug>(PrintUnderCursor)       :pythonx print_variable(vim_jupyter_shell, arg="")<CR>
noremap  <Plug>(PrintVariable)          :pythonx print_variable(vim_jupyter_shell, arg="")<CR>
noremap  <Plug>(GetDocUnderCursor)      :pythonx get_doc(vim_jupyter_shell, arg="")<CR>
noremap  <Plug>(GetDoc)                 :pythonx get_doc(vim_jupyter_shell, arg="")<CR>



map <buffer><localleader>r              <Plug>(RunAll) 
map <buffer><localleader>cc             <Plug>(RunCurrentCell)
map <buffer><localleader>cn             <Plug>(RunCell)
nmap <buffer><space>                    <Plug>(RunLine)
map <buffer><localleader>p              <Plug>(PrintUnderCursor)
map <buffer><localleader>pn             <Plug>(PrintVariable)
map <buffer><localleader>h              <Plug>(GetDocUnderCursor) 
map <buffer><localleader>hn             <Plug>(GetDoc) 
map <buffer><localleader>a              :call IpynbRunAboveLines()  <cr>
map <buffer><localleader>d              <Plug>(RunCurrentCellDown)


