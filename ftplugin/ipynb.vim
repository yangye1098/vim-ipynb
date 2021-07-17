

if !has('pythonx')
    " exit if python3 is not available.
    " XXX: raise an error message here
    finish
end



pyx << EOF
import sys
import vim
vim_expand = vim.Function('expand')

vim_jupyter_path = str(vim_expand('<sfile>:p:h'), 'utf-8') + "/python"
sys.path.append(vim_jupyter_path)
from vimjupytermanager import *
launch(vim.current.buffer.name)
EOF


au BufWritePost *.ipynb pythonx vim_jupyter_formatter[vim.current.buffer.name].to_ipynb()
au BufDelete *.ipynb pythonx clean_up(vim.current.buffer.name)
au VimLeave * pythonx clean_all()


" Wrap python function to vim command

command! -nargs=0 ConvertIpynb            :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_buffer()
command! -nargs=0 ToIpynb                 :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_ipynb()
command! -nargs=0 ToPandoc                :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_pandoc()
command! -nargs=0 ToHtml                  :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_html()
command! -nargs=0 ToMd                    :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_markdown()
command! -nargs=0 ToPdf                   :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_pdf()
command! -nargs=0 ToCode                  :pythonx vim_jupyter_formatter[vim.current.buffer.name].to_code()
command! -nargs=0 ClearAll                :pythonx vim_jupyter_formatter[vim.current.buffer.name].clear_all_output()



command! -nargs=0 Kernelname              :pythonx print_kernel_name(vim.current.buffer.name)
command! -nargs=1 StartKernel             :pythonx start_kernel(vim.current.buffer.name, kernel_name="<args>")
command! -nargs=1 ConnectToKernel         :pythonx change_kernel(vim.current.buffer.name, existing="<args>")
command! -nargs=0 ConnectToPreviousKernel :pythonx change_kernel(vim.current.buffer.name, existing="kernel-*.json")
command! -nargs=0 KernelShutdown          :pythonx vim_jupyter_wrapper[vim.current.buffer.name].shutdown_verbose()
command! -nargs=0 KernelRestart           :pythonx vim_jupyter_wrapper[vim.current.buffer.name].restart()
command! -nargs=0 RunAll                  :pythonx vim_jupyter_wrapper[vim.current.buffer.name].run_all()
command! -nargs=0 RunLine                 :pythonx vim_jupyter_wrapper[vim.current.buffer.name].run_line()
command! -nargs=0 RunLineAbort            :pythonx vim_jupyter_wrapper[vim.current.buffer.name].run_line_abort()
command! -nargs=1 RunCell                 :pythonx vim_jupyter_wrapper[vim.current.buffer.name].run_cell(arg="<args>")
command! -nargs=0 RunCurrentCell          :pythonx vim_jupyter_wrapper[vim.current.buffer.name].run_cell_under_cursor(down=False)
command! -nargs=0 RunCurrentCellDown      :pythonx vim_jupyter_wrapper[vim.current.buffer.name].run_cell_under_cursor(down=True)
command! -nargs=1 PrintVariable           :pythonx vim_jupyter_wrapper[vim.current.buffer.name].print_variable(arg="<args>")
command! -nargs=0 PrintUnderCursor        :pythonx vim_jupyter_wrapper[vim.current.buffer.name].print_variable(arg="")
command! -nargs=1 GetDoc                  :pythonx vim_jupyter_wrapper[vim.current.buffer.name].get_doc(arg="<args>")
command! -nargs=0 GetDocUnderCursor       :pythonx vim_jupyter_wrapper[vim.current.buffer.name].get_doc(arg="")




noremap  <Plug>(FromIpynb)               :FromIpynb<CR>
noremap  <Plug>(ToIpynb)                 :ToIpynb<CR>
noremap  <Plug>(ToPandoc)                :ToPandoc<CR>
noremap  <Plug>(ToHtml)                  :ToHtml<CR>
noremap  <Plug>(ToMd)                    :ToMd<CR>
noremap  <Plug>(ToPdf)                   :ToPdf<CR>
noremap  <Plug>(ToCode)                :ToCode<CR>
noremap  <Plug>(ClearAll)                :ClearAll<CR>

noremap  <Plug>(ConnectToPreviousKernel) :ConnectToPreviousKernel<CR>
noremap  <Plug>(ConnectToKernel)         :ConnectToKernel<Space>
noremap  <Plug>(StartKernel)             :StartKernel<Space>
noremap  <Plug>(KernelShutdown)          :KernelShutdown<CR>
noremap  <Plug>(KernelRestart)           :KernelRestart<CR>

noremap  <Plug>(RunCell)                 :RunCell<Space>
noremap  <Plug>(RunCurrentCell)          :RunCurrentCell<CR>
noremap  <Plug>(RunCurrentCellDown)      :RunCurrentCellDown<CR>
noremap  <Plug>(RunLine)                 :RunLine<CR>
noremap  <Plug>(RunLineAbort)            :RunLineAbort<CR>
noremap  <Plug>(RunAll)                  :RunAll<CR>

noremap  <Plug>(PrintUnderCursor)        :PrintUnderCursor<CR>
noremap  <Plug>(PrintVariable)           :PrintVariable<Space>
noremap  <Plug>(GetDocUnderCursor)       :GetDocUnderCursor<CR>
noremap  <Plug>(GetDoc)                  :GetDoc<Space>


"keyboard shortcuts

map <buffer><localleader>r              <Plug>(RunAll)
map <buffer><localleader>cc             <Plug>(RunCurrentCell)
map <buffer><localleader>cd             <Plug>(RunCurrentCellDown)
map <buffer><localleader>cn             <Plug>(RunCell)
nmap <buffer><space>                    <Plug>(RunLine)
nmap <buffer><localleader>a             <Plug>(RunLineAbort)
map <buffer><localleader>p              <Plug>(PrintUnderCursor)
map <buffer><localleader>pn             <Plug>(PrintVariable)
map <buffer><localleader>h              <Plug>(GetDocUnderCursor)
map <buffer><localleader>hn             <Plug>(GetDoc)   

" turn off pandoc auto exec
let g:pandoc#command#autoexec_on_writes = 0


if !exists("g:ipynb_convert_on_start")
    let g:ipynb_convert_on_start=1
endif

if g:ipynb_convert_on_start == 1
    pythonx vim_jupyter_formatter[vim.current.buffer.name].to_buffer()
endif








