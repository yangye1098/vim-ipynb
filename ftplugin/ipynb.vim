
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


au BufWritePost *.ipynb pythonx formatter.to_ipynb()
au Quitpre * pythonx wrapper.shutdown_silent(vim_jupyter_shell)

let g:ipynb_convert_on_start = 1

if g:ipynb_convert_on_start == 1
    pythonx formatter.from_ipynb()
endif

command! -nargs=0 FromIpynb              :pythonx formatter.from_ipynb()
command! -nargs=0 ToIpynb                :pythonx formatter.to_ipynb()
command! -nargs=0 StartKernel            :pythonx launch()
command! -nargs=1 ConnectToKernel        :pythonx launch(existing="<args>")
command! -nargs=0 ConnectToPreviousKernel:pythonx launch(existing="*.json")
command! -nargs=0 KernelShutdown         :pythonx wrapper.shutdown_verbose()
command! -nargs=0 KernelRestart          :pythonx wrapper.restart()
command! -nargs=1 RunCell                :pythonx wrapper.run_cell(arg="<args>")
command! -nargs=1 PrintVariable          :pythonx wrapper.print_variable(arg="<args>")
command! -nargs=1 GetDoc                 :pythonx wrapper.print_variable(arg="<args>")



noremap  <Plug>(FromIpynb)              :FromIpynb<CR>
noremap  <Plug>(ToIpynb)                :ToIpynb<CR>
noremap  <Plug>(ConnectToPreviousKernel):pythonx launch(existing="*.json")<CR>
noremap  <Plug>(ConnectToKernel)        :ConnectToKernel
noremap  <Plug>(StartKernel)            :StartKernel<CR>
noremap  <Plug>(KernelShutdown)         :KernelShutdown<CR>
noremap  <Plug>(KernelRestart)          :KernelRestart<CR>
noremap  <Plug>(RunCell)                :RunCell
noremap  <Plug>(RunCurrentCell)         :pythonx wrapper.run_cell_under_cursor(down=False)<CR>
noremap  <Plug>(RunCurrentCellDown)     :pythonx wrapper.run_cell_under_cursor(vim_jupyter_shell, down=True)<CR>
noremap  <Plug>(RunLine)                :pythonx wrapper.run_line()<CR>
noremap  <Plug>(RunAll)                 :pythonx wrapper.run_all()<CR>
noremap  <Plug>(PrintUnderCursor)       :pythonx wrapper.print_variable(arg="")<CR>
noremap  <Plug>(PrintVariable)          :PrintVariable
noremap  <Plug>(GetDocUnderCursor)      :pythonx get_doc(arg="")<CR>
noremap  <Plug>(GetDoc)                 :GetDoc



map <buffer><localleader>r              <Plug>(RunAll) 
map <buffer><localleader>cc             <Plug>(RunCurrentCell)
map <buffer><localleader>cn             <Plug>(RunCell)
nmap <buffer><space>                    <Plug>(RunLine)
map <buffer><localleader>p              <Plug>(PrintUnderCursor)
map <buffer><localleader>pn             <Plug>(PrintVariable)
map <buffer><localleader>h              <Plug>(GetDocUnderCursor) 
map <buffer><localleader>hn             <Plug>(GetDoc) 
map <buffer><localleader>d              <Plug>(RunCurrentCellDown)


