import sys

sys.path.append("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python")

from vimjupyter import VimJupyter
from vimjupytershellwrapper import VimJupyterShellWrapper
from vimipynbformatter import VimIpynbFormatter

vim_jupyter = VimJupyter()
vim_jupyter_shell = None
vim_jupyter_client = None
vim_jupyter_formatter = None
vim_jupyter_wrapper = None


def launch(existing=""):
    global vim_jupyter
    global vim_jupyter_shell
    global vim_jupyter_client
    global vim_jupyter_kernel_manager
    global vim_jupyter_wrapper
    global vim_jupyter_formatter

    vim_jupyter.initialize(existing=existing)
    vim_jupyter_shell = vim_jupyter.shell
    vim_jupyter_client = vim_jupyter.kernel_client
    vim_jupyter_kernel_manager = vim_jupyter.kernel_manager
    vim_jupyter_wrapper = VimJupyterShellWrapper(vim_jupyter_shell)
    vim_jupyter_formatter = VimIpynbFormatter(vim_jupyter_shell)
    return vim_jupyter_wrapper, vim_jupyter_formatter
