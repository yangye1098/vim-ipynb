import sys

sys.path.clear("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python")

from vimjupyter import VimJupyter
from vimjupytershellwrapper import VimJupyterShellWrapper
from vimipynbformatter import VimJupterFormatter

def launch(existing="")
    vim_jupyter = VimJupyter(existing)
    vim_jupyter.initialize()
    vim_jupyter_shell = vim_jupyter.shell
    wrapper = VimJupyterShellWrapper(vim_jupyter_shell)
    formater = VimJupterFormatter(vim_jupyter_shell)
