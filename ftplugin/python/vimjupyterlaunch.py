import sys

sys.path.append("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python")

from vimjupyter import VimJupyter
from vimjupytershellwrapper import VimJupyterShellWrapper
from vimipynbformatter import VimIpynbFormatter

vim_jupyter = dict()
vim_jupyter_shell = dict()
vim_jupyter_client = dict()
vim_jupyter_formatter = dict()
vim_jupyter_wrapper = dict()
vim_jupyter_kernel_manager = dict()


def launch(name, existing=""):
    global vim_jupyter
    global vim_jupyter_shell
    global vim_jupyter_client
    global vim_jupyter_kernel_manager
    global vim_jupyter_wrapper
    global vim_jupyter_formatter
    if name in vim_jupyter:
        return

    vim_jupyter[name] = VimJupyter()
    vim_jupyter[name].initialize(existing=existing)
    vim_jupyter_shell[name] = vim_jupyter[name].shell
    vim_jupyter_client[name] = vim_jupyter[name].kernel_client
    vim_jupyter_kernel_manager[name] = vim_jupyter[name].kernel_manager
    vim_jupyter_wrapper[name] = VimJupyterShellWrapper(vim_jupyter_shell[name])
    vim_jupyter_formatter[name] = VimIpynbFormatter(vim_jupyter_shell[name])


def clean_up(name):
    if name in vim_jupyter:
        vim_jupyter_wrapper[name].shutdown_silent()
        del vim_jupyter_wrapper[name]
        del vim_jupyter_formatter[name]
        del vim_jupyter_shell[name]
        del vim_jupyter_client[name]
        del vim_jupyter_kernel_manager[name]
        del vim_jupyter[name]


def clean_all():
    for name in vim_jupyter:
        clean_up(name)
