import vim


def run_line(shell):
    vim.command(".y j")
    vim.command("j")
    code = vim.eval("@j")
    shell.run_cell(code, store_history=True)

def run_cell_under_cursor(shell):

    code = vim.eval("@j")
    shell.run_cell(code, store_history=True)


def run_cell(shell):
    code = vim.eval("@j")
    shell.run_cell(code, store_history=True)


def shutdown(shell):
    shell.ask_shutdown(restart=False)


def restart(shell):
    shell.ask_restart()

