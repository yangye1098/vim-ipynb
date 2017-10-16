"""IPython terminal interface using prompt_toolkit in place of readline"""
from __future__ import print_function

import base64
import errno
import sys
from io import BytesIO
import os
import signal
import subprocess
import time

try:
    from queue import Empty  # Py 3
except ImportError:
    from Queue import Empty  # Py 2

from zmq import ZMQError
from IPython.core import page
from ipython_genutils.tempdir import NamedFileInTemporaryDirectory
from traitlets import (Bool, Integer, Float, Unicode, List, Dict, Enum,
                       Instance, Any)
from traitlets.config import SingletonConfigurable

from jupyter_console.zmqhistory import ZMQHistoryManager

sys.path.append("/home/eric/.vim/myplugin/vim-ipynb/ftplugin/python/")

from _version import __version__
from vimjupyterdisplaymanager import VimJupterDisplayManager


class VimJupyterShell(SingletonConfigurable):
    """ Modified from ZMQTerminalInteractiveShell, rewrite handler functions for
        handling data inside the Vim
    """
    readline_use = False

    _executing = False
    _execution_state = Unicode('')
    _pending_clearoutput = False
    _eventloop = None
    own_kernel = False  # Changed by ZMQTerminalIPythonApp

    editing_mode = Unicode(
        'emacs', config=True,
        help="Shortcut style to use at the prompt. 'vi' or 'emacs'.",
    )

    highlighting_style = Unicode(
        '', config=True,
        help="The name of a Pygments style to use for syntax highlighting"
    )

    highlighting_style_overrides = Dict(
        config=True,
        help="Override highlighting format for specific tokens"
    )

    true_color = Bool(
        False, config=True,
        help=("Use 24bit colors instead of 256 colors in prompt highlighting. "
              "If your terminal supports true color, the following command "
              "should print 'TRUECOLOR' in orange: "
              "printf \"\\x1b[38;2;255;100;0mTRUECOLOR\\x1b[0m\\n\"")
    )

    history_load_length = Integer(
        1000, config=True,
        help="How many history items to load into memory"
    )

    banner = Unicode(
        'Vim Jupyter console {version}\n\n{kernel_banner}', config=True,
        help=("Text to display before the first prompt. Will be formatted with "
              "variables {version} and {kernel_banner}.")
    )

    kernel_timeout = Float(
        60, config=True,
        help="""Timeout for giving up on a kernel (in seconds).

        On first connect and restart, the console tests whether the
        kernel is running and responsive by sending kernel_info_requests.
        This sets the timeout in seconds for how long the kernel can take
        before being presumed dead.
        """
    )

    vim_display_manager = VimJupterDisplayManager()

    image_handler = Enum(
        ('PIL', 'stream', 'tempfile', 'callable'),
        'PIL', config=True, allow_none=True, help="""
        Handler for image type output.  This is useful, for example,
        when connecting to the kernel in which pylab inline backend is
        activated.  There are four handlers defined.  'PIL': Use
        Python Imaging Library to popup image; 'stream': Use an
        external program to show the image.  Image will be fed into
        the STDIN of the program.  You will need to configure
        `stream_image_handler`; 'tempfile': Use an external program to
        show the image.  Image will be saved in a temporally file and
        the program is called with the temporally file.  You will need
        to configure `tempfile_image_handler`; 'callable': You can set
        any Python callable which is called with the image data.  You
        will need to configure `callable_image_handler`.
        """
    )

    stream_image_handler = List(
        config=True, help="""
        Command to invoke an image viewer program when you are using
        'stream' image handler.  This option is a list of string where
        the first element is the command itself and reminders are the
        options for the command.  Raw image data is given as STDIN to
        the program.
        """
    )

    tempfile_image_handler = List(
        config=True, help="""
        Command to invoke an image viewer program when you are using
        'tempfile' image handler.  This option is a list of string
        where the first element is the command itself and reminders
        are the options for the command.  You can use {file} and
        {format} in the string to represent the location of the
        generated image file and image format.
        """
    )

    callable_image_handler = Any(
        config=True, help="""
        Callable object called via 'callable' image handler with one
        argument, `data`, which is `msg["content"]["data"]` where
        `msg` is the message from iopub channel.  For exmaple, you can
        find base64 encoded PNG data as `data['image/png']`. If your function
        can't handle the data supplied, it should return `False` to indicate
        this.
        """
    )

    mime_preference = List(
        default_value=['image/png', 'image/jpeg', 'image/svg+xml'],
        config=True, help="""
        Preferred object representation MIME type in order.  First
        matched MIME type will be used.
        """
    )

    use_kernel_is_complete = Bool(
        True, config=True, help="""
        Whether to use the kernel's is_complete message
        handling. If False, then the frontend will use its
        own is_complete handler.
        """
    )
    kernel_is_complete_timeout = Float(
        1, config=True, help="""
        Timeout (in seconds) for giving up on a kernel's is_complete
        response.

        If the kernel does not respond at any point within this time,
        the kernel will no longer be asked if code is complete, and the
        console will default to the built-in is_complete test.
        """
    )

    confirm_exit = Bool(
        True, config=True, help="""Set to display confirmation dialog on exit.
        You can always use 'exit' or 'quit', to force a
        direct exit without any confirmation.
        """
    )

    manager = Instance('jupyter_client.KernelManager', allow_none=True)
    client = Instance('jupyter_client.KernelClient', allow_none=True)

    def _client_changed(self, name, old, new):
        self.session_id = new.session.session
    session_id = Unicode()

    def _banner1_default(self):
        return "Vim Jupyter"

    simple_prompt = Bool(
        False, help="""Use simple fallback prompt. Features may be limited."""
    ).tag(config=True)

    def __init__(self, **kwargs):
        # This is where traits with a config_key argument are updated
        # from the values on config.
        super(VimJupyterShell, self).__init__(**kwargs)
        self.configurables = [self]

        self.init_history()
        self.init_io()

        self.init_kernel_info()
        self.execution_count = 1

    def init_history(self):
        """Sets up the command history. """
        self.history_manager = ZMQHistoryManager(client=self.client)
        self.configurables.append(self.history_manager)

    kernel_info = {}

    def init_kernel_info(self):
        """Wait for a kernel to be ready, and store kernel info"""
        timeout = self.kernel_timeout
        tic = time.time()
        self.client.hb_channel.unpause()
        msg_id = self.client.kernel_info()
        while True:
            try:
                reply = self.client.get_shell_msg(timeout=1)
            except Empty:
                if (time.time() - tic) > timeout:
                    raise RuntimeError(
                        "Kernel didn't respond to kernel_info_request")
            else:
                if reply['parent_header'].get('msg_id') == msg_id:
                    self.kernel_info = reply['content']
                    return

    def init_io(self):
        if sys.platform not in {'win32', 'cli'}:
            return

        import colorama
        colorama.init()

    def ask_restart(self):
        self.vim_display_manager.open_window(kind="stdout")
        self.kernel_manager.restart_kernel()
        self.vim_display_manager.handle_stdout("Kernel restart!")
        self.vim_display_manager.finish_stdout()

    def ask_shutdown(self, silent=True):
        if silent is False:
            choice = self.vim_display_manager.handle_confirm(
                "Confirm shutdown kernel? y/n", {'y', 'n'})
            if choice == 1:
                return
        msg_id = self.client.shutdown(restart=False)
        while self.client.is_alive():
            try:
                msg = self.client.shell_channel.get_msg(block=False, timeout=0.05)
                if msg["parent_header"].get("msg_id", None) == msg_id:
                    break
            except Empty:
                pass
            else:
                break
        if silent is False:
            self.vim_display_manager.open_window(kind="stdout")
            self.vim_display_manager.handle_stdout("The kernel has been shut down: "
                                               + msg["header"]["session"])
            self.vim_display_manager.finish_stdout()

    # This is set from payloads in handle_execute_reply
    next_input = None

    def run_cell(self, cell, store_history=True):
        """Run a complete IPython cell.

        Parameters
        ----------
        cell : str
          The code (including IPython code such as %magic functions) to run.
        store_history : bool
          If True, the raw and translated cell will be stored in IPython's
          history. For user code calling back into IPython's machinery, this
          should be set to False.
        """

        self.vim_display_manager.open_window(kind="stdout")
        if (not cell) or cell.isspace():
            # pressing enter flushes any pending display
            self.handle_iopub()
            self.vim_display_manager.finish_stdout()
            return

        if self.client.is_alive() is False:
            self.handle_iopub()
            self.vim_display_manager.handle_stdout("The kernel is not alive")
            self.vim_display_manager.finish_stdout()
            return

        # flush stale replies, which could have been ignored,
        # due to missed heartbeats
        while self.client.shell_channel.msg_ready():
            self.client.shell_channel.get_msg()
        # execute takes 'hidden', which is the inverse of store_hist
        msg_id = self.client.execute(cell, not store_history)

        # first thing is wait for any side effects (output, stdin, etc.)
        self._executing = True
        self._execution_state = "busy"
        while self._execution_state != 'idle' and self.client.is_alive():
            try:
                self.handle_input_request(msg_id, timeout=0.05)
            except Empty:
                # display intermediate print statements, etc.
                self.handle_iopub(msg_id)
            except ZMQError as e:
                # Carry on if polling was interrupted by a signal
                if e.errno != errno.EINTR:
                    raise

        # after all of that is done, wait for the execute reply
        while self.client.is_alive():
            try:
                self.handle_execute_reply(msg_id, timeout=0.05)
            except Empty:
                pass
            else:
                break
        self._executing = False
        self.vim_display_manager.finish_stdout()

    # -----------------
    # message handlers
    # -----------------

    def handle_execute_reply(self, msg_id, timeout=None):
        msg = self.client.shell_channel.get_msg(block=False, timeout=timeout)
        if msg["parent_header"].get("msg_id", None) == msg_id:

            self.handle_iopub(msg_id)

            content = msg["content"]
            status = content['status']
            if status == 'aborted':
                self.write('Aborted\n')
                return
            elif status == 'ok':
                # handle payloads
                for item in content.get("payload", []):
                    source = item['source']
                    if source == 'page':
                        page.page(item['data']['text/plain'])
                    elif source == 'set_next_input':
                        self.next_input = item['text']
                    elif source == 'ask_exit':
                        self.keepkernel = item.get('keepkernel', False)

            elif status == 'error':
                pass

            self.execution_count = int(content["execution_count"] + 1)

    include_other_output = Bool(
        False, config=True,
        help="""Whether to include output from clients
        other than this one sharing the same kernel.

        Outputs are not displayed until enter is pressed.
        """
    )
    other_output_prefix = Unicode(
        "[remote] ", config=True,
        help="""Prefix to add to outputs coming from clients other than this one.

        Only relevant if include_other_output is True.
        """
    )

    def from_here(self, msg):
        """Return whether a message is from this session"""
        return msg['parent_header'].get(
            "session", self.session_id) == self.session_id

    def include_output(self, msg):
        """Return whether we should include a given output message"""
        from_here = self.from_here(msg)
        if msg['msg_type'] == 'execute_input':
            # echo inputs
            return True

        if self.include_other_output:
            return True
        else:
            return from_here

# need to redirect
    def handle_iopub(self, msg_id=''):
        """Process messages on the IOPub channel

           This method consumes and processes messages on the IOPub channel,
           such as stdout, stderr, execute_result and status.

           It only displays output that is caused by this session.
        """

        output_handler = self.vim_display_manager.handle_stdout
        clear_buffer = self.vim_display_manager.clear_stdout_buffer

        while self.client.iopub_channel.msg_ready():
            sub_msg = self.client.iopub_channel.get_msg()

            msg_type = sub_msg['header']['msg_type']
            # parent = sub_msg["parent_header"]

            # Update execution_count in case it changed in another session
            if msg_type == "execute_input":
                self.execution_count = int(
                    sub_msg["content"]["execution_count"]) + 1

            if self.include_output(sub_msg):
                if msg_type == 'status':
                    self._execution_state = sub_msg["content"]["execution_state"]
                elif msg_type == 'stream':
                    output_handler("Out[{}]: ".format(self.execution_count))
                    if sub_msg["content"]["name"] == "stdout":
                        if self._pending_clearoutput:
                            clear_buffer()
                            self._pending_clearoutput = False
                        output_handler(
                            sub_msg["content"]["text"])
                    elif sub_msg["content"]["name"] == "stderr":
                        if self._pending_clearoutput:
                            clear_buffer()
                            self._pending_clearoutput = False
                        output_handler(
                            sub_msg["content"]["text"])

                elif msg_type == 'execute_result':
                    if self._pending_clearoutput:
                        clear_buffer()
                        self._pending_clearoutput = False
                    self.execution_count = int(
                        sub_msg["content"]["execution_count"])
                    output_handler("Out[{}]: ".format(self.execution_count))

                    if not self.from_here(sub_msg):
                        output_handler(
                            self.other_output_prefix)
                    format_dict = sub_msg["content"]["data"]
                    self.handle_rich_data(format_dict)

                    if 'text/plain' not in format_dict:
                        continue

                    # output_handler("Out[{}]: ".format(self.execution_count))
                    text_repr = format_dict['text/plain']
                    if '\n' in text_repr:
                        # For multi-line results, start a new line after prompt
                        output_handler()
                    output_handler(text_repr)


                elif msg_type == 'display_data':
                    data = sub_msg["content"]["data"]
                    handled = self.handle_rich_data(data)
                    if not handled:
                        if not self.from_here(sub_msg):
                            output_handler(
                                self.other_output_prefix)
                        # if it was an image, we handled it by now
                        if 'text/plain' in data:
                            output_handler(
                                data['text/plain'])

                elif msg_type == 'execute_input':
                    content = sub_msg['content']
                    if not self.from_here(sub_msg):
                        output_handler(
                            self.other_output_prefix)
                    output_handler(
                        "In [{0}]: ".format(content['execution_count']) +
                        content['code'] + "\n")

                elif msg_type == 'clear_output':
                    if sub_msg["content"]["wait"]:
                        self._pending_clearoutput = True
                    else:
                        clear_buffer()

                elif msg_type == 'error':
                    for frame in sub_msg["content"]["traceback"]:
                        output_handler(frame)


    _imagemime = {
        'image/png': 'png',
        'image/jpeg': 'jpeg',
        'image/svg+xml': 'svg',
    }

    def handle_rich_data(self, data):
        for mime in self.mime_preference:
            if mime in data and mime in self._imagemime:
                if self.handle_image(data, mime):
                    return True
        return False

    def handle_image(self, data, mime):
        handler = getattr(
            self, 'handle_image_{0}'.format(self.image_handler), None)
        if handler:
            return handler(data, mime)

    def handle_image_PIL(self, data, mime):
        if mime not in ('image/png', 'image/jpeg'):
            return False
        try:
            from PIL import Image, ImageShow
        except ImportError:
            return False
        raw = base64.decodestring(data[mime].encode('ascii'))
        img = Image.open(BytesIO(raw))
        return ImageShow.show(img)

    def handle_image_stream(self, data, mime):
        raw = base64.decodestring(data[mime].encode('ascii'))
        imageformat = self._imagemime[mime]
        fmt = dict(format=imageformat)
        args = [s.format(**fmt) for s in self.stream_image_handler]
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(
                args, stdin=subprocess.PIPE,
                stdout=devnull, stderr=devnull)
            proc.communicate(raw)
        return (proc.returncode == 0)

    def handle_image_tempfile(self, data, mime):
        raw = base64.decodestring(data[mime].encode('ascii'))
        imageformat = self._imagemime[mime]
        filename = 'tmp.{0}'.format(imageformat)
        with NamedFileInTemporaryDirectory(filename) as f, \
                open(os.devnull, 'w') as devnull:
            f.write(raw)
            f.flush()
            fmt = dict(file=f.name, format=imageformat)
            args = [s.format(**fmt) for s in self.tempfile_image_handler]
            rc = subprocess.call(args, stdout=devnull, stderr=devnull)
        return (rc == 0)

    def handle_image_callable(self, data, mime):
        res = self.callable_image_handler(data)
        if res is not False:
            # If handler func returns e.g. None, assume it has handled the data.
            res = True
        return res

    def handle_input_request(self, msg_id, timeout=0.1):
        """ Method to capture raw_input
        """
        req = self.client.stdin_channel.get_msg(timeout=timeout)
        # in case any iopub came while we were waiting:
        self.handle_iopub(msg_id)
        if msg_id == req["parent_header"].get("msg_id"):
            # wrap SIGINT handler
            real_handler = signal.getsignal(signal.SIGINT)

            def double_int(sig, frame):
                # call real handler (forwards sigint to kernel),
                # then raise local interrupt, stopping local raw_input
                real_handler(sig, frame)
                raise KeyboardInterrupt
            signal.signal(signal.SIGINT, double_int)
            content = req['content']
            self.vim_display_manager.open_window(kind="stdin")
            if content.get('password', False):
                read = self.vim_display_manager.handle_password
            else:
                read = self.vim_display_manager.handle_stdin
            try:
                raw_data = read(content["prompt"])
            except EOFError:
                # turn EOFError into EOF character
                raw_data = '\x04'
            except KeyboardInterrupt:
                self.vim_display_manager.handle_input("KeyboradInterrupt!")
                return
            finally:
                # restore SIGINT handler
                self.vim_display_manager.close_stdin_window()
                signal.signal(signal.SIGINT, real_handler)
            # only send stdin reply if there *was not* another request
            # or execution finished while we were reading.
            if not (self.client.stdin_channel.msg_ready()
                    or self.client.shell_channel.msg_ready()):
                self.client.input(raw_data)
