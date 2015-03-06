from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os.path

import sublime
import sublime_plugin

from .lib.fastswitch import ERROR
from .lib.fastswitch import INFO
from .lib.fastswitch import WARNING
from .lib.fastswitch import fast_switch, extended_fast_switch
from .lib.fastswitch import log


settings = {}


def assign_settings():
    global settings
    settings = sublime.load_settings('FastSwitch.sublime-settings')


def syntax_name(view):
    log(98, "syntax_name: start")
    syntax = os.path.basename(view.settings().get('syntax'))
    syntax = os.path.splitext(syntax)[0]
    log(98, "syntax_name: %s" % syntax)
    return syntax


class FastSwitchCommand(sublime_plugin.WindowCommand):

    def run(self):
        log(98, "run: Start")
        # Set user options
        assign_settings()

        log(WARNING, "Settings: all: %s" % settings)

        syntax = syntax_name(self.window.active_view())
        log(WARNING, "Syntax: %s" % syntax)

        ext_dir = settings.get(syntax)
        if None == ext_dir:
            log(ERROR, "Setting not found for the syntax %s" % syntax)
            return
        else:
            log(INFO, "Using settings for syntax %s: %s" % (syntax, ext_dir))

        # Get the current active file name and active folder
        path = self.window.active_view().file_name()
        log(WARNING, "Current active file: %s" % path)
        if not path:
            log(ERROR, "Can not switch script, file name can not be retrieved. Is a file currently open and active?")
            return

        wife = fast_switch(settings.get("verbosity", -1), syntax, path, ext_dir)

        if not wife:
            extended_settings = settings.get("extended", {})
            if not extended_settings:
                return
            wife = extended_fast_switch(settings.get("verbosity", -1), syntax, path, extended_settings)
            if not wife:
                return

        if (os.path.abspath(self.window.active_view().file_name()) ==
                os.path.abspath(wife)):
            log(INFO, "Found wife file is myself: %s. Continuing." % wife)
        else:
            log(INFO, "Found a wife file: %s" % wife)
            self.window.open_file(wife)
            return

        self.window.open_file(wife)
