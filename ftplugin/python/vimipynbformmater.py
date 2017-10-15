import vim
import nbformat

cb = vim.current.buffer
cb_name = vim.current.buffer.name
vim_ipynb_nbs = {}

with open(cb_name) as cf:
    vim_ipynb_nbs[cb_name] = (nbformat.read(cf, as_version=4))

cb[:] = None
for cell in vim_ipynb_nbs[cb_name].cells:
    if cell["cell_type"] == "code":
        cb.append("")
        cb.append("#%% code")

    elif cell["cell_type"] == "markdown":
        cb.append("")
        cb.append("#%% markdown")

    cb.append(cell["source"].split('\n'))

