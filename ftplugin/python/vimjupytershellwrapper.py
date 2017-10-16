import vim
import re
import sys

sys.path.append("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python/")

from vimjupytershell import VimJupyterShell

getline = vim.Function('getline')
cursor = vim.Function('cursor')
search = vim.Function('search')


class VimJupyterShellWrapper():

    shell = None

    def __init__(self, shell):
        self.shell = shell

    def in_cell(self, pos):
        cursor(pos[0], pos[1])
        row_finish = search("^```\s*[^{]*", "cW")
        row_begin = search("^```\s*{", "bcW")
        cursor(pos[0], pos[1])
        if row_finish < pos[0] or row_begin > pos[0]:
            vim.command("echo \"Not inside a code cell\"")
            return False
        return True
    def run_line(self):
        pos = vim.current.window.cursor
        if self.in_cell(pos) is False:
            return
        code = str(getline(pos[0]).decode('UTF-8'))
        self.shell.run_cell(code, store_history=True)
        cursor(pos[0]+1, pos[1])

    def run_cell_under_cursor(self, down=False):
        pos = vim.current.window.cursor
        cursor(pos)
        row_finish = search("^```[^{]*", "cW")
        row_begin = search("^```\s*{", "bcW")
        code = ""

        if self.in_cell(pos) is False:
            return
        cell = getline(row_begin+1, row_finish-1)
        for line in cell:
            code += line.decode("UTF-8") + "\n"

        if down is False:
            cursor(pos[0], pos[1])
        else:
            cursor(row_finish-1, pos[1])
        self.shell.run_cell(code, store_history=True)

    def run_cell(self, arg=""):
        code = ""
        pos = vim.current.window.cursor
        row_begin = search("^```\s*{"+arg, "bcW")
        if row_begin == 0:
            vim.command("echo \"Cannot find a code cell named " + arg + "\"")
            return
        row_finish = search("^```[^{]*", "cW")
        cell = getline(row_begin+1, row_finish-1)
        for line in cell:
            code += line.decode("UTF-8") + "\n"
        cursor(pos[0], pos[1])
        self.shell.run_cell(code, store_history=True)

    def run_all(self):
        code = ""
        cb = vim.current.buffer()
        all_list = re.findall(r'^```\s*{.*?\n(.*?)^```[^{]*\n', "".join(cb[:]))
        for line in all_list:
            code += line.decode("UTF-8") + "\n"
        self.shell.run_cell(code, store_history=True)

    def print_variable(self, arg=""):
        pos = vim.current.window.cursor
        code = ""
        if arg == "":
            if self.in_cell(pos) is False:
                return
            vim.command("normal viw\"jy")
            var = str(vim.eval("@j"))
        else:
            var = str(arg)

        code = "print(str(" + var + "))"
        self.shell.run_cell(code, store_history=True)

    def get_doc(self, arg=""):
        pos = vim.current.window.cursor
        code = ""
        if arg == "":
            if self.in_cell(pos) is False:
                return
            vim.command("normal viw\"jy")
            var = str(vim.eval("@j"))
        else:
            var = str(arg)

        code = "?" + var
        self.shell.run_cell(code, store_history=True)

    def shutdown_silent(self):
        self.shell.ask_shutdown(silent=True)

    def shutdown_verbose(self):
        self.shell.ask_shutdown(silent=False)

    def restart(self):
        self.shell.ask_restart()


