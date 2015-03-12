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
        log(50, "get_prefixes: Ici 2 settings: %s" % (settings[idx][2]))
        if type(settings[idx][2]) == type(dict()):
            log(50, "get_prefixes: Ici 2.01 settings: %s" % (settings[idx][2]['prefixes']))
            prefixes = settings[idx][2]['prefixes']
        else:
            log(50, "get_prefixes: Ici 2.02")
            prefixes = settings[idx][2]
    return prefixes


def has_prefix(filename, prefixes):
    log(50, "has_prefix: start")
    if prefixes:
        log(50, "Ici 0")
        for prefix in prefixes:
            log(50, "Ici 0")
            prefix = prefix.strip()
            log(50, "Ici 1")
            if filename.startswith(prefix):
                log(100, "Using {!r} for my_prefix".format(prefix))
                return prefix
        return None
    return ""

def has_extension(filename, extensions):
    """
    Return the extension of the filename if it is one of the extensions or None
    """
    log(50, "has_extension: start")
    if extensions:
        for ext in extensions:
            ext = ext.strip()
            if my_basename.endswith(ext):
                return ext
    return None


def find_index(filename, settings):
    """
    Find the index of the setting to which the filename belongs
    Find the first settings iteration for which a prefix and an extension matches
    return a tuple [idx, ext, prefix] the index is -1 if not found
    """
    nb_transition = len(settings)
    for i in range(nb_transition):
        log(50, "find_index: Starting: %d, current: %d" % (starting_idx, i))
        extensions = setting[i][0]
        ext = has_extension(filename, extensions)
        if ext is not None:
            prefixes = get_prefixes(i, settings)
            if len(settings[i]) > 2 :
                log(50, "find_index: Ici 2 settings: %s" % (settings[i][2]))
                if type(settings[i][2]) == type(dict()):
                    log(50, "find_index: Ici 2.01 settings: %s" % (settings[i][2]['prefixes']))
                    prefixes = settings[i][2]['prefixes']
                else:
                    log(50, "find_index: Ici 2.02")
                    prefixes = settings[i][2]
            prefix = has_prefix(filename, prefixes)
            if prefix is not None:
                return [i, ext, prefix]
    return [-1, None, None]



def filter_directory(wife_dir, path):
    # RR do we rellay need this ????? path = os.path.dirname(path)

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
        m = pattern.match(d)
        if d == ".":
            idx = 0
            log(100, "{!r} matches {}, which is {!r}".format(d, idx, parts[idx]))
            reconstructed_wife.append(parts[idx])
        elif m:
            idx = -(int(m.group(1)))
            log(100, "{!r} matches {}, which is {!r}".format(e, -idx, parts[idx]))
            reconstructed_wife.append(parts[idx])
        else:
            reconstructed_wife.append(d)
    # cannot use os.path.join since it will not handle the first element "" correctly
    # ("/a/b" is splitted into ["", "a", "b"])
    reconstructed_wife = os.path.sep.join(reconstructed_wife)
    reconstructed_wife = os.path.abspath(reconstructed_wife)
    log(100, "reconstructed_wife", reconstructed_wife)
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

    husband_idx, husband_ext, husban_prefix = find_index(filename, settings)
    if husband_idx != -1:
        husband_basename = filename[:len(husband_ext)+1]
        husband_basename = husband_basename[len(husband_prefix):]

        log(50, "Index: \"%d\"" Husband: \"%s\" has prefix \"%s\", basename: \"%s\" and extension \"%s\"" % (husband_idx, husband_filename, husband_prefix, husband_basename, husband_ext))

        for wife_idx in range(husband_idx, nb_transition+husband_idx):
            wife_idx = (i + 1) % nb_transition
            wife_extensions = settings[wife_idx][0]
            wife_directories = settings[wife_idx][1]
            wife_prefixes = get_prefixes(wife_idx, settings)

            log(50, "Index: \"%d\" Wife: extensions: %s directories:%s" % (wife_idx, wife_extensions, wife_directories, wife_prefixes))


            # Split the base since the current directory might be needed
            # and because every is with respect to the base - last_dir
            splitted_base, last_dir = os.path.split(base)
            log(50, "Splitted base: %s   last dir: %s" % (splitted_base, last_dir))

            log(INFO, "Looking for file \"%s\" with one of the following extensions %s in one "
                      "of the sub directories %s with one of the prefixes %s in the path \"%s\"" % (
                      husband_basename, wife_extensions, wife_directories, wife_extensions, splitted_base))

            wife_dir = filter_directory(wife_dir, base)
            log(50, "The investigation wife directory with everything replaced: \"%s\"" % wife_dir)

            path = os.path.join(splitted_base, wife_dir)
            for wife_ext in wife_extensions:
                wife_ext = ('.' + wife_e if wife_e[0] != '.' else wife_e[1:])
                for wife_prefix in wife_prefixes:
                    log(50, "Investigating for file \"%s\" in directory \"%s\" with extension \"%s\" and prefix \%s\"" %
                            (husband_basename, path, wife_ext, wife_prefix))
                    wife = os.path.join(path, wife_prefix + husband_basename + wife_ext)
                    log(50, "Ici 1: wife\"%s\"" % { wife })
                    wife = os.path.abspath(wife)
                    log(50, "Ici 2: wife\"%s\"" % { wife })
                    log(INFO, "Looking for wife file: %s" % wife)
                    if os.path.isfile(wife):
                        log(INFO, "Found a wife file: %s" % wife)
                        return wife

    log(INFO, "The file [%s] has no extension found in the list %s, %s for the syntax [%s]." %
            (filename, settings[0][0], settings[1][0], syntax))

def extended_fast_switch(verbose_level, syntax, path, extended_settings):
    global current_verbosity
    current_verbosity = verbose_level

    log(50, "")
    log(1, "Analysing: {!r}, syntax: {!r}".format(path, syntax))
    for extended_setting in extended_settings:
        if syntax not in extended_setting['syntaxes']:
            continue
        log(3, "Selecting configuration for syntax {}: {!r}".format(syntax, extended_setting))
        for ith, transition in enumerate(extended_setting['transitions']):
            log(100, "transition number {!r}".format(ith + 1))
            my_extensions = transition['my_extensions']
            my_prefixes = transition['my_prefixes']
            wife_directories = transition['wife_directories']
            wife_prefixes = transition['wife_prefixes']
            wife_extensions = transition['wife_extensions']

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
                        log(100, "Using {!r} for my_prefix".format(found_prefix))
                        break

                if found_prefix is None:
                    continue
            else:
                found_prefix = ""

            log(1, "Selecting transition {}' for file '{}'".format(ith, path))
            log(2, "  my extension:", found_ext)
            if found_prefix:
                log(2, "  my prefix:", found_prefix)
            log(2, "  wife directories:", wife_directories)
            log(2, "  wife prefixes:", wife_prefixes)
            log(2, "  wife extensions:", wife_extensions)

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
                log(60, "Searching wife of {!r} with prefix {!r} and extension {!r} "
                    "in directory {!r}"
                    .format(path, wife_prefix, wife_extension, wife_relative_dir))
                if wife_relative_dir == ".":
                    wife_relative_dir = ""
                if not wife_relative_dir and not wife_prefix and not wife_extension:
                    # will find myself!
                    continue
                wife_dir = os.path.dirname(path)
                if wife_relative_dir:
                    wife_dir = os.path.join(wife_dir, wife_relative_dir)
                    wife_dir = filter_directory(wife_dir, path)
                    wife_dir = os.path.abspath(wife_dir)
                    log(100, "  Wife directory: {!r}".format(wife_dir))
                wife_basename = my_basename
                log(100, "  My name is:", wife_basename)
                # Removing my prefix
                if found_prefix:
                    wife_basename = wife_basename[len(found_prefix):]
                    log(100, "wife basename after having removed prefix {!r}: {!r}"
                        .format(found_prefix, wife_basename))
                wife_basename = wife_basename[:-len(found_ext)] + wife_extension
                wife_basename = wife_prefix + wife_basename
                log(100, "  My name with wife_extension {!r} and wife prefix {!r}: {!r}"
                    .format(wife_extension, wife_prefix, wife_basename))
                # Adding wife prefix
                wife_path = os.path.join(wife_dir, wife_basename)
                wife_path = os.path.abspath(wife_path)
                log(100, "File exists {!r}? {!r}".format(wife_path, os.path.exists(wife_path)))
                if os.path.exists(wife_path):
                    log(100, "Found wife: {!r}".format(wife_path))
                    return wife_path

    log(1, "No wife found for file {!r}".format(path))


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

    @unittest.skip("development ongoing")
    def test1_SrcHdrInSameDir1(self):
        wife = fast_switch(100, "C++", os.path.join(self.test_db,
                                                  "Test_1",
                                                  "src",
                                                  "test1.cpp"),
                           self.specTest1)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_1", "src", "test1.hpp"), wife)

    @unittest.skip("development ongoing")
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

    # @unittest.skip("development ongoing")
    def test1_husband_extended_1(self):
        wife = fast_switch(100, "C++", os.path.join(self.test_db,
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
        wife = fast_switch(100, "C++", os.path.join(self.test_db,
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

    @unittest.skip("development ongoing")
    def test2_SrcHdrInTwoSibblingDirs1(self):
        wife = fast_switch(0, "C++", os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                  "tests_db",
                                                                  "Test_2",
                                                                  "src",
                                                                  "test2.cpp")),
                           self.specTest2)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_2", "include", "test2.h"), wife)

    @unittest.skip("development ongoing")
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

    @unittest.skip("development ongoing")
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
    @unittest.skip("development ongoing")
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

    @unittest.skip("development ongoing")
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

    @unittest.skip("development ongoing")
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
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_5", "foo", "test", "test5Spec.js"),
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
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_5", "foo", "public", "js", "test5.js"),
                             wife)

    # Test 6
    # ./foo/test/test_file.cpp should switch to ./foo/test6.cpp
    # ./foo/file.cpp should switch to ./foo/test/test_test6.cpp
    specTest6 = {
        'extended': [
            {
                'syntaxes': ["C++"],
                'transitions':[
                    {
                        'my_prefixes': ["test_", "test"],
                        'my_extensions': [".cpp"],
                        'wife_directories': [".", ".."],
                        'wife_prefixes': [],
                        'wife_extensions': ['.cpp'],
                    }, {
                        'my_prefixes': [],
                        'my_extensions': [".cpp"],
                        'wife_directories': [".", "test", "tests"],
                        'wife_prefixes': ["test_", "test"],
                        'wife_extensions': ['.cpp'],
                    }
                ]
            }
        ]
    }

    @unittest.skip("development ongoing")
    def test6_ExtendedSyntax_WithPrefixForTest1(self):
        wife = extended_fast_switch(0, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_6",
                                                                 "test6.cpp")),
                                    self.specTest6['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6",  "test", "test_test6.cpp"),
                             wife)

    @unittest.skip("development ongoing")
    def test6_ExtendedSyntax_WithPrefixForTest2(self):
        wife = extended_fast_switch(0, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_6",
                                                                 "test",
                                                                 "test_test6.cpp"
                                                                 )),
                                    self.specTest6['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6", "test6.cpp"),
                             wife)


    # Test 6
    # ./foo/test/test_file.cpp should switch to ./foo/test6.cpp
    # ./foo/file.cpp should switch to ./foo/test/test_test6.cpp
    specTest6 = {
                  [ [".cpp"], [".", ".."], { "prefixes": [""]} ],
                  [ [".cpp"], [".", "test", "tests"], { "prefixes": ["test_"] } ]
                }

    #@unittest.skip("development ongoing")
    def test6_ExtendedSyntax_WithPrefixForTest1(self):
        wife = extended_fast_switch(99, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_6",
                                                                 "test.cpp")),
                                    self.specTest6)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6",  "test", "test_test6.cpp"),
                             wife)

    @unittest.skip("development ongoing")
    def test6_ExtendedSyntax_WithPrefixForTest2(self):
        wife = extended_fast_switch(99, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_6",
                                                                 "test",
                                                                 "test_test6.cpp"
                                                                 )),
                                    self.specTest6)
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_6", "test6.cpp"),
                             wife)

    # Test 7
    # ls ./ => main.template.html, main.controller.js
    # ./main.template.html => ./main.controller.js
    # ./main.controller.js => ./main.template.html
    specTest7 = {
        'extended': [
            {
                'syntaxes': ["js", "html"],
                'transitions': [
                    {
                        'my_prefixes': [],
                        'my_extensions': [".controller.js"],
                        'wife_directories': ["."],
                        'wife_prefixes': [],
                        'wife_extensions': ['.template.html'],
                    }, {
                        'my_prefixes': [],
                        'my_extensions': [".template.html"],
                        'wife_directories': [],
                        'wife_prefixes': [],
                        'wife_extensions': ['.service.js'],
                    }, {
                        'my_prefixes': [],
                        'my_extensions': [".service.js"],
                        'wife_directories': [],
                        'wife_prefixes': [],
                        'wife_extensions': ['.controller.js'],
                    }
                ]
            }
        ]
    }

    @unittest.skip("development ongoing")
    def test7_ExtendedSyntax_WithPrefixForTest1(self):
        wife = extended_fast_switch(0, "js",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_7",
                                                                 "main.controller.js")),
                                    self.specTest7['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB", "Test_7",  "main.template.html"),
                             wife)

    @unittest.skip("development ongoing")
    def test7_ExtendedSyntax_WithPrefixForTest2(self):
        wife = extended_fast_switch(0, "html",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_7",
                                                                 "main.template.html"
                                                                 )),
                                    self.specTest7['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_7",
                                          "main.service.js"),
                             wife)

    @unittest.skip("development ongoing")
    def test7_ExtendedSyntax_WithPrefixForTest3(self):
        wife = extended_fast_switch(0, "html",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_7",
                                                                 "main.service.js"
                                                                 )),
                                    self.specTest7['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_7",
                                          "main.controller.js"),
                             wife)

    # Test 8 (use file from Test 4)
    # ./src/module/file.cpp => ./include/module/file.hpp
    # ./include/module/file.hpp => ./src/module/file.cpp
    specTest8 = {
        'extended': [
            {
                'syntaxes': ["C++", "C"],
                'transitions':[
                    {
                        'my_prefixes': [],
                        'my_extensions': [".cpp"],
                        'wife_directories': ["../../include/@-2/@0"],  # @0 == "."
                        'wife_prefixes': [],
                        'wife_extensions': ['.h'],
                    },
                    {
                        'my_prefixes': [],
                        'my_extensions': [".h"],
                        'wife_directories': ["../../../src/."],  # . == @0
                        'wife_prefixes': [],
                        'wife_extensions': ['.cpp'],
                    }
                ]
            }
        ]
    }

    @unittest.skip("development ongoing")
    def test8_ExtendedSyntax_SrcHdrInComplexPackageDir1(self):
        wife = extended_fast_switch(0, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_4",
                                                                 "foo",
                                                                 "src",
                                                                 "bar",
                                                                 "test4.cpp"
                                                                 )),
                                    self.specTest8['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_4",
                                          "foo",
                                          "include",
                                          "foo",
                                          "bar",
                                          "test4.h",
                                          ),
                             wife)

    @unittest.skip("development ongoing")
    def test8_ExtendedSyntax_SrcHdrInComplexPackageDir2(self):
        wife = extended_fast_switch(0, "C++",
                                    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "tests_db",
                                                                 "Test_4",
                                                                 "foo",
                                                                 "include",
                                                                 "foo",
                                                                 "bar",
                                                                 "test4.h",
                                                                 )),
                                    self.specTest8['extended'])
        self.assertPathEqual(os.path.join("TESTS_DB",
                                          "Test_4",
                                          "foo",
                                          "src",
                                          "bar",
                                          "test4.cpp"),
                             wife)

if __name__ == '__main__':
    unittest.main(verbosity=2)
