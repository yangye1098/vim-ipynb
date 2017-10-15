
import vim


class VimJupterDisplayManager():
    """ Deal with the output display in Vim """
    prompt = ""

    stdout_buffer_name = "Vim-Jupter-Output"
    stdout_buffer = None
    stdout_ratio = 3
    stdout_dir = "above"

    interactive_buffer_name = "Vim-Jupter-Interactive"
    interactive_buffer = None
    interactive_ratio = 3
    interactive_dir = "below"

    stdin_buffer_name = "Vim-Jupter-Input"
    stdin_buffer = None

    # ratio for window split
    w_origin_ID = 0

    # vim function handle
    bufwinid = vim.Function("bufwinid")
    win_gotoid = vim.Function("win_gotoid")

    def __init__(self):
        pass

    def open_window(self, kind="stdout"):
        """ Open window to interact with user.

        """
        self.w_origin_ID = vim.eval("win_getid()")
        if kind == "stdout":
            cmd = self.open_stdout_window()
            vim.command(cmd)
            self.stdout_buffer = vim.current.buffer
            self.clear_stdout_buffer()
        elif kind == "stdin":
            cmd = self.open_stdin_window()
            vim.command(cmd)
            self.stdin_buffer = vim.current.buffer
            self.stdin_buffer[:] = None
        elif kind == "interactive":
            cmd = self.open_interactive_window()
            vim.command(cmd)
            self.interactive_buffer = vim.current.buffer
            self.interactive_buffer[:] = None

    def open_stdout_window(self, ratio=None, wdir=None):
        if ratio is None:
            ratio = self.stdout_ratio

        if wdir is None:
            wdir = self.stdout_dir

        interactive_id = self.bufwinid(self.interactive_buffer_name)
        if interactive_id != -1:
            self.close_interactive_window()

        height = vim.current.window.height/ratio
        width = vim.current.window.width/ratio

        if wdir == "above":
            cmd = "aboveleft " + str(height) + "split "
        elif wdir == "below":
            cmd = "belowright " + str(height) + "split "
        elif wdir == "left":
            cmd = "leftabove " + str(width) + "vsplit "
        elif wdir == "right":
            cmd = "rightbelow " + str(width) + "vsplit "

        stdout_id = self.bufwinid(self.stdout_buffer_name)

        if stdout_id != -1:
            self.win_gotoid(stdout_id)
            cmd = "set noreadonly modifiable"
        else:
            cmd += "+set\ noreadonly\ modifiable" + \
                self.stdin_buffer_name
        return cmd

    def handle_prompt(self, prompt):
        self.prompt = prompt

    def handle_stdout(self, msg=""):
        output = self.prompt + msg
        if output:
            self.stdout_buffer.append(msg.split('\n'))
        self.prompt = ""

    def clear_stdout_buffer(self):
        if self.stdout_buffer is not None:
            self.stdout_buffer[:] = None

    def finish_stdout(self):
        cmd = "set readonly nomodifiable"
        vim.command(cmd)
        self.win_gotoid(self.w_origin_ID)

    def open_stdin_window(self):
        stdin_id = self.bufwinid(self.stdin_buffer_name)
        if stdin_id != -1:
            self.win_gotoid(stdin_id)
            cmd = "set noreadonly modifiable"
        else:
            cmd = "split +set\ noreadonly\ modifiable " + \
                self.stdin_buffer_name
        return cmd

    def handle_stdin(self, prompt):
        vim.command("set tw=0")
        self.stdin_buffer.append(prompt)


    def close_stdin_window(self):
        stdin_id = self.bufwinid(self.stdin_buffer_name)
        if stdin_id != -1:
            self.win_gotoid(stdin_id)
            vim.command("q!")

    def open_interactive_window(self, ratio=None, wdir=None):
        if ratio is None:
            ratio = self.interactive_ratio

        if wdir is None:
            wdir = self.interactive_dir

        height = vim.current.window.height/self.interactive_ratio
        width = vim.current.window.width/self.interactive_ratio

        if wdir == "above":
            cmd = "aboveleft " + str(height) + "split "
        elif wdir == "below":
            cmd = "belowright " + str(height) + "split "
        elif wdir == "left":
            cmd = "leftabove " + str(width) + "vsplit "
        elif wdir == "right":
            cmd = "rightbelow " + str(width) + "vsplit "

        interactive_id = self.bufwinid(self.interactive_buffer_name)

        if interactive_id != -1:
            self.win_gotoid(interactive_id)
            cmd = "set noreadonly modifiable"
        else:
            cmd += "+set\ noreadonly\ modifiable" + \
                self.interactive_buffer_name
        return cmd

    def handle_interactive(self, msg):
        output = self.prompt + msg

        self.prompt = ""

    def close_interactive_window(self):
        stdin_id = self.bufwinid(self.stdin_buffer_name)
        if stdin_id != -1:
            self.win_gotoid(stdin_id)
            vim.command("q!")

    def change_ratio(self, ratio):
        self.ratio = ratio
