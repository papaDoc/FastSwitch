from __future__ import print_function
import sublime
import sublime_plugin
import os.path
import re

version = "0.1"
settings = {}

# Verbosity
ERROR = 0
WARNING = 1
INFO = 2


def lreplace(string, pattern, sub):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)


def assign_settings():
    global settings
    settings = sublime.load_settings('FastSwitch.sublime-settings')


def syntax_name(view):
    log(98, "syntax_name: start")
    syntax = os.path.basename(view.settings().get('syntax'))
    syntax = os.path.splitext(syntax)[0]
    log(98, "syntax_name: %s" % syntax)
    return syntax


def log(verbosity, msg):
    if settings.get("verbosity", -1) > verbosity:
        global version
        print("FastSwitch %s: %s" % (version, msg))


def with_index(seq):
    for i in range(len(seq)):
        yield i, seq[i]


def replace_current_directory(orig, replacement):
    '''
      Replace single dot by replacement
      Ex: "."       => "src"
          "@-1/."   => "@-1/src"
          "../tata" => "../tata"

      @param orig        The original string which might need replacement
      @param replacement If the indicator for the current directory is found in orig it will be replaced
                         by this value

      @return The "orig" string with single dot replaced by "replacement"
    '''

    pattern = "(?<!\.)(\.)(?!\.)"
    new_orig = re.sub(pattern, replacement, orig)
    log(50, "replace_current_directory: orig: \"%s\" replaced: \"%s\"" % (orig, new_orig))
    return new_orig


def replace_index(orig, replacements):
    '''
      Replacement a index indicator by the correcponding value in the replacement list
      Ex: orig= "@-1", replacements = ["aa", "bb", "cc"] => "cc"
          orig="@-2/include", replacements = ["aa", "bb", "cc"] => "bb/include"

      @param orig         The original string that which might containe an index indicator.
                          An index indicator the the symbol "@" followed by a negative number
      @param replacements A list of string used for the replacement

      @return The "orig" string with, if needed the index indicator replaced
    '''
    log(50, "replace_index: orig: [%s] replacements: [%s]" % (orig, replacements))

    pattern1 = "(?<=@)-[0-9]+"
    pattern2 = "@-[0-9]+"
    cnt = 0
    while '@' in orig and cnt < 20:
        nb = len(replacements)

        log(50, "replace_index: There is a \"@\" in the original string: [%s]" % orig)
        m = re.search(pattern1, orig)
        if m:
            log(50, "replace_index: The match: [%s] Found a groups: %s" % (m, m.group(0)))
            idx = int(m.group(0))
            log(50, "replace_index: nb: %d  idx: %d" % (nb, idx))
            if idx > -nb and idx < 0:
                log(INFO, "Replacing the indicator index in [%s] by [%s]" % (orig, replacements[idx]))
                new_str = re.sub(pattern2, replacements[idx], orig, 1)
                log(INFO, "The original string [%s] is now: [%s]" % (orig, new_str))
                orig = new_str
        else:
            log(ERROR, "The index indicator tag \"@\" found in \"%s\" is not followed by a negative number." % orig)
        cnt = cnt + 1
    return orig


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

        base, filename = os.path.split(path)
        log(50, "Base: %s, filename: %s" % (base, filename))

        # Start working on finding the wife of the current file
        # - No work is done in advance everything is done when needed

        # Find in which of the two list the current extension belongs
        for i in (0, 1):
            for j, e in with_index(ext_dir[i][1]):  # Index 0 for the extension
                if len(ext_dir[i]) == 2:
                    cur_ext = ext_dir[i][0][j]
                    wife_idx = (i + 1) % 2
                    wife_prefixes_to_remove = []
                    wife_exts = ext_dir[wife_idx][0]
                    wife_dirs = ext_dir[wife_idx][1]
                    wife_prefixes = []
                else:
                    # Extended syntax
                    cur_ext = ext_dir[i][1][j]
                    wife_idx = (i + 1) % 2
                    wife_prefixes_to_remove = ext_dir[wife_idx][0]
                    wife_exts = ext_dir[wife_idx][1]
                    wife_dirs = ext_dir[wife_idx][2]
                    wife_prefixes = ext_dir[wife_idx][3]
                log(50, "Checking if file \"%s\" has extension \"%s\" " % (filename, cur_ext))
                if not filename.endswith(cur_ext):
                    continue

                log(50, "\"%s\" has extension \"%s\" " % (filename, cur_ext))
                name = re.sub(re.escape(cur_ext) + '$', '', filename)

                # Handle None, empty set, empty string...
                # => if it doesn't evaluate to True, replace by empty string
                if not wife_prefixes_to_remove:
                    wife_prefixes_to_remove = [""]

                if not wife_prefixes:
                    wife_prefixes = [""]

                extended_wife_exts = []
                for e in wife_exts:
                    if e[0] == '.':
                        extended_wife_exts.append(e[1:])
                    else:
                        extended_wife_exts.append(e)
                wife_exts = extended_wife_exts

                for wife_prefix_to_remove in wife_prefixes_to_remove:
                    log(INFO, "Removing prefix '{}'".format(wife_prefix_to_remove))
                    prefix_removed_name = lreplace(name, wife_prefix_to_remove, "")
                    log(INFO, "=> Looking for file \"%s\" with one of the following prefixes %r, "
                        "one of the following extensions %r, "
                        "in one of the sub directory %r, from the path \"%s\"" % (
                            prefix_removed_name, wife_prefixes, wife_exts, wife_dirs, base))

                    for wife_prefix in wife_prefixes:
                        resolved_name = wife_prefix + prefix_removed_name
                        for wife_dir in wife_dirs:
                            log(50, "Investigating wife directory: \"%s\"" % wife_dir)

                            # Need to replace the special caracter with the appropriate directory in
                            # the husband's file path
                            if "@" in wife_dir:
                                log(50, "There is a \"@\" in directory \"%s\" need to split the path \"%s\" " %
                                    (wife_dir, base))
                                dirs = []
                                head = base
                                cnt = 0
                                tail = ""
                                while head and head != os.path.sep and cnt < 10:
                                    log(50, "Head: \"%s\" tail: \"%s\" " % (head, tail))
                                    (head, tail) = os.path.split(head)
                                    log(50, "Adding \"%s\" to dirs: \"%s\"" % (tail, dirs))
                                    dirs.append(tail)
                                    cnt = cnt + 1

                                dirs.reverse()
                                log(50, "The component of the path: %s" % dirs)
                                log(INFO, "Might need to replace the \"@index\" in \"%s\" by one of the following %s" %
                                    (wife_dir, dirs))
                                wife_dir = replace_index(wife_dir, dirs)
                                log(50, "The new directory: \"%s\"" % wife_dir)

                            log(INFO, "The investigation directory with everything replaced: \"%s\"" % wife_dir)
                            for wife_ext in wife_exts:
                                print("wife_ext", wife_ext)
                                path = os.path.join(base, wife_dir)
                                log(50, "Investigating for file \"%s\" in directory \"%s\" with extension \"%s\"" %
                                    (resolved_name, path, wife_ext))
                                wife = os.path.join(path, resolved_name + wife_ext)
                                log(INFO, "Looking for wife file: %s" % wife)
                                if not os.path.isfile(wife):
                                    continue
                                if (os.path.abspath(self.window.active_view().file_name()) ==
                                        os.path.abspath(wife)):
                                    log(INFO, "Found wife file is myself: %s. Continuing." % wife)
                                else:
                                    log(INFO, "Found a wife file: %s" % wife)
                                    self.window.open_file(wife)
                                    return
        else:
            log(INFO, "The file [%s] has no extension found in the list %s, %s for the syntax [%s]." %
                (filename, ext_dir[0][0], ext_dir[1][0], syntax))


# Test 1
#  "C++": [
#             [ [".cpp"], ["src"] ],
#             [ ["hpp"],  ["."] ]
#           ]
# or
#  "C++": [
#             [ [".cpp"], ["."] ],
#             [ ["hpp"],  ["."] ]
#           ]
# ls ./foo/src => test1.cpp, test1.hpp
# ./foo/src/test1.cpp should switch to ./src/test1.hpp
# ./foo/src/test1.hpp should switch to ./src/test1.cpp

# Test 2
#  "C++": [
#             [ [".cpp"], ["src"] ],
#             [ [".h"],   ["include"] ]
#           ]
# ls ./foo/src => test2.cpp
# ls ./foo/include => test2.h
# ./foo/src/test2.cpp should switch to ./include/test2.hpp
# ./foo/include/test2.hpp should switch to ./src/test2.cpp

# Test 3
#  "C++": [
#             [ [".cpp"], ["../src"] ],
#             [ [".h"],   ["include/@-1"] ]
#           ]
# ls ./foo/src => test3.cpp
# ls ./foo/include/foo => test3.h
# ./foo/src/test3.cpp should switch to ./foo/include/foo/test3.h
# ./foo/include/foo/test3.h should switch to ./foo/src/test3.cpp

# Test 4
#  "C++": [
#             [ [".cpp"], ["../../src/."] ],
#             [ [".h"],   ["../include/@-2/."] ]
#           ]
# ls ./foo/src/bar => toto.cpp
# ls ./foo/include/foo/bar/ => toto.h
# ./foo/src/bar/toto.cpp should switch to ./foo/include/foo/bar/toto.h
# ./foo/include/foo/bar/toto.hpp should switch to ./foo/src/bar/toto.cpp

# Test 5
# "JavaScript": [
#             [ [".js"], ["public/js"] ],
#             [ ["Spec.js"], ["../test"] ]
#           ],
# ls ./foo/public/js => test5.js
# ls ./foo/test => test5Spec.js
# ./foo/public/js/test5.js should switch to ./foo/test/test5Spec.js
# ./foo/test/test5Spec.js should switch to ./foo/public/js/test5.js
