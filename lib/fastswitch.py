from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools
import os.path
import re
import sys
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


def log(verbosity, msg, *args):
    if current_verbosity >= verbosity:
        global version
        print("FastSwitch[{}]: {}".format(verbosity, msg), *args)


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

def get_prefixes(idx, settings):
    prefixes = [""]
    if len(settings[idx]) > 2 :
        if type(settings[idx][2]) == type(dict()):
            prefixes = settings[idx][2]['prefixes']
        else:
            prefixes = settings[idx][2]
    log(50, "get_prefixes: Returning the prefixes: \"%s\" at index: \"%d\" in settings: \"%s\"" % (prefixes, idx, settings))
    return prefixes


def has_prefix(filename, prefixes):
    log(50, "has_prefix: start: filename: \"%s\" prefixes: \"%s\"" % (filename, prefixes))
    if prefixes:
        #log(50, "has_prefix: Ici 0")
        for prefix in prefixes:
            #log(50, "has_prefix: Ici 0")
            prefix = prefix.strip()
            #log(50, "has_prefix: Ici 1")
            if filename.startswith(prefix):
                log(100, "has_prefix: Using {!r} for my_prefix".format(prefix))
                return prefix
        return None
    return ""

def has_extension(filename, extensions):
    """
    Return the extension of the filename if it is one of the extensions or None
    """
    log(50, "has_extension: start: filename: {%s}  extensions: {%s}" % (filename, extensions))
    if extensions:
        for ext in extensions:
            ext = ext.strip()
            if filename.endswith(ext):
                return ext
    return None


def find_index(filename, settings, start_idx=0):
    """
    Find the index of the setting to which the filename belongs
    Find the first settings iteration for which a prefix and an extension matches
    return a tuple [idx, ext, prefix] the index is -1 if not found
    """
    nb_transition = len(settings)
    for i in range(start_idx, nb_transition):
        log(98, "find_index: i: %d" % (i))
        extensions = settings[i][0]
        ext = has_extension(filename, extensions)
        if ext is not None:
            prefixes = get_prefixes(i, settings)
            if len(settings[i]) > 2 :
                if type(settings[i][2]) == type(dict()):
                    prefixes = settings[i][2]['prefixes']
                else:
                    prefixes = settings[i][2]
            prefix = has_prefix(filename, prefixes)
            if prefix is not None:
                log(50, "find_index: The filename \"%s\" has the prefix: \"%s\" and extension: \"%s\" corresponding to index \"%s\" of settings: \"%s\"" % (filename, prefix, ext, i, settings))
                return [i, ext, prefix]
    log(50,"find_index: The filename  \"%s\" does not correspond to any of the settings: \"%s\"" % (filename, settings))
    return [-1, None, None]



def filter_directory(wife_dir, path):
    log(98, "filter_directory: start: wife_dir \"%s\"  path: \"%s\"" % (wife_dir, path))
    # RR do we really need this ????? path = os.path.dirname(path)

    # special handling for windows path => replace "/" (from conf) by \\
    if sys.platform == "win32":
        wife_dir = wife_dir.replace("/", os.path.sep)
    else:
        wife_dir = wife_dir.replace("\\", os.path.sep)

    log(100, "Magic filter for wife {!r}, from path {!r}".format(wife_dir, path))
    parts = path.split(os.path.sep)
    parts.reverse()

    exploded_wife_path = wife_dir.split(os.path.sep)
    log(100, "  exploded_wife_path", exploded_wife_path)
    pattern = re.compile(r"@(-[0-9]+|0)")
    reconstructed_wife = []
    for d in exploded_wife_path:
        log(100, "filter_directory: converting directory \"{!r}\"".format(d) )
        m = pattern.match(d)
        if d == ".":
            idx = 0
            log(100, "{!r} matches {}, which is {!r}".format(d, idx, parts[idx]))
            reconstructed_wife.append(parts[idx])
        elif m:
            idx = -(int(m.group(1)))
            tat = parts[idx]
            log(100, "{!r} matches with {!r}".format(d, parts[idx]))
            reconstructed_wife.append(parts[idx])
        else:
            reconstructed_wife.append(d)
    # cannot use os.path.join since it will not handle the first element "" correctly
    # ("/a/b" is splitted into ["", "a", "b"])
    reconstructed_wife = os.path.sep.join(reconstructed_wife)
    log(100, "Ici 3: reconstructed_wife: %s" % reconstructed_wife)
    return reconstructed_wife



def fast_switch(verbose_level, syntax, path, settings):
    global current_verbosity
    current_verbosity = verbose_level

    log(98, "Syntax: {}, path: {}, settings: {!r}".format(syntax, path, settings))

    base, filename = os.path.split(path)
    log(50, "Base: {}, filename: {}".format(base, filename))

    nb_transition = len(settings)
    # Start working on finding the wife of the current file
    # - No work is done in advance everything is done when needed
    # Find in which of the two list the current extension belongs

    for i in range(nb_transition):
        husband_idx, husband_ext, husband_prefix = find_index(filename, settings, i)
        log(98, "Index: \"%d\" Husband: \"%s\" has prefix \"%s\", and extension \"%s\"" % (husband_idx, filename, husband_prefix, husband_ext))

        if husband_idx != -1:
            husband_basename = filename[:-len(husband_ext)]
            #log(50, "Index: \"%d\" Husband: \"%s\" without extension \"%s\", basename \"%s\"" % (husband_idx, filename, husband_ext, husband_basename))
            husband_basename = husband_basename[len(husband_prefix):]
            #log(50, "Index: \"%d\" Husband: \"%s\" without prefix \"%s\", basename \"%s\"" % (husband_idx, filename, husband_prefix, husband_basename))

            log(50, "Index: \"%d\" Husband: \"%s\" has prefix \"%s\", basename: \"%s\" and extension \"%s\"" % (husband_idx, filename, husband_prefix, husband_basename, husband_ext))

            for wife_idx in range(husband_idx+1, nb_transition+husband_idx):
                wife_idx = (wife_idx) % nb_transition
                log(100,"husband_idx: %d   nb_transition: %d  wife_idx: (husband_idx+1) mod nb_transition = %d" % (husband_idx, nb_transition, wife_idx))
                wife_extensions = settings[wife_idx][0]
                wife_directories = settings[wife_idx][1]
                wife_prefixes = get_prefixes(wife_idx, settings)

                log(50, "Index: \"%d\" Wife: extensions: {%s} directories: {%s}  prefixes: {%s}" % (wife_idx, wife_extensions, wife_directories, wife_prefixes))


                # Split the base since the current directory might be needed
                # and because every is with respect to the base - last_dir
                splitted_base, last_dir = os.path.split(base)
                log(50, "Splitted base: %s   last dir: %s" % (splitted_base, last_dir))

                log(INFO, "Looking for file \"%s\" with one of the following extensions %s in one "
                          "of the sub directories %s with one of the prefixes %s in the path \"%s\"" % (
                          husband_basename, wife_extensions, wife_directories, wife_prefixes, splitted_base))
                for wife_dir in wife_directories:
                    wife_dir = filter_directory(wife_dir, base)
                    path = os.path.join(splitted_base, wife_dir)
                    log(50, "The investigation of wife directory with everything replaced: \"%s\"" % path)
                    for wife_ext in wife_extensions:
                        if wife_ext[0] != '.':
                            wife_extensions.append('.' + wife_ext)
                        #wife_ext = ('.' + wife_ext if wife_ext[0] != '.' else wife_ext)
                        for wife_prefix in wife_prefixes:
                            log(50, "Investigating for file \"%s\" in directory \"%s\" with extension \"%s\" and prefix \"%s\"" %
                                    (husband_basename, path, wife_ext, wife_prefix))
                            wife = os.path.join(path, wife_prefix + husband_basename + wife_ext)
                            wife = os.path.abspath(wife)
                            log(50, "Absolute path: wife: \"%s\"" % (wife) )
                            log(INFO, "Looking for wife file: %s" % wife)
                            if os.path.isfile(wife):
                                log(INFO, "Found a wife file: %s" % wife)
                                return wife
                            log(INFO, "The wife file: %s was not found" % wife)

        log(INFO, "The file [%s] has no extension found in the list %s, %s for the syntax [%s]." %
                 (filename, settings[0][0], settings[1][0], syntax))


class TestFastSwitch(unittest.TestCase):

    def setUp(self):
        self.test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "tests_db"))

    def assertPathEqual(self, expected, wife):
        self.assertIsNotNone(wife)
        wife = wife.replace(self.test_db, "TESTS_DB")
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
        [[".hpp"], ["."]]
    ]

    #@unittest.skip("development ongoing")
    def test1_SrcHdrInSameDir1(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.cpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.hpp"), wife)

    #@unittest.skip("development ongoing")
    def test1_SrcHdrInSameDir2(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.hpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.cpp"), wife)



    # Test 1 husband_extended
    #  "C++": [
    #             [ [".cpp"], ["."] [""]],
    #             [ ["hpp"],  ["."] ]
    #           ]
    # ls ./foo/src => test1.cpp, test1.hpp
    # ./foo/src/test1.cpp should switch to ./src/test1.hpp
    # ./foo/src/test1.hpp should switch to ./src/test1.cpp
    specTest1 = [
        [[".cpp"], ["."], [""]],
        [[".hpp"], ["."]]
    ]

    #@unittest.skip("development ongoing")
    def test1_husband_extended_1(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.cpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.hpp"), wife)

    @unittest.skip("development ongoing")
    def test1_husband_extended_2(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.hpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.cpp"), wife)


    # Test 1 husband_extended_dict
    #  "C++": [
    #             [ [".cpp"], ["."], [{"prefixes":[""]}]],
    #             [ ["hpp"],  ["."] ]
    #           ]
    # ls ./foo/src => test1.cpp, test1.hpp
    # ./foo/src/test1.cpp should switch to ./src/test1.hpp
    # ./foo/src/test1.hpp should switch to ./src/test1.cpp
    specTest1 = [
        [[".cpp"], ["."], {"prefixes":[""]} ],
        [[".hpp"], ["."]]
    ]

    # @unittest.skip("development ongoing")
    def test1_husband_extended_dict_1(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.cpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.hpp"), wife)

    #@unittest.skip("development ongoing")
    def test1_husband_extended_2(self):
        wife = fast_switch(0, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.hpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.cpp"), wife)



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
        [[".cpp"], ["src"]],
        [[".h"],   ["include"]]
    ]

    #@unittest.skip("development ongoing")
    def test2_SrcHdrInTwoSibblingDirs1(self):
        wife = fast_switch(0, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                  "tests_db",
                                                                  "Test_2",
                                                                  "src",
                                                                  "test2.cpp")),
                           self.specTest2)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_2", "include", "test2.h"), wife)

    #@unittest.skip("development ongoing")
    def test2_SrcHdrInTwoSibblingDirs2(self):
        wife = fast_switch(0, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                  "tests_db",
                                                                  "Test_2",
                                                                  "include",
                                                                  "test2.h")),
                           self.specTest2)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_2", "src", "test2.cpp"), wife)

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
        [[".h"],   ["include/@-1"]]
    ]

    #@unittest.skip("development ongoing")
    def test3_HdrInPackageDir1(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_3",
                                                        "foo",
                                                        "src",
                                                        "test3.cpp")),
                           self.specTest3)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_3", "foo", "include", "foo", "test3.h"),
                             wife)
    #@unittest.skip("development ongoing")
    def test3_HdrInPackageDir2(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_3",
                                                        "foo",
                                                        "include",
                                                        "foo",
                                                        "test3.h")),
                           self.specTest3)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_3", "foo", "src", "test3.cpp"), wife)

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

    #@unittest.skip("development ongoing")
    def test4_SrcHdrInComplexPackageDir1(self):
        wife = fast_switch(0, "C++",
                           os.path.join(self.test_db,
                                        "Test_4",
                                        "foo",
                                        "src",
                                        "bar",
                                        "test4.cpp"),
                           self.specTest4)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_4", "foo", "include", "foo", "bar", "test4.h"), wife)

    #@unittest.skip("development ongoing")
    def test4_SrcHdrInComplexPackageDir2(self):
        wife = fast_switch(0, "C++",
                           os.path.join(self.test_db,
                                        "Test_4",
                                        "foo",
                                        "include",
                                        "foo",
                                        "bar",
                                        "test4.h"),
                           self.specTest4)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_4", "foo", "src", "bar", "test4.cpp"), wife)

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
        [[".js"], ["public/js"]],
        [["Spec.js"], ["../test"]]
    ]

    #@unittest.skip("development ongoing")
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
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_5", "foo", "test", "test5Spec.js"),
                             wife)

    #@unittest.skip("development ongoing")
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
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_5", "foo", "public", "js", "test5.js"),
                             wife)

    # Test 6
    # ./Test_6/test/test_test6.cpp should switch to ./Test_6/test6.py
    # ./Test_6/test6.py should switch to ./foo/test/test_test6.py
    specTest6 = [
                  [[".py"], [".", "..", ""] ],
                  [['.py'], [".", "./test", "./tests"], {"prefixes": ["test_", "test"]}]
                ]

    #@unittest.skip("development ongoing")
    def test6_ExtendedSyntax_WithPrefixForTest1(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_6",
                                                        "test6.py")),
                           self.specTest6)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6",  "test", "test_test6.py"),
                             wife)

    #@unittest.skip("development ongoing")
    def test6_ExtendedSyntax_WithPrefixForTest2(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_6",
                                                        "test",
                                                        "test_test6.py")),
                            self.specTest6)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6", "test6.py"),
                             wife)


    # Test 6 Inverted
    # ./foo/test/test_file.py should switch to ./foo/test6.py
    # ./foo/file.py should switch to ./foo/test/test_test6.py
    # Inverse the order in the settings of test 6

    specTest6 = [
                  [['.py'], [".", "./test", "./tests"], {"prefixes": ["test_", "test"]}],
                  [[".py"], [".", ""] ]
                ]

    #@unittest.skip("development ongoing")
    def test6_CppWithTestDir_settingInverted1(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_6",
                                                        "test6.py")),
                           self.specTest6)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6",  "test", "test_test6.py"),
                             wife)

    #@unittest.skip("development ongoing")
    def test6_CppWithTestDir_settingsInverted2(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_6",
                                                        "test",
                                                        "test_test6.py")),
                           self.specTest6)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6", "test6.py"),
                             wife)


    # Test 7
    # ls ./ => main.template.html, main.controller.js
    # ./test7_A.template.html => ./test7_A.controller.js
    # ./test7_A.controller.js => ./test7_A.template.html
    specTest7 = [
                  [[".controller.js"], ["."]],
                  [['.template.html'], ["."]],
                  [['.service.js'], ["."]]
                ]

    #@unittest.skip("development ongoing")
    def test7_ExtendedSyntax_WithPrefixForTest1(self):
        wife = fast_switch(0, "js",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_7",
                                                        "test7_A.controller.js")),
                           self.specTest7)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_7",  "test7_A.template.html"),
                             wife)

    #@unittest.skip("development ongoing")
    def test7_ExtendedSyntax_WithPrefixForTest2(self):
        wife = fast_switch(0, "html",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_7",
                                                        "test7_A.template.html")),
                           self.specTest7)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_7",
                                          "test7_A.service.js"),
                             wife)

    #@unittest.skip("development ongoing")
    def test7_ExtendedSyntax_WithPrefixForTest3(self):
        wife = fast_switch(0, "html",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_7",
                                                        "test7_A.service.js")),
                           self.specTest7)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_7",
                                          "test7_A.controller.js"),
                             wife)


    def test7_B_ExtendedSyntax_WithPrefixForTest1(self):
        wife = fast_switch(0, "js",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_7",
                                                        "test7_B.controller.js")),
                           self.specTest7)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_7",  "test7_B.service.js"),
                             wife)

    #@unittest.skip("development ongoing")
    def test7_B_ExtendedSyntax_WithPrefixForTest2(self):
        wife = fast_switch(0, "js",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_7",
                                                        "test7_B.service.js")),
                           self.specTest7)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_7",
                                          "test7_B.controller.js"),
                             wife)

    # Test 8
    # ./foo/src/bar/test4.cpp => ./foo/include/foo/bar/test4.h
    # ./foo/include/foo/bar/file.h => ./foo/src/bar/test4.cpp
    # ["C++", "C"],
    specTest8 = [
                  [[".cpp"], ["../../src/."],       {"prefixes":[""]}],
                  [[".h"],   ["../include/@-2/@0"], {"prefixes":[""]}]
                ]

    #@unittest.skip("development ongoing")
    def test8_ExtendedSyntax_SrcHdrInComplexPackageDir1(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_8",
                                                        "foo",
                                                        "src",
                                                        "bar",
                                                        "test8_A.cpp")),
                           self.specTest8)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_8",
                                          "foo",
                                          "include",
                                          "foo",
                                          "bar",
                                          "test8_A.h",
                                          ),
                             wife)

    #@unittest.skip("development ongoing")
    def test8_ExtendedSyntax_SrcHdrInComplexPackageDir2(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_8",
                                                        "foo",
                                                        "include",
                                                        "foo",
                                                        "bar",
                                                        "test8_A.h")),
                           self.specTest8)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_8",
                                          "foo",
                                          "src",
                                          "bar",
                                          "test8_A.cpp"),
                             wife)


    # Test 9
    # ./Test_9/test9.cpp => ./Test_9/test_9.h
    # ./Test_9/test_9.h => ./Test_9/unittest/t_test9.cpp
    # ./Test_9/unittest/t_test9.cpp => ./Test_9/test9/cpp
    # ["C++", "C"],
    specTest9 = [
                  [[".cpp"], [".", ""]],
                  [[".h"],   ["."]],
                  [[".cpp"], ["./unittest"], {"prefixes":["t_"]}]
                ]
    def test9_A_3filesCppToH(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_9",
                                                        "test9_A.cpp")),
                           self.specTest9)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_9",
                                          "test9_A.h"),
                             wife)

    def test9_A_3filesHToT_cpp(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_9",
                                                        "test9_A.h")),
                           self.specTest9)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_9",
                                          "unittest",
                                          "t_test9_A.cpp"),
                             wife)

    def test9_A_3filesT_cppToCpp(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_9",
                                                        "unittest",
                                                        "t_test9_A.cpp")),
                           self.specTest9)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_9",
                                          "test9_A.cpp"),
                             wife)

    def test9_B_2filesCppToH(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_9",
                                                        "test9_B.cpp")),
                           self.specTest9)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_9",
                                          "test9_B.h"),
                             wife)

    def test9_B_2filesHToCpp(self):
        wife = fast_switch(0, "C++",
                           os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "tests_db",
                                                        "Test_9",
                                                        "test9_B.h")),
                           self.specTest9)
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_9",
                                          "test9_B.cpp"),
                             wife)


if __name__ == '__main__':
    unittest.main(verbosity=2)

