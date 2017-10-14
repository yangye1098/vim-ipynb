
if !has('python3')
    " exit if python3 is not available.
    " XXX: raise an error message here
    finish
end

python3 << EOF
import vim
import nbformat as nf

nb = nf.read(vim.current.buffer.name)
cells = nb.cells

EOF
