import vim
import nbformat
from nbformat.v4 import (
    nbformat as current_nbformat,
    nbformat_minor as current_nbformat_minor
)
import re
from collections import OrderedDict


class VimIpynbFormatter():
    vim_ipynb_nb = None
    vim_ipynb_cells = OrderedDict()
    kernel_info = {}
    shell = None

    def __init__(self, shell=None):
        self.shell = shell

    def to_ipynb(self):
        cb = vim.current.buffer
        cb_name = vim.current.buffer.name

        self.update_from_buffer(cb)

        with open(cb_name, "w") as cf:
            nbformat.write(self.vim_ipynb_nb, cf)

    def from_ipynb(self):
        cb = vim.current.buffer
        cb_name = vim.current.buffer.name

        with open(cb_name) as cf:
            try:
                self.vim_ipynb_nb = nbformat.read(
                    cf, as_version=current_nbformat)
            except nbformat.reader.NotJSONError:
                self.vim_ipynb_nb = self.nb_from_buffer(cb)
            finally:
                pass

        cb[:] = None
        last_row = 1
        cells = OrderedDict()
        for n in range(len(self.vim_ipynb_nb.cells)):
            cell = self.vim_ipynb_nb.cells[n]
            name = cell["cell_type"] + str(n)
            if cell["cell_type"] == "code":
                last_row = self.buffer_append_beauty(
                    cb, last_row, "\n```{" + name + " }")
                last_row = self.buffer_append_beauty(
                    cb, last_row, cell["source"] + "\n```")

            elif cell["cell_type"] == "markdown":
                last_row = self.buffer_append_beauty(
                    cb, last_row, "\n#%%{" + name + " }")
                last_row = self.buffer_append_beauty(
                    cb, last_row, cell["source"])

            cells[name] = self.vim_ipynb_nb.cells[n]
        self.vim_ipynb_cells = cells

    def update_from_buffer(self, cb):
        self.vim_ipynb_nb.metadata["language_info"] \
            = self.shell.kernel_info["language_info"]
        self.vim_ipynb_nb.nbformat = current_nbformat
        self.vim_ipynb_nb.nbformat_minor = current_nbformat_minor
        new_cells = self.cells_from_buffer(
            cb, self.vim_ipynb_cells)
        self.vim_ipynb_nb.cells = []
        for cell in new_cells:
            self.vim_ipynb_nb.cells.append(new_cells[cell])

    def nb_from_buffer(self, cb):
        new_nb = nbformat.v4.new_notebook()
        if self.shell is not None:
            new_nb.metadata["language_info"] = \
                self.shell.kernel_info["language_info"]
        new_nb.nbformat = current_nbformat
        new_nb.nbformat_minor = current_nbformat_minor
        new_cells = self.cells_from_buffer(cb, old_cells=dict())
        for cell in new_cells:
            new_nb.cells.append(new_cells[cell])
        return new_nb

    def cells_from_buffer(self, cb, old_cells):
        in_code = False
        new_cells = OrderedDict()
        name = None

        for line in cb:
            if not in_code:
                matchObj = re.match(r'^#%%\{(.*?)[\s\}]', line)
                if matchObj:
                    if name is not None:
                        new_cells[name]["source"] = \
                            new_cells[name]["source"][:-2]

                    name = matchObj.group(1)
                    if name.isalnum():
                        if name in old_cells:
                            new_cells[name] = old_cells[name]
                            new_cells[name]["source"] = ""
                        else:
                            new_cells[name] = nbformat.v4.new_markdown_cell()
                            new_cells[name]["source"] = ""

                    else:
                        raise ValueError(
                            "Cell names should contain only \
                            numbers or letters. Need at least \
                            one letter")
                    continue
                else:
                    matchObj = re.match(r'^```\{(.*?)[\s\}]', line)
                    if matchObj:
                        if name is not None:
                            new_cells[name]["source"] \
                                = new_cells[name]["source"][:-2]
                        in_code = True
                        name = matchObj.group(1)
                        if name.isalnum():
                            if name in old_cells:
                                new_cells[name] = old_cells[name]
                                new_cells[name]["source"] = ""
                            else:
                                new_cells[name] = nbformat.v4.new_code_cell()
                                new_cells[name]["source"] = ""

                        else:
                            raise ValueError(
                                "Cell names should contain only \
                                numbers or letters. Need at least \
                                one letter")
                        continue
                    else:
                        if name is not None:
                            new_cells[name]["source"] += line + "\n"
            elif in_code:
                matchObj = re.match(r'^```\s*', line)
                if name is not None:
                    new_cells[name]["source"] = \
                        new_cells[name]["source"][:-2]
                if matchObj:
                    in_code = False
                else:
                    new_cells[name]["source"] += line + "\n"
        return new_cells

    def buffer_append_beauty(self, cb, last_row, msg=""):
        msg_list = msg.split('\n')
        if cb[last_row - 1] == "":
            cb.append(msg_list, last_row-1)
        else:
            cb.append(msg_list, last_row)
        return last_row + len(msg_list)
