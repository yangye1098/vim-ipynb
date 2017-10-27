""" For format .ipynb notebook

"""
from collections import OrderedDict
from nbformat.v4 import (
    nbformat as current_nbformat,
    nbformat_minor as current_nbformat_minor
)

import vim
import nbformat
import re


class VimIpynbFormatter():
    vim_ipynb_nb = None
    vim_ipynb_cells = OrderedDict()
    # each formatter is in charge of one buffer
    nb_buffer = None
    kernel_info = {}
    shell = None
    kernel_language = ""
    language_supported = ["python"]
    language_pattern = ""
    for language in language_supported:
        language_pattern += language + '|'
    language_pattern = language_pattern.rstrip('|')

    def __init__(self, shell=None, ):
        self.shell = shell

    def to_ipynb(self):
        self.update_from_buffer()

        with open(self.nb_buffer.name, "w") as cf:
            nbformat.write(self.vim_ipynb_nb, cf)

    def to_markdown(self):
        cb_name = self.nb_buffer.name
        markdown_name = cb_name.split('.')(0) + ".md"
        self.update_from_buffer()
        markdown_cell_pattern = re.compile(r'^#%%(?:(.*?)$|(.*?)\s(.*?)$)')

        with open(markdown_name, "w") as mf:
            for line in self.nb_buffer:
                if markdown_cell_pattern.match(line) is None:
                    mf.write(line)

    def embed_output(self, name, msg):
        if name == '':
            return
        if name not in self.vim_ipynb_cells:
            self.update_from_buffer()

        output = nbformat.v4.output_from_msg(msg)
        self.vim_ipynb_cells[name]['outputs'].append(output)

    def clear_all_output(self):
        for name in self.vim_ipynb_cells:
            if self.vim_ipynb_cells[name]['cell_type'] == "code":
                self.vim_ipynb_cells[name]['outputs'] = []

    def clear_output(self, name):
        if name == '':
            return
        if name not in self.vim_ipynb_cells:
            self.update_from_buffer()

        self.vim_ipynb_cells[name]['outputs'] = []

    def from_ipynb(self):
        # open .ipynb file
        self.nb_buffer = vim.current.buffer
        cb_name = self.nb_buffer.name
        try:
            with open(cb_name) as cf:
                try:
                    self.vim_ipynb_nb = nbformat.read(
                        cf, as_version=current_nbformat)
                except nbformat.reader.NotJSONError:
                    self.vim_ipynb_nb = self.nb_from_buffer()
                finally:
                    pass
        except FileNotFoundError:
            self.vim_ipynb_nb = self.nb_from_buffer()
        self.kernel_language = self.vim_ipynb_nb[
                "metadata"]["language_info"]["name"]
        self.nb_buffer[:] = None
        last_row = 0
        cells = OrderedDict()
        n_code = 0
        n_mkd = 0
        for n in range(len(self.vim_ipynb_nb.cells)):
            cell = self.vim_ipynb_nb.cells[n]
            if cell["cell_type"] == "code":
                n_code += 1
                name = " code" + str(n_code)
                last_row = self.buffer_append(
                    last_row, "\n```" + self.kernel_language + name)
                last_row = self.buffer_append(
                    last_row, cell["source"] + "\n```")

            elif cell["cell_type"] == "markdown":
                n_mkd += 1
                name = "markdown" + str(n_mkd)
                last_row = self.buffer_append(
                    last_row, "\n#%%" + name)
                last_row = self.buffer_append(
                    last_row, cell["source"])

            cells[name] = self.vim_ipynb_nb.cells[n]
        self.vim_ipynb_cells = cells

    def update_from_buffer(self):
        self.vim_ipynb_nb.metadata["language_info"] \
            = self.shell.kernel_info["language_info"]
        self.vim_ipynb_nb.nbformat = current_nbformat
        self.vim_ipynb_nb.nbformat_minor = current_nbformat_minor
        self.cells_from_buffer()
        self.vim_ipynb_nb.cells = []
        for cell in self.vim_ipynb_cells:
            self.vim_ipynb_nb.cells.append(self.vim_ipynb_cells[cell])

    def nb_from_buffer(self):
        new_nb = nbformat.v4.new_notebook()
        if self.shell is not None:
            new_nb.metadata["language_info"] = \
                self.shell.kernel_info["language_info"]
        new_nb.nbformat = current_nbformat
        new_nb.nbformat_minor = current_nbformat_minor
        self.cells_from_buffer()
        for cell in self.vim_ipynb_cells:
            new_nb.cells.append(self.vim_ipynb_cells[cell])
        return new_nb

    def cells_from_buffer(self):
        in_code = False
        new_cells = OrderedDict()
        name = None
        nrow = len(self.nb_buffer)
        language_pattern = r"python"
        code_cell_start_pattern = \
            re.compile(r'^```(?:' + language_pattern +
                       ')\s(?:(.*?)$|(.*?)\s(.*?)$)')
        code_cell_stop_pattern = re.compile(r'^```\s*$')
        markdown_cell_pattern = re.compile(r'^#%%(?:(.*?)$|(.*?)\s(.*?)$)')

        for l in range(nrow):
            if not in_code:
                matchObj = markdown_cell_pattern.match(self.nb_buffer[l])
                if matchObj:
                    self.trim_n(name, new_cells)
                    name = matchObj.group(1)
                    try:
                        if self.check_name:
                            if name in self.vim_ipynb_cells:
                                new_cells[name] = \
                                        self.vim_ipynb_cells[name]
                                new_cells[name]["source"] = ""
                            else:
                                new_cells[name] =\
                                        nbformat.v4.new_markdown_cell()
                                new_cells[name]["source"] = ""
                    except ValueError:
                        raise
                else:
                    matchObj = code_cell_start_pattern.match(self.nb_buffer[l])
                    if matchObj:
                        self.trim_n(name, new_cells)
                        in_code = True
                        name = matchObj.group(1)
                        try:
                            if self.check_name:
                                if name in self.vim_ipynb_cells:
                                    new_cells[name] = \
                                        self.vim_ipynb_cells[name]
                                    new_cells[name]["source"] = ""
                                else:
                                    new_cells[name] = \
                                            nbformat.v4.new_code_cell()
                                    new_cells[name]["source"] = ""

                        except ValueError:
                            raise
                    else:
                        if name is not None:
                            new_cells[name]["source"] += (
                                    self.nb_buffer[l] + '\n')
            elif in_code:
                matchObj = code_cell_stop_pattern.match(self.nb_buffer[l])
                if matchObj:
                    in_code = False
                else:
                    new_cells[name]["source"] += (self.nb_buffer[l] + '\n')
        self.trim_n(name, new_cells)
        self.vim_ipynb_cells = new_cells

    def trim_n(self, name, cells):
        if name is not None:
            # trim the last "\n" appended in from_ipynb
            cells[name]["source"] = \
                    cells[name]["source"][:-2]

    def check_name(self, name, cells):
        if name in cells:
            raise ValueError("Cell name already exists.")
            return False
        if name.isalnum():
            return True
        else:
            return False
            raise ValueError(
                            "Cell names should contain only \
                            numbers or letters. Need at least \
                            one letter: {0}".format(name))
        return False

    def buffer_append(self, last_row, msg=""):
        msg_list = msg.split("\n")
        self.nb_buffer.append(msg_list, last_row)
        return last_row + len(msg_list)
