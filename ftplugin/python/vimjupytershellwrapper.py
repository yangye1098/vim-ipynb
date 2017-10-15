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


def shutdown_silent(shell):
    shell.ask_shutdown(silent=True)


del shutdown_verbose(shell)
    shell.ask_shutdown(silent=False)


def restart(shell):
    shell.ask_restart()

