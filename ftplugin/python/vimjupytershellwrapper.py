import vim
import re
import sys


getline = vim.Function('getline')
cursor = vim.Function('cursor')
search = vim.Function('search')

"""
Class for handling get code for shell to send to kernel from vim buffer.
"""
class VimJupyterShellWrapper():

    shell = None
    vim_ipynb_formatter = None

    def __init__(self, shell):
        self.shell = shell
        self.vim_ipynb_formatter = shell.vim_ipynb_formatter

    def in_cell(self, pos):
        cursor(pos[0], pos[1])
        row_finish = search(r"^```\s*$", "cW")
        row_begin = search(r"^```\w\+", "bcW")
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

    def run_line_abort(self):
        self.shell.run_line_abort()
        return

    def run_cell_under_cursor(self, down=False):
        vim.command(":write")
        pos = vim.current.window.cursor
        cursor(pos)
        row_finish = search(r"^```\s*$", "cW")
        row_begin = search(r"^```\w\+", "bcW")
        code = ""

        if self.in_cell(pos) is False:
            return None
        cell = vim.current.buffer[row_begin:row_finish-1]
        for line in cell:
            code += line + "\n"

        if down is False:
            cursor(pos[0], pos[1])
        else:
            cursor(row_finish-1, pos[1])

        name = re.match(r"^```.*?\s+(.*?)[\s$]",
                        vim.current.buffer[row_begin-1] + '\n').group(1)
        self.shell.run_cell(code, name, store_history=True)

    def run_cell(self, arg=""):
        code = ""
        pos = vim.current.window.cursor
        row_begin = search("^```"
                           + self.vim_ipynb_formatter.kernel_language
                           + r"\s"+arg+r"[\s\n]", "c")
        if row_begin == 0:
            vim.command("echo \"Cannot find a code cell named " + arg + "\"")
            return
        row_finish = search(r"^```\s*$", "cW")
        cell = vim.current.buffer[row_begin: row_finish-1]
        for line in cell:
            code += line + "\n"
        cursor(pos[0], pos[1])
        self.shell.run_cell(code, arg, store_history=True)

    def run_all(self):
        self.vim_ipynb_formatter.update_from_buffer()
        cells = self.vim_ipynb_formatter.vim_ipynb_cells
        for name in cells:
            if cells[name]['cell_type'] == "code":
                self.shell.run_cell(cells[name]['source'], name,
                                    clear_display=False, store_history=True)

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
        self.shell.run_cell(code,  store_history=True)

    def shutdown_silent(self):
        self.shell.ask_shutdown(silent=True)

    def shutdown_verbose(self):
        self.shell.ask_shutdown(silent=False)

    def restart(self):
        self.shell.ask_restart()
