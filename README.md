# vim-jupyter
 
 vim plugin for viewing, editting jupyter notebook, running code cells and
 converting to markdown, pdf. 


# Requirement

1. vim with python3 integrated
2. vim-pandoc and vim-pandoc-syntax plugin for converting .ipynb files to  grammar support

# Features

1. Open and edit .ipynb files with corresponding backend kernel.
2. Different kernels support (python and matlab for now).
3. Syntax highlighting support through vim-pandoc-syntax.
4. Creating markdown and code cells. 
5. Running codes in code cells.
6. Converting .ipynb files into pandoc-markdown pdf. (Todo)


# Syntax 

## Markdown cell 

    #%%<MardownCellName>

## Code cell

    ```<KernelLanguage> <CellName>
    some codes
    ```


# Usage

## New .ipynb files

After creating a new .ipynb file, a kernel must be explicitly started using 

    :StartKernel <kernelname>

## Kernel Related Commands

    :StartKernel <kernelname> Start a kernel
    :ConnectToKernel <jsonfile> Connect to an existing kernel specified by <jsonfile>
    :ConnectToPreviousKernel Connect to a most recented created kernel 
    :KernelShutdown Shutdown current kernel
    :KernelRestart Restart current kernel 

## Run Code Cells

For running current code cell command, code can only be run when cursor is inside a code cell. 

    <space>  Run current line 
    <localleader>a Abort Run line buffer
    <localleader>cc Run current cell 
    <localleader>cd Run current cell and go to nex cell
    <localleader>cn <n> Run number n cell
    <localleader>r Run all code cells

## Other Commands

    <localleader>p: print variable under cursor
    <localleader>pn <var>: print variable <var>
    <localleader>h: get help under cursor
    <localleader>hn <name>: get help for <name>


## Convert Filetype Commands

    :ToPandoc 
    :ToHtml
    :ToMd
    :ToPdf

## Output related Commands
    :ClearAll Clear all output from code cells.
    


# Configuration Option

## Open ipynb as raw ipynb json format 

    let g:ipynb_convert_on_start=0


# Comment

This is a primary plugin and still under developing. Basic functionalities are
working with potential bugs.
