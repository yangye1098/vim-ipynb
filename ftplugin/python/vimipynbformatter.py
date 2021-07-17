""" For extract info from and format .ipynb notebook

"""
from collections import OrderedDict
from nbformat.v4 import (
    nbformat as current_nbformat,
    nbformat_minor as current_nbformat_minor
)
from jupyter_client import kernelspec
import vim
import nbformat
import re

from nbconvert.exporters import (HTMLExporter, MarkdownExporter, PDFExporter,
                                 PythonExporter)

from nbconvert.writers import FilesWriter
from traitlets.config import Config


class VimIpynbFormatter():
    buffer_formatted = False
    vim_ipynb_nb = None
    vim_ipynb_cells = OrderedDict()
    # each formatter is in charge of one buffer
    nb_buffer = None
    kernel_info = {}
    shell = None
    kernel_language = ""
    kernel_specs = {}
    writer = FilesWriter()
    c = Config()
    c.CSSHTMLHeaderPreprocessor.style = 'colorful'
    c.LatexPreprocessor.style = 'colorful'


    def __init__(self):
        pass

    def assign_shell(self, shell):
        self.shell = shell
        self._get_kernel_specs()
        self.update_from_buffer()

    def write_buffer(self):
        vim.command(":write")

    # format methods

    def to_ipynb(self):
        self.update_from_buffer()
        with open(self.nb_buffer.name, "w") as cf:
            nbformat.write(self.vim_ipynb_nb, cf)

    def to_pandoc(self):
        cb_name = self.nb_buffer.name.split('/')[-1]
        markdown_name = cb_name.split('.')[0] + ".pandoc"
        self.update_from_buffer()
        with open(markdown_name, "w") as mf:
            for line in self.nb_buffer:
                if self.match_marker(line, kind='markdown') is None:
                    if self.match_marker(line, kind='code_begin'):
                        mf.write("```" + self.kernel_language + '\n')
                    else:
                        mf.write(line + '\n')

    def to_markdown(self):
        cb_name = self.nb_buffer.name.split('/')[-1]
        notebook_name = cb_name.split('.')[0]
        self.write_buffer()
        markdown_exporter = MarkdownExporter()
        body, resources = markdown_exporter.from_filename(cb_name)
        self.writer.write(body, resources, notebook_name = notebook_name)


    def to_html(self):
        cb_name = self.nb_buffer.name.split('/')[-1]
        notebook_name = cb_name.split('.')[0]
        self.write_buffer()
        html_exporter = HTMLExporter(config=self.c)
        html_exporter.template_file = 'full'
        body, resources = html_exporter.from_filename(cb_name)
        self.writer.write(body, resources, notebook_name = notebook_name)


    def to_pdf(self):
        cb_name = self.nb_buffer.name.split('/')[-1]
        notebook_name = cb_name.split('.')[0]
        self.write_buffer()
        pdf_exporter = PDFExporter(config=self.c)
        body, resources = pdf_exporter.from_filename(cb_name)
        self.writer.write(body, resources, notebook_name = notebook_name)

    def to_code(self):
        if self.kernel_language == 'python':
            suffix = '.py'
        elif self.kernel_language == 'matlab':
            suffix = '.mat'
        else:
            raise NotImplementedError

        cb_name = self.nb_buffer.name.split('/')[-1]
        script_name = cb_name.split('.')[0] + suffix
        self.write_buffer()
        with open(script_name, "w") as sf:
            for name in self.vim_ipynb_cells:
                if self.vim_ipynb_cells[name]['cell_type'] == "code":
                    sf.write(self.vim_ipynb_cells[name]['source'])
                    sf.write('\n\n')




    #output method

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

    # update methods

    def to_buffer(self):
        self.buffer_formatted = True
        self.nb_buffer[:] = None
        last_row = 0
        n_code = 0
        n_mkd = 0
        for n in range(len(self.vim_ipynb_nb.cells)):
            cell = self.vim_ipynb_nb.cells[n]
            if cell["cell_type"] == "code":
                n_code += 1
                name = "code" + str(n_code)
                last_row = self.buffer_append(
                    last_row, "\n```"+self.kernel_language+' '+name)
                last_row = self.buffer_append(
                    last_row, cell["source"] + "\n```")

            elif cell["cell_type"] == "markdown":
                n_mkd += 1
                name = "markdown" + str(n_mkd)
                last_row = self.buffer_append(
                    last_row, "\n#%%" + name)
                last_row = self.buffer_append(
                    last_row, cell["source"])

            self.vim_ipynb_cells[name] = self.vim_ipynb_nb.cells[n]


    def read_ipynb(self):
        # open .ipynb file
        self.nb_buffer = vim.current.buffer
        cb_name = self.nb_buffer.name
        try:
            with open(cb_name) as cf:
                try:
                    self.vim_ipynb_nb = nbformat.read(
                        cf, as_version=current_nbformat)
                    try:
                        self.kernel_language = self.vim_ipynb_nb[
                            "metadata"]["language_info"]["name"]
                    except:
                        # language_info is missing, set to default
                        self.kernel_language = "python"
                    self._get_kernel_specs()
                except nbformat.reader.NotJSONError:
                    raise
                finally:
                    pass
        except FileNotFoundError:
            self.vim_ipynb_nb = nbformat.v4.new_notebook()

    def update_from_buffer(self):
        if self.shell is not None:
            self.update_notebook_info()
            if self.buffer_formatted:
                self.cells_from_buffer()
                self.vim_ipynb_nb.cells = []
                for cell in self.vim_ipynb_cells:
                    self.vim_ipynb_nb.cells.append(self.vim_ipynb_cells[cell])
        else:
            vim.command("echo \"No running kernel. Please start one using :StartKernel(<kernel_name>)\" ")

    def new_notebook(self):
        self.vim_ipynb_nb = nbformat.v4.new_notebook()
        self.update_notebook_info()

    def cells_from_buffer(self):
        if not self.buffer_formatted:
            return
        in_code = False
        new_cells = OrderedDict()
        name = None
        nrow = len(self.nb_buffer)

        for l in range(nrow):
            if not in_code:
                matchObj = self.match_marker(self.nb_buffer[l], kind='markdown')
                if matchObj:
                    self.trim_n(name, new_cells)
                    name = matchObj.group(1)
                    try:
                        if self.check_name(name, new_cells):
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
                    matchObj = self.match_marker(self.nb_buffer[l], kind='code_begin')
                    if matchObj:
                        self.trim_n(name, new_cells)
                        in_code = True
                        name = matchObj.group(1)
                        try:
                            if self.check_name(name, new_cells):
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
                matchObj = self.match_marker(self.nb_buffer[l], kind='code_end')
                if matchObj:
                    in_code = False
                else:
                    new_cells[name]["source"] += (self.nb_buffer[l] + '\n')
        self.trim_n(name, new_cells)
        self.vim_ipynb_cells = new_cells

    # utility methods

    """
    match markdown begin marker, code begin marker and code end marker.
    kind = "markdown", "code_begin", or "code_end"
    """
    def match_marker(self, line, kind):
        markdown_cell_pattern = re.compile(r'^#%%(?:(.*?)$|(.*?)\s(.*?)$)')
        code_cell_begin_pattern = \
            re.compile(r'^```(?:' + self.kernel_language +
                       ')\s(?:(.*?)$|(.*?)\s(.*?)$)')
        code_cell_stop_pattern = re.compile(r'^```\s*$')
        if kind == 'markdown':
            return markdown_cell_pattern.match(line)
        elif kind == 'code_begin':
            return code_cell_begin_pattern.match(line)
        elif kind == 'code_end':
            return code_cell_stop_pattern.match(line)
        else:
            raise ValueError



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


    def get_kernel_name(self):
        if self.kernel_language:
            return self.kernel_specs[self.kernel_language]["name"]
        else:
            return ""

    def update_notebook_info(self):
        self.vim_ipynb_nb.nbformat = current_nbformat
        self.vim_ipynb_nb.nbformat_minor = current_nbformat_minor
        if self.shell is not None:
            self.vim_ipynb_nb.metadata["language_info"] = \
                self.shell.kernel_info["language_info"]
            self.kernel_language = \
                self.shell.kernel_info["language_info"]["name"]
            self.vim_ipynb_nb.metadata["kernelspec"] = \
                self.kernel_specs[self.kernel_language]

    """
    Get all kernel specs installed
    """
    def _get_kernel_specs(self):
        kernelspec_manager = kernelspec.KernelSpecManager()
        kernelspec_info = kernelspec_manager.get_all_specs()
        for (key, value) in kernelspec_info.items():
            self.kernel_specs[value["spec"]["language"]] = {"display_name":"", \
                    "language":"", "name":""}
            self.kernel_specs[value["spec"]["language"]]["display_name"] = \
                value["spec"]["display_name"]
            self.kernel_specs[value["spec"]["language"]]["language"] = \
                value["spec"]["language"]
            self.kernel_specs[value["spec"]["language"]]["name"] = \
                key

