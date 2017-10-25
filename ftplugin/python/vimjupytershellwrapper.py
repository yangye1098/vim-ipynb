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
        row_finish = search("^```\\s*$", "cW")
        row_begin = search("^```\\w+", "bcW")
        cursor(pos[0], pos[1])
        if row_finish <= pos[0] or row_begin >= pos[0]:
            vim.command("echo \"Not inside a code cell\"")
            return False
        return True

    def run_line(self):
        pos = vim.current.window.cursor
        if self.in_cell(pos) is False:
            return
        line = vim.current.buffer[pos[0]-1]
        self.shell.run_line(line, store_history=True)
        cursor(pos[0]+1, pos[1])

    def run_cell_under_cursor(self, down=False):
        pos = vim.current.window.cursor
        cursor(pos)
        row_finish = search("^```\\s*$", "cW")
        row_begin = search("^```\\w\+", "bcW")
        code = ""

        if self.in_cell(pos) is False:
            return
        cell = vim.current.buffer[row_begin:row_finish-1]
        for line in cell:
            code += line + "\n"

        if down is False:
            cursor(pos[0], pos[1])
        else:
            cursor(row_finish-1, pos[1])
        self.shell.run_cell(code, store_history=True)

    def run_cell(self, arg=""):
        code = ""
        pos = vim.current.window.cursor
        row_begin = search("^```"+self.shell.kernel_language+"\\s"+arg, "c")
        if row_begin == 0:
            vim.command("echo \"Cannot find a code cell named " + arg + "\"")
            return
        row_finish = search("^```\\s*$", "cW")
        cell = vim.current.buffer[row_begin: row_finish-1]
        for line in cell:
            code += line + "\n"
        cursor(pos[0], pos[1])
        self.shell.run_cell(code, store_history=True)

    def run_all(self):
        code = ""
        cb = vim.current.buffer
        text = ""
        for line in cb:
            text += line + "\n"
        all_list = re.findall(r'^```' +
                              self.shell.kernel_info["language_info"]["name"] +
                              '\s.*?$\n((?:.*?$\n)*?)^```\s*$\n', text, re.M)
        for cell in all_list:
            code += cell
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


