from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os.path

import sublime
import sublime_plugin

from .lib.fastswitch import ERROR
from .lib.fastswitch import INFO
from .lib.fastswitch import WARNING
from .lib.fastswitch import fast_switch
from .lib.fastswitch import log


settings = {}

# Fallback method


def compare_file_names(x, y):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        return x.lower() == y.lower()
    else:
        return x == y

def find_in_current_dir(basename, extensions):
    for ext in extensions:
        new_path = basename + '.' + ext

        if os.path.exists(new_path):
            return new_path

    return None

def find_in_special_dirs(basename, extensions, special_dirs):
    base, filename = os.path.split(basename)

    dirname = True

    while dirname:
        root, dirname = os.path.split(base)

        if dirname in special_dirs:
            index = special_dirs.index(dirname)
            others = special_dirs[index + 1:] + special_dirs[:index]

            for d in others:
                for wroot, dirs, files in os.walk(os.path.join(root, d), topdown=False):
                    for ext in extensions:
                        found = [x for x in files if compare_file_names(x, filename + '.' + ext)]
                        if found:
                            return os.path.join(wroot, found[0])

    return None

def prepare_for_find_in_special_dir(syntax, path, ext_dir):
    log(DEBUG, "Syntax: %s  Path: %s  Ext_dir" % (syntax, path, ext_dir))

    base, filename = os.path.split(basename)
    log(50, "Base: {}, filename: {}".format(base, filename))

    nb_transition = len(settings)
    # Start working on finding the wife of the current file
    # - No work is done in advance everything is done when needed
    # Find in which of the two list the current extension belongs

    special_dirs = []
    for i in range(nb_transition):
        husband_idx, husband_ext, husband_prefix = find_index(filename, settings, i)

        log(98, "Index: \"%d\" Husband: \"%s\" has prefix \"%s\", and extension \"%s\"" %
            (husband_idx, filename, husband_prefix, husband_ext))

        if husband_idx != -1:
            husband_basename = filename[:-len(husband_ext)]
            # log(50, "Index: \"%d\" Husband: \"%s\" without extension \"%s\", basename \"%s\""
            #    % (husband_idx, filename, husband_ext, husband_basename))
            husband_basename = husband_basename[len(husband_prefix):]
            # log(50, "Index: \"%d\" Husband: \"%s\" without prefix \"%s\", basename \"%s\"" %
            # (husband_idx, filename, husband_prefix, husband_basename))

            log(50, "Index: \"%d\" Husband: \"%s\" has prefix \"%s\", basename: \"%s\" and extension \"%s\"" %
                (husband_idx, filename, husband_prefix, husband_basename, husband_ext))

            for wife_idx in range(husband_idx + 1, nb_transition + husband_idx):
                wife_idx = (wife_idx) % nb_transition
                log(100, "husband_idx: %d   nb_transition: %d  wife_idx: (husband_idx+1) mod nb_transition = %d" %
                    (husband_idx, nb_transition, wife_idx))
                wife_extensions = settings[wife_idx][0]
                wife_directories = settings[wife_idx][1]
                wife_prefixes = get_prefixes(wife_idx, settings)

                log(50, "Index: \"%d\" Wife: extensions: {%s} directories: {%s}  prefixes: {%s}" % (
                    wife_idx, wife_extensions, wife_directories, wife_prefixes))




# First method used by FastSwich


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
                wife = prepare_for_find_in_special_dirs(syntax, path, ext_dir)

        if (os.path.abspath(self.window.active_view().file_name()) ==
                os.path.abspath(wife)):
            log(INFO, "Found wife file is myself: %s. Continuing." % wife)
        else:
            log(INFO, "Found a wife file: %s" % wife)
            self.window.open_file(wife)
            return

        self.window.open_file(wife)
