import vim
import nbformat
import re
from collections import OrderedDict


class VimIpynbFormmater():
    vim_ipynb_nbs = dict()
    vim_ipynb_nodes = dict()

    def to_ipynb(self):
        cb = vim.current.buffer
        cb_name = vim.current.buffer.name

        self.adjust_order(cb, cb_name)

        with open(cb_name, "w") as cf:
            nbformat.write(self.vim_ipynb_nbs[cb_name], cf)

    def from_ipynb(self):
        cb = vim.current.buffer
        cb_name = vim.current.buffer.name

        with open(cb_name) as cf:
            self.vim_ipynb_nbs[cb_name] = (nbformat.read(cf, as_version=4))

        cb[:] = None
        last_row = 1
        cells = OrderedDict()
        for n in range(len(self.vim_ipynb_nbs[cb_name].cells)):
            cell = self.vim_ipynb_nbs[cb_name].cells[n]
            name = cell["cell_type"] + str(n)
            if cell["cell_type"] == "code":
                last_row = self.buffer_append_beauty(
                    cb, last_row, "\n```{" + name + " }")
                last_row = self.buffer_append_beauty(cell["source"] + "\n```")

            elif cell["cell_type"] == "markdown":
                last_row = self.buffer_append_beauty(
                    cb, last_row, "\n#%%{" + name + " }")
                last_row = self.buffer_append_beauty(cell["source"] + "\n")

            cells[name] = self.vim_ipynb_nbs[cb_name].cells[n]
        self.vim_ipynb_nodes[cb_name] = cells

    def buffer_append_beauty(self, cb, last_row, msg=""):
        msg_list = msg.split('\n')
        if cb[last_row - 1] == "":
            cb.append(msg_list, last_row-1)
        else:
            cb.append(msg_list, last_row)
        return last_row + len(msg_list)

    def adjust_order(self, cb, cb_name):
        in_code = False
        new_nb = nbformat.v4.new_notebook()
        new_nb.metadata = self.vim_ipynb_nbs[cb_name].metadata
        new_nb.nbformat = self.vim_ipynb_nbs[cb_name].nbformat
        new_nb.nbformat_minor = self.vim_ipynb_nbs[cb_name].nbformat_minor
        new_cells = OrderedDict()

        for line in cb:
            if not in_code:
                matchObj = re.match(r'^#%%\{(.*?)\s')
                if matchObj:
                    name = matchObj.group(1)
                    if name.isalnum():
                        if name in self.vim_ipynb_nodes[cb_name]:
                            new_cells[name] = self.vim_ipynb_nodes[cb_name][name]
                            new_cells[name]["source"] = ""
                        else:
                            new_cells[name] = nbformat.v4.new_markedown_cell()
                            new_cells[name]["source"] = ""

                    else:
                        raise ValueError(
                            "Cell names should contain only \
                            numbers or letters. Need at least \
                            one letter")
                    continue
                else:
                    matchObj = re.match(r'^```\{(.*?)\s')
                    if matchObj:
                        in_code = True
                        name = matchObj.group(1)
                        if name.isalnum():
                            if name in self.vim_ipynb_nodes[cb_name]:
                                new_cells[name] = self.vim_ipynb_nodes[cb_name][name]
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
                        new_cells[name]["source"] += line
            elif in_code:
                matchObj = re.match(r'^```\s')
                if matchObj:
                    in_code = False
                else:
                    new_cells[name]["source"] += line
        for name in new_cells:
            new_nb.cells.append(new_cells[name])
        self.vim_ipynb_nodes[cb_name] = new_cells
        self.vim_ipynb_nbs[cb_name] = new_nb
