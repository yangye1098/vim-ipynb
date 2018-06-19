
import sys

import time
import re
sys.path.append("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python/")
# from vimjupyterlaunch import launch


# cells = OrderedDict()
# cells['abc'] = nbformat.v4.new_markdown_cell()
# cell['abc']['source'] = "abc"
# print(cell)


# wrapper, fomatter = launch()
# vim_jupyter_shell = wrapper.shell
# vim_jupyter_client = wrapper.shell.client
# vim_jupyter_km = wrapper.shell.manager

# msg = ""

# time.sleep(1)
# while vim_jupyter_client.shell_channel.msg_ready():
#    msg = vim_jupyter_client.shell_channel.get_msg()


# print(msg)
# print(vim_jupyter_shell.kernel_info)

# print(vim_jupyter_client.shutdown(restart=False))
code_cell_start_pattern \
            = re.compile(r'^```(?: python)\s(.*?)\s*(.*?)\n')
code_cell_stop_pattern = re.compile(r'^```\s*\n')
markdown_cell_pattern = re.compile(r'^#%%(?:(.*?)$|(.*?)\s(.*?)$)')
cb = "#%%markdown1"
matchObj = markdown_cell_pattern.match(cb)
if matchObj:
    print(matchObj.group(1))
