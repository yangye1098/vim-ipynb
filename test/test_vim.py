import vim

# ratio for window split
ratio = 3

vj_height = vim.current.window.height/3
w_origin_ID = vim.eval("win_getid()")
vim.command("belowright "+str(vj_height)+"split +set\ noreadonly\ modifiable Vim-Jupyter")

cw = vim.current.window
cb = vim.current.buffer
nrow = cw.cursor[0]
msg = "Hello World!\n\rDude\n\n\r\r"
msg_list = msg.split('\n')

cb[:] = None
if cb[nrow-1] == '\n':
    cb.append(str(nrow), nrow-1)
cb.append(str(len(msg_list)))
cb.append(msg_list)
nrow = nrow + len(cb)
cb.append(str(nrow))



vim.command("set readonly nomodifiable")
vim.command("call win_gotoid("+str(w_origin_ID)+")")

vim.command("let vim_jupyter = 1")
vim.eval("vim_jupyter")
