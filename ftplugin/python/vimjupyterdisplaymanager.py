
import vim


class VimJupterDisplayManager():
    """ Deal with the output display in Vim """

    stdout_buffer_name = "Vim-Jupter-Output"
    stdout_buffer = None
    stdout_ratio = 3
    stdout_dir = "above"
    stdout_last_row = 1

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
            self.stdout_last_row = vim.current.window.cursor[0]
        elif kind == "stdin":
            cmd = self.open_stdin_window()
            vim.command(cmd)
            self.stdin_buffer = vim.current.buffer
            self.stdin_buffer[:] = None

    def open_stdout_window(self, ratio=None, wdir=None):
        if ratio is None:
            ratio = self.stdout_ratio

        if wdir is None:
            wdir = self.stdout_dir

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
            cmd += "+set\ noreadonly\ modifiable " + \
                self.stdout_buffer_name
        return cmd

    def handle_stdout(self, msg=""):
        if msg:
            msg_list = msg.split('\n')
            if self.stdout_buffer[self.stdout_last_row - 1] != '':
                self.stdout_buffer.append(msg_list)
            else:
                self.stdout_buffer.append(msg_list,
                                          self.stdout_last_row - 1)
            self.stdout_last_row += len(msg_list)

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
            cmd = "belowright 2split +set\ noreadonly\ modifiable " + \
                self.stdin_buffer_name
        return cmd

    def handle_stdin(self, prompt):
        vim.command("set tw=0")
        self.stdin_buffer.append(prompt)

    def handle_password(self, prompt):
        vim.command("set tw=0")
        self.stdin_buffer.append(prompt)

    def close_stdin_window(self):
        stdin_id = self.bufwinid(self.stdin_buffer_name)
        if stdin_id != -1:
            self.win_gotoid(stdin_id)
            vim.command("q!")

    def change_ratio(self, ratio):
        self.ratio = ratio

    def echom(msg):
        vim.command("echom " + msg)
