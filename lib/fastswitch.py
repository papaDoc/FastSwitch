from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import re
import unittest
import itertools

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


def log(verbosity, msg, *args):
    if current_verbosity >= verbosity:
        global version
        print("FastSwitch {}: {}".format(version, msg), *args)


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
            cur_ext = ext_dir[i][0][j]
            wife_idx = (i + 1) % 2
            wife_prefixes_to_remove = []
            wife_exts = ext_dir[wife_idx][0]
            wife_dirs = ext_dir[wife_idx][1]
            wife_prefixes = []
            cur_ext = cur_ext.strip()
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
                            path = os.path.join(base, wife_dir)
                            log(50, "Investigating for file \"{}\" in directory \"{}\" "
                                "with extension \"{}\"".format(resolved_name, path, wife_ext))
                            wife = os.path.join(path, resolved_name + wife_ext)
                            wife = os.path.normpath(wife)
                            if not os.path.isfile(wife):
                                log(INFO, "Path does not exists: {}".format(wife))
                                continue
                            return wife
    else:
        log(INFO, "Cannot find wife file for {}, using the syntax '{}'.".format(filename, syntax))


def extended_fast_switch(verbose_level, syntax, path, extended_settings):
    global current_verbosity
    current_verbosity = verbose_level

    log(50, "")
    log(50, "====")
    log(1, "Analysing: {!r}, syntax: {!r}".format(path, syntax))
    for extended_setting in extended_settings:
        if syntax not in extended_setting['syntaxes']:
            continue
        log(50, "Selecting configuration for syntax {}: {!r}".format(syntax, extended_setting))
        for way in ["first_way", "second_way"]:
            log(100, "Way: {!r}".format(way))
            my_extensions = extended_setting[way]['my_extensions']
            my_prefixes = extended_setting[way]['my_prefixes']
            wife_directories = extended_setting[way]['wife_directories']
            wife_prefixes = extended_setting[way]['wife_prefixes']
            wife_extensions = extended_setting[way]['wife_extensions']

            log(100, "Extension matching: {!r}".format(my_extensions))

            my_basename = os.path.basename(path)

            found_ext = None
            for ext in my_extensions:
                ext = ext.strip()
                if my_basename.endswith(ext):
                    found_ext = ext
                    break

            if found_ext is None:
                continue

            log(100, "Prefix matching: {!r}".format(my_prefixes))

            found_prefix = None
            if my_prefixes:
                for prefix in my_prefixes:
                    prefix = prefix.strip()
                    if my_basename.startswith(prefix):
                        found_prefix = prefix
                        break

                if found_prefix is None:
                    continue
            else:
                found_prefix = ""

            log(10, "Selecting way '{}' for file '{}'".format(way, path))
            log(50, "  my extension:", found_ext)
            if found_prefix:
                log(50, "  my prefix:", found_prefix)
            log(50, "  wife directories:", wife_directories)
            log(50, "  wife prefixes:", wife_prefixes)
            log(50, "  wife extensions:", wife_extensions)

            if not wife_prefixes:
                # if not set, search with empty prefix (so only remove my prefix)
                wife_prefixes = [""]

            if not wife_directories:
                # if not directory set, search in same directory
                wife_directories = ["."]

            if not wife_extensions:
                # if no extension is specified, search the same extension
                wife_extensions = [os.path.splitext(path)[1]]

            for (wife_prefix,
                 wife_relative_dir,
                 wife_extension) in list(itertools.product(*[wife_prefixes,
                                                             wife_directories,
                                                             wife_extensions])):
                log(60, "Searching wife of {!r} with prefix {!r} in directory {!r}"
                    .format(path, wife_prefix, wife_relative_dir))
                if wife_relative_dir == ".":
                    wife_relative_dir = ""
                if not wife_relative_dir and not wife_prefix and not wife_extension:
                    # will find myself!
                    continue
                wife_dir = os.path.dirname(path)
                if wife_relative_dir:
                    wife_dir = os.path.join(wife_dir, wife_relative_dir)
                wife_basename = my_basename
                # Removing my prefix
                if found_prefix:
                    wife_basename = wife_basename[len(found_prefix):]
                wife_basename = wife_basename[:-len(wife_extension)] + wife_extension
                # Adding wife prefix
                wife_basename = wife_prefix + wife_basename
                wife_path = os.path.join(wife_dir, wife_basename)
                wife_path = os.path.abspath(wife_path)
                log(100, "File exists {!r}? {!r}".format(wife_path, os.path.exists(wife_path)))
                if os.path.exists(wife_path):
                    log(100, "Found wife: {!r}".format(wife_path))
                    return wife_path

    log(50, "====")


class TestFastSwitch(unittest.TestCase):

    def setUp(self):
        self.test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests_db"))

    def assertPathEqual(self, expected, wife):
        self.assertIsNotNone(wife)
        wife = wife.replace(self.test_db, "test_db")
        self.assertEqual(expected, wife)

    # Test 1
    #  "C++": [
    #             [ [".cpp"], ["."] ],
    #             [ ["hpp"],  ["."] ]
    #           ]
    # ls ./foo/src => test1.cpp, test1.hpp
    # ./foo/src/test1.cpp should switch to ./src/test1.hpp
    # ./foo/src/test1.hpp should switch to ./src/test1.cpp
    specTest1 = [
        [[".cpp"], ["."]],
        [[".hpp"],  ["."]]
    ]

    # @unittest.skip("development ongoing")
    def test1_SrcHdrInSameDir1(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.cpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("test_db", "Test_1", "src", "test1.hpp"), wife)

    # @unittest.skip("development ongoing")
    def test1_SrcHdrInSameDir2(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.hpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("test_db", "Test_1", "src", "test1.cpp"), wife)

    # Test 2
    #  "C++": [
    #             [ [".cpp"], ["src"] ],
    #             [ [".h"],   ["include"] ]
    #           ]
    # ls ./foo/src => test2.cpp
    # ls ./foo/include => test2.h
    # ./foo/src/test2.cpp should switch to ./include/test2.hpp
    # ./foo/include/test2.hpp should switch to ./src/test2.cpp
    specTest2 = [
        [[".cpp"], ["../src"]],
        [[".h"],   ["../include"]]
    ]

    # @unittest.skip("development ongoing")
    def test2_SrcHdrInTwoSibblingDirs1(self):
        wife = fast_switch(0, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                  "tests_db",
                                                                  "Test_2",
                                                                  "src",
                                                                  "test2.cpp")),
                           self.specTest2)
        self.assertPathEqual(os.path.join("test_db", "Test_2", "include", "test2.h"), wife)

    # @unittest.skip("development ongoing")
    def test2_SrcHdrInTwoSibblingDirs2(self):
        wife = fast_switch(0, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                  "tests_db",
                                                                  "Test_2",
                                                                  "include",
                                                                  "test2.h")),
                           self.specTest2)
        self.assertPathEqual(os.path.join("test_db", "Test_2", "src", "test2.cpp"), wife)

    # Test 3
    #  "C++": [
    #             [ [".cpp"], ["../src"] ],
    #             [ [".h"],   ["include/@-1"] ]
    #           ]
    # ls ./foo/src => test3.cpp
    # ls ./foo/include/foo => test3.h
    # ./foo/src/test3.cpp should switch to ./foo/include/foo/test3.h
    # ./foo/include/foo/test3.h should switch to ./foo/src/test3.cpp
    specTest3 = [
        [[".cpp"], ["../src"]],
        [[".h"],   ["../include/@-1"]]
    ]

    # @unittest.skip("development ongoing")
    def test3_HdrInPackageDir1(self):
        wife = fast_switch(100, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_3",
                                                        "foo",
                                                        "src",
                                                        "test3.cpp")),
                           self.specTest3)
        self.assertPathEqual(os.path.join("test_db", "Test_3", "foo", "include", "foo", "test3.h"),
                             wife)

    @unittest.skip("development ongoing")
    def test3_HdrInPackageDir2(self):
        wife = fast_switch(100, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_3",
                                                        "include",
                                                        "foo",
                                                        "test3.h")),
                           self.specTest3)
        self.assertPathEqual(os.path.join("test_db", "Test_3", "foo", "src", "test3.cpp"), wife)

    # Test 4
    #  "C++": [
    #             [ [".cpp"], ["../../src/."] ],
    #             [ [".h"],   ["../include/@-2/."] ]
    #           ]
    # ls ./foo/src/bar => toto.cpp
    # ls ./foo/include/foo/bar/ => toto.h
    # ./foo/src/bar/toto.cpp should switch to ./foo/include/foo/bar/toto.h
    # ./foo/include/foo/bar/toto.hpp should switch to ./foo/src/bar/toto.cpp
    specTest4 = [
        [[".cpp"], ["../../src/."]],
        [[".h"],   ["../include/@-2/."]]
    ]

    @unittest.skip("development ongoing")
    def test4_SrcHdrInComplexPackageDir(self):
        wife = fast_switch(100, "C++",
                           os.path.join(self.test_db,
                                        "Test_4",
                                        "src",
                                        "test4.cpp"),
                           self.specTest4)
        self.assertPathEqual(os.path.join("test_db", "Test_4", "src", "test4.hpp"), wife)

    # Test 5
    # "javascript": [
    #             [ [".js"], ["../public/js"] ],
    #             [ ["Spec.js"], ["../test"] ]
    #           ],
    # ls ./foo/public/js => test5.js
    # ls ./foo/test => test5Spec.js
    # ./foo/public/js/test5.js should switch to ./foo/test/test5Spec.js
    # ./foo/test/test5Spec.js should switch to ./foo/public/js/test5.js
    specTest5 = [
        [[".js"], ["../public/js"]],
        [["Spec.js"], ["../../test"]]
    ]

    @unittest.skip("development ongoing")
    def test5_HdrInPublicJs1(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_5",
                                                        "foo",
                                                        "public",
                                                        "js",
                                                        "test5.js")),
                           self.specTest5)
        self.assertPathEqual(os.path.join("test_db", "Test_5", "foo", "test", "test5Spec.js"),
                             wife)

    @unittest.skip("development ongoing")
    def test5_HdrInPublicJs2(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_5",
                                                        "foo",
                                                        "test",
                                                        "test5Spec.js"
                                                        )),
                           self.specTest5)
        self.assertPathEqual(os.path.join("test_db", "Test_5", "foo", "public", "js", "test5.js"),
                             wife)

    # Test 6
    # "javascript": [
    #    [["test_", "test"],["cpp"],[".", ".."],[]],
    #    [[],["cpp"],[".", "test", "tests"],["test_", "test"]]
    #  ],
    # ls ./test => test_file.h
    # ls ./ => file.cpp
    # ./foo/test/test_file.cpp should switch to ./foo/file.cpp
    # ./foo/file.cpp should switch to ./foo/test/test_file.cpp
    specTest6 = {
        'extended': [
            {
                'syntaxes': ["C++"],
                'first_way':{
                    'my_prefixes': ["test_", "test"],
                    'my_extensions': ["cpp"],
                    'wife_directories': [".", ".."],
                    'wife_prefixes': [],
                    'wife_extensions': ['.cpp'],
                },
                'second_way':{
                    'my_prefixes': [],
                    'my_extensions': ["cpp"],
                    'wife_directories': [".", "test", "tests"],
                    'wife_prefixes': ["test_", "test"],
                    'wife_extensions': ['.cpp'],
                }
            }
        ]
    }

    # @unittest.skip("development ongoing")
    def test6_ExtendedSyntaxWithPrefixForTest1(self):
        wife = extended_fast_switch(0, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_6",
                                                                 "file.cpp")),
                                    self.specTest6['extended'])
        self.assertPathEqual(os.path.join("test_db", "Test_6",  "test", "test_file.cpp"),
                             wife)

    # @unittest.skip("development ongoing")
    def test6_ExtendedSyntaxWithPrefixForTest2(self):
        wife = extended_fast_switch(0, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_6",
                                                                 "test",
                                                                 "test_file.cpp"
                                                                 )),
                                    self.specTest6['extended'])
        self.assertPathEqual(os.path.join("test_db", "Test_6", "file.cpp"),
                             wife)

    # Test 7
    # ls ./ => main.template.html, main.controller.js
    # ./main.template.html => ./main.controller.js
    # ./main.controller.js => ./main.template.html
    specTest7 = {
        'extended': [
            {
                'syntaxes': ["js", "html"],
                'first_way':{
                    'my_prefixes': [],
                    'my_extensions': [".controller.js"],
                    'wife_directories': ["."],
                    'wife_prefixes': [],
                    'wife_extensions': ['.template.html'],
                },
                'second_way':{
                    'my_prefixes': [],
                    'my_extensions': [".template.html"],
                    'wife_directories': [],
                    'wife_prefixes': [],
                    'wife_extensions': ['.controller.js'],
                }
            }
        ]
    }

    # @unittest.skip("development ongoing")
    def test7_ExtendedSyntaxWithPrefixForTest1(self):
        wife = extended_fast_switch(0, "js",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_7",
                                                                 "main.controller.js")),
                                    self.specTest7['extended'])
        self.assertPathEqual(os.path.join("test_db", "Test_7",  "main.template.html"),
                             wife)

    # @unittest.skip("development ongoing")
    def test7_ExtendedSyntaxWithPrefixForTest2(self):
        wife = extended_fast_switch(0, "html",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_7",
                                                                 "main.template.html"
                                                                 )),
                                    self.specTest7['extended'])
        self.assertPathEqual(os.path.join("test_db", "Test_7", "main.controller.js"),
                             wife)

if __name__ == '__main__':
    unittest.main(verbosity=2)
