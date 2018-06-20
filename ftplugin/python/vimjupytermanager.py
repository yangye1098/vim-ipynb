import sys

from jupyter_client import kernelspec

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
    # only launch once, reconnetiong is dealt in other functions
    if name in vim_jupyter:
        return
    vim_jupyter[name] = VimJupyter()
    vim_jupyter_formatter[name] = VimIpynbFormatter()
    vim_jupyter_formatter[name].read_ipynb() 
    start_kernel(name, vim_jupyter_formatter[name].get_kernel_name())

def start_kernel(name, kernel_name):
    global vim_jupyter
    global vim_jupyter_shell
    global vim_jupyter_client
    global vim_jupyter_kernel_manager
    global vim_jupyter_wrapper
    global vim_jupyter_formatter
    if name not in vim_jupyter:
        launch(name)
    else:
        if kernel_name:
            vim_jupyter[name].set_kernel_name(kernel_name)
            setup(name)

def change_kernel(name, existing=""):
    global vim_jupyter_shell
    global vim_jupyter_client
    global vim_jupyter_kernel_manager
    global vim_jupyter_wrapper
    global vim_jupyter_formatter
    if name not in vim_jupyter:
        launch(name, existing)
    else:
        vim_jupyter_formatter[name].clear_all_output()
        setup(name, existing)

def setup(name, existing=""):
    global vim_jupyter_shell
    global vim_jupyter_client
    global vim_jupyter_kernel_manager
    global vim_jupyter_wrapper
    global vim_jupyter_formatter
    vim_jupyter[name].initialize(existing=existing)
    vim_jupyter_shell[name] = vim_jupyter[name].shell
    vim_jupyter_client[name] = vim_jupyter[name].kernel_client
    vim_jupyter_kernel_manager[name] = vim_jupyter[name].kernel_manager
    vim_jupyter_wrapper[name] = VimJupyterShellWrapper(
        vim_jupyter_shell[name])
    vim_jupyter_shell[name].vim_ipynb_formmater = \
        vim_jupyter_formatter[name]
    vim_jupyter_formatter[name].assign_shell(vim_jupyter_shell[name])


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
    if isinstance(vim_jupyter, dict):
        names = list(vim_jupyter.keys())
        for name in names:
            clean_up(name)
