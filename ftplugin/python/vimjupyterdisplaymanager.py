
import vim


class VimJupterDisplayManager():
    """ Deal with the output display in Vim """

    buffer_name = ""
    align = -1
    ansiesc_on = False

    stdout_buffer_name = ""
    stdout_id = 0
    stdout_buffer = None
    stdout_ratio = 3
    stdout_dir = "above"
    stdout_last_row = 0

    # ratio for window split
    w_origin_ID = 0

    # vim function handle
    bufwinid = vim.Function("bufwinid")
    win_gotoid = vim.Function("win_gotoid")

    def __init__(self):
        pass

    def open_window(self, kind="stdout", clear_display=True):
        """ Open window to interact with user.

        """
        self.buffer_name = vim.current.buffer.name
        self.w_origin_ID = vim.eval("win_getid()")
        if kind == "stdout":
            self.open_stdout_window(clear_display)

    def open_stdout_window(self, clear_display=True):
        ratio = self.stdout_ratio
        wdir = self.stdout_dir

        self.stdout_buffer_name = self.buffer_name + "-Vim-Jupyter-Output"
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
            vim.command(cmd)
        else:
            cmd += "+set\ noreadonly\ modifiable " + \
                self.stdout_buffer_name
            vim.command(cmd)
            if self.ansiesc_on is False:
                vim.command("AnsiEsc")
                self.ansiesc_on = True
        self.stdout_buffer = vim.current.buffer
        if clear_display:
            self.clear_stdout_buffer()
            self.stdout_last_row = vim.current.window.cursor[0] - 1
            print(self.stdout_last_row)

    def close_stdout_window(self):
        stdout_id = self.bufwinid(self.stdout_buffer_name)
        if stdout_id != -1:
            self.win_gotoid(stdout_id)
        vim.command("q!")

    def handle_continous(self, lines=""):
        """ Handle the display of continue lines
        """
        self.open_window("stdout")
        self.handle_stdout(lines + " ...")
        self.finish_stdout()

    def handle_stdout(self, msg=""):
        if msg:
            msg = msg.rstrip()
            msg_list = msg.split('\n')
            for n in range(len(msg_list)):
                if self.align >= 0:
                    msg_list[n] = ' '*(self.align) + '> ' + msg_list[n]

            self.stdout_buffer.append(msg_list, self.stdout_last_row)
            self.stdout_last_row += len(msg_list)
            self.align = -1

    def handle_prompt(self, prompt=""):
        if prompt:
            self.align = prompt.lstrip().find(":")
            msg_list = prompt.split('\n')
            self.stdout_buffer.append(msg_list, self.stdout_last_row)
            self.stdout_last_row += len(msg_list)

    def clear_stdout_buffer(self):
        if self.stdout_buffer is not None:
            self.stdout_buffer[:] = None

    def finish_stdout(self):
        cmd = "set readonly nomodifiable"
        if self.stdout_last_row == 0:
            self.handle_stdout("<No Output>")
        vim.command(cmd)
        self.win_gotoid(self.w_origin_ID)

    def handle_stdin(self, prompt):
        f = vim.Function("input")
        return f(prompt).decode('utf-8')

    def handle_password(self, prompt):
        f = vim.Function("inputsecret")
        return f(prompt).decode('utf-8')

    def handle_confirm(self, msg, choice_list):
        f = vim.Function("input")
        choice = f(msg).decode('utf-8')
        while(choice not in choice_list):
            choice = f("Please choose again, " + msg)
        return choice_list.index(choice)

    def change_ratio(self, ratio):
        self.ratio = ratio
