from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import re
import unittest

version = "0.1"

# Verbosity
ERROR = 0
WARNING = 1
INFO = 2

current_verbosity = 0


def lreplace(string, pattern, sub):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^{}'.format(pattern), sub, string)


def log(verbosity, msg):
    if current_verbosity > verbosity:
        global version
        print("FastSwitch {}: {}".format(version, msg))


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
    log(50, "replace_current_directory: orig: \"{}\" replaced: \"{}\"".format(orig, new_orig))
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
    log(50, "replace_index: orig: [{}] replacements: [{}]".format(orig, replacements))

    pattern1 = "(?<=@)-[0-9]+"
    pattern2 = "@-[0-9]+"
    cnt = 0
    while '@' in orig and cnt < 20:
        nb = len(replacements)

        log(50, "replace_index: There is a \"@\" in the original string: [{}]".format(orig))
        m = re.search(pattern1, orig)
        if m:
            log(50, "replace_index: The match: [{}] Found a groups: {}".format(m, m.group(0)))
            idx = int(m.group(0))
            log(50, "replace_index: nb: {}  idx: {}".format(nb, idx))
            if idx > -nb and idx < 0:
                log(INFO, "Replacing the indicator index in [{}] by [{}]".format(orig, replacements[idx]))
                new_str = re.sub(pattern2, replacements[idx], orig, 1)
                log(INFO, "The original string [{}] is now: [{}]".format(orig, new_str))
                orig = new_str
        else:
            log(ERROR, "The index indicator tag \"@\" found in \"{}\" is "
                "not followed by a negative number.".format(orig))
        cnt = cnt + 1
    return orig


def fast_switch(verbose_level, syntax, path, ext_dir):

    global current_verbosity
    current_verbosity = verbose_level

    base, filename = os.path.split(path)
    log(50, "Base: {}, filename: {}".format(base, filename))

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
            cur_ext = cur_ext.strip()
            log(50, "Checking if file \"{}\" has extension \"{}\"".format(filename, cur_ext))
            if not filename.endswith(cur_ext):
                continue

            log(50, "\"{}\" has extension \"{}\"".format(filename, cur_ext))
            name = re.sub(re.escape(cur_ext) + '$', '', filename)

            # Handle None, empty set, empty string...
            # => if it doesn't evaluate to True, replace by empty string
            if not wife_prefixes_to_remove:
                wife_prefixes_to_remove = [""]

            if not wife_prefixes:
                wife_prefixes = [""]

            for wife_prefix_to_remove in wife_prefixes_to_remove:
                log(INFO, "Removing prefix '{}'".format(wife_prefix_to_remove))
                prefix_removed_name = lreplace(name, wife_prefix_to_remove, "")
                log(INFO, "=> Looking for file \"{}\" with one of the following prefixes {!r}, "
                    "one of the following extensions {!r}, "
                    "in one of the sub directory {!r}, from the path \"{}\"".format(
                        prefix_removed_name, wife_prefixes, wife_exts, wife_dirs, base))

                for wife_prefix in wife_prefixes:
                    resolved_name = wife_prefix + prefix_removed_name
                    for wife_dir in wife_dirs:
                        log(50, "Investigating wife directory: \"{}\"".format(wife_dir))

                        # Need to replace the special caracter with the appropriate directory in
                        # the husband's file path
                        if "@" in wife_dir:
                            log(50, "There is a \"@\" in directory \"{}\" need to split "
                                "the path \"{}\" ".format(wife_dir, base))
                            dirs = []
                            head = base
                            cnt = 0
                            tail = ""
                            while head and head != os.path.sep and cnt < 10:
                                log(50, "Head: \"{}\" tail: \"{}\" ".format(head, tail))
                                (head, tail) = os.path.split(head)
                                log(50, "Adding \"{}\" to dirs: \"{}\"".format(tail, dirs))
                                dirs.append(tail)
                                cnt = cnt + 1

                            dirs.reverse()
                            log(50, "The component of the path: {}".format(dirs))
                            log(INFO, "Might need to replace the \"@index\" in \"{}\" "
                                "by one of the following {}".format(wife_dir, dirs))
                            wife_dir = replace_index(wife_dir, dirs)
                            log(50, "The new directory: \"{}\"".format(wife_dir))

                        log(INFO, "The investigation directory with everything "
                            "replaced: \"{}\"".format(wife_dir))
                        for wife_ext in wife_exts:
                            if not wife_ext.startswith("."):
                                wife_ext = "." + wife_ext
                            if resolved_name.endswith("."):
                                resolved_name = resolved_name[:-1]
                            path = os.path.join(base, wife_dir)
                            log(50, "Investigating for file \"{}\" in directory \"{}\" "
                                "with extension \"{}\"".format(resolved_name, path, wife_ext))
                            wife = os.path.join(path, resolved_name + wife_ext)
                            wife = os.path.normpath(wife)
                            log(INFO, "Looking for wife file: {}".format(wife))
                            if not os.path.isfile(wife):
                                log(INFO, "Path does not exists: {}".format(wife))
                                continue
                            return wife
    else:
        if len(ext_dir[i]) == 2:
            log(INFO, "The file [{}] has no extension found in the list {}, "
                "{} for the syntax [{}].".format(filename, ext_dir[0][0], ext_dir[1][0], syntax))
        else:
            log(INFO, "The file [{}] has no extension found in the list {}, "
                "{} for the syntax [{}].".format(filename, ext_dir[0][1], ext_dir[1][1], syntax))


class TestFastSwitch(unittest.TestCase):

    def setUp(self):
        self.test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests_db"))

    def assertPathEqual(self, expected, wife):
        self.assertIsNotNone(wife)
        wife = wife.replace(self.test_db, "TEST_DB")
        self.assertEqual(expected, wife)

    def test1(self):
        # Test 1
        #  "C++": [
        #             [ [".cpp"], ["."] ],
        #             [ ["hpp"],  ["."] ]
        #           ]
        # ls ./foo/src => test1.cpp, test1.hpp
        # ./foo/src/test1.cpp should switch to ./src/test1.hpp
        # ./foo/src/test1.hpp should switch to ./src/test1.cpp
        ext_dir = [
            [[".cpp"], ["."]],
            [["hpp"],  ["."]]
        ]
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.cpp"),
                           ext_dir)
        self.assertPathEqual(os.path.join("TEST_DB", "Test_1", "src", "test1.hpp"), wife)

        wife = fast_switch(100, "C++", os.path.join(self.test_db,
                                                    "Test_1",
                                                    "src",
                                                    "test1.hpp"),
                           ext_dir)
        self.assertPathEqual(os.path.join("TEST_DB", "Test_1", "src", "test1.cpp"), wife)

    @unittest.skip("development ongoing")
    def test2(self):
        # Test 2
        #  "C++": [
        #             [ [".cpp"], ["src"] ],
        #             [ [".h"],   ["include"] ]
        #           ]
        # ls ./foo/src => test2.cpp
        # ls ./foo/include => test2.h
        # ./foo/src/test2.cpp should switch to ./include/test2.hpp
        # ./foo/include/test2.hpp should switch to ./src/test2.cpp
        ext_dir = [
            [[".cpp"], ["src"]],
            [[".h"],   ["include"]]
        ]
        wife = fast_switch(100, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                    "tests_db",
                                                                    "Test_1",
                                                                    "src",
                                                                    "test2.cpp")),
                           ext_dir)
        self.assertPathEqual(os.path.join("TEST_DB", "Test_2", "src", "test2.hpp"), wife)

    @unittest.skip("development ongoing")
    def test3(self):
        # Test 3
        #  "C++": [
        #             [ [".cpp"], ["../src"] ],
        #             [ [".h"],   ["include/@-1"] ]
        #           ]
        # ls ./foo/src => test3.cpp
        # ls ./foo/include/foo => test3.h
        # ./foo/src/test3.cpp should switch to ./foo/include/foo/test3.h
        # ./foo/include/foo/test3.h should switch to ./foo/src/test3.cpp
        ext_dir = [
            [[".cpp"], ["../src"]],
            [[".h"],   ["include/@-1"]]
        ]
        wife = fast_switch(100, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                    "tests_db",
                                                                    "Test_3",
                                                                    "src",
                                                                    "test3.cpp")),
                           ext_dir)
        self.assertPathEqual(os.path.join("TEST_DB", "Test_3", "src", "test3.hpp"), wife)

    @unittest.skip("development ongoing")
    def test4(self):
        # Test 4
        #  "C++": [
        #             [ [".cpp"], ["../../src/."] ],
        #             [ [".h"],   ["../include/@-2/."] ]
        #           ]
        # ls ./foo/src/bar => toto.cpp
        # ls ./foo/include/foo/bar/ => toto.h
        # ./foo/src/bar/toto.cpp should switch to ./foo/include/foo/bar/toto.h
        # ./foo/include/foo/bar/toto.hpp should switch to ./foo/src/bar/toto.cpp
        ext_dir = [
            [[".cpp"], ["../../src/."]],
            [[".h"],   ["../include/@-2/."]]
        ]
        wife = fast_switch(100, "C++", os.path.join(self.test_db,
                                                    "Test_4",
                                                    "src",
                                                    "test4.cpp"),
                           ext_dir)
        self.assertPathEqual(os.path.join("TEST_DB", "Test_4", "src", "test4.hpp"), wife)

    @unittest.skip("development ongoing")
    def test5(self):
        # Test 5
        # "JavaScript": [
        #             [ [".js"], ["public/js"] ],
        #             [ ["Spec.js"], ["../test"] ]
        #           ],
        # ls ./foo/public/js => test5.js
        # ls ./foo/test => test5Spec.js
        # ./foo/public/js/test5.js should switch to ./foo/test/test5Spec.js
        # ./foo/test/test5Spec.js should switch to ./foo/public/js/test5.js
        ext_dir = [
            [[".js"], ["public/js"]],
            [["Spec.js"], ["../test"]]
        ]
        wife = fast_switch(100, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                    "tests_db",
                                                                    "Test_5",
                                                                    "src",
                                                                    "test5.cpp")),
                           ext_dir)
        self.assertPathEqual(os.path.join("TEST_DB", "Test_5", "src", "test5.hpp"), wife)


if __name__ == '__main__':
    unittest.main(verbosity=2)
