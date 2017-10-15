import vim


def run_line(shell):
    print("run line")
    vim.command(".y j")
    vim.command("j")
    code = vim.eval("@j")
    shell.run_cell(code, store_history=True)
