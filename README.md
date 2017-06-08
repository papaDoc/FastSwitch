FastSwitch
==========

A Sublime Text 2/3 plugin. To switch between files

A file of a given syntax will switch to a file with the same base name but with a different user defined extension.
The file will be searched in a list of user defined directory. The first file found respecting the criteria will be the one Sublime Text 2/3 will switch to.

If the file is not found with this fast switch algorithm then the path is walked. If a walked path contains the substring of the user define directory it will
be searched for the file to switch to.

2017/06/08
----------
New features:
   - If the file is not found in the provided path, a new algorithm will be used based on the work of gmatte11/sublime-text-switch-file on github
     to walk through the path and search for a path containing as a substring the user defined directory.
     This is slower but will be able to find more with out giving too many paths.

2015/03/21
----------
New features:
  - It is now possible to switch to a file with a different prefix if a prefix is specified in the settings.<BR>
    The prefix is stripped from the filename as for the extension and the prefix and extension
    of the other line of the settings is added.<BR>
    See examples 6 and 9 below.
  - It is possible to cycle between more than 2 files, if the settings has more than 2 lines.>BR>
    See examples 7 and 9 below

Here is an example of a setting:
```
// For the settings you define the syntax for which the extension and directory applies
// "syntax_X": [
//               [["ext_A1, ext_A2"], ["directory_A1", directory_A2]],
//               [["ext_B1", "ext_B2"], ["directory_B1", "directory_B2"]]
//             ]
// N.B. The "syntax_X" must be the string found in the lower right corner if the SublimeText 2/3
// Example: "Plain Text", "C++". "Python", "Markdown"
//
// settings with the new feature:
// "syntax_Y": [
//               [["ext_A1, ext_A2"], ["directory_A1", directory_A2], {"prefixes": ["prefix_A1_", "prefix_A2_"]}],
//               [["ext_B1", "ext_B2"], ["directory_B1", "directory_B2"], {"prefixes": ["prefix_B_"]}],
//               [["ext_C1"], ["directory_C1", ""]]
//             ]
// N.B. The {"prefixes": ["prefix_A1", "prefix_A2"]} is optional and can be ommitted
//
//
// With the above settings when in syntax_X (Ex C++) and you are currently in the file:
//     .../foo/bar/directory_A1/file.ext_A1
//
// using the fastswitch pluging then the pluging will try to open the file:
//     foo/bar/directory_B1/file.ext_B1
//     foo/bar/directory_B1/file.ext_B2
//     foo/bar/directory_B2/file.ext_B1
//     foo/bar/directory_B2/file.ext_B2
//
//
// With the above settings when in syntax_Y and you are currently in the file:
//     .../foo/bar/directory_A1/prefix_A1_file.ext_A1
//
// using the fastswitch pluging then the pluging will try to open the file:
//     foo/bar/directory_B1/prefix_B_file.ext_B1
//     foo/bar/directory_B1/prefix_B_file.ext_B2
//     foo/bar/directory_B1/prefix_B_file.ext_B1
//     foo/bar/directory_B1/prefix_B_file.ext_B2
//     foo/bar/directory_B1/prefix_B_file.ext_B2
//     foo/bar/directory_C1/file.ext_C1
//     foo/bar/file.ext_C1
//
//
// The first existing file will be openned so the order is important.
//
//
// N.B. The "." will be replaced by the current directory
//      Ex: If you are currently in  c:\foo\src\bar\file.cpp the "include\." correspond to "include\bar"
//      The "@d" means to replace the tag by the corresponding directory in path of the current file.
//      d must be a negative number
//      Ex:
//           If you are currently in c:\foo\bar\src\file.cpp the "@-1" correspond to the directory "bar"
//
// For the C++ syntax, I'm using the following
"C++": [
         [ [".cpp"], ["src", "../src", "../../src/."] ],
         [ ["h", "hpp"], [".", "include", "include/@-1", "../include/@-2/."] ]
       ],
"verbosity": 0
```

With the above settings when in C++
If you are currently in the file:
  * .../foo/bar/src/file.cpp
using the FastSwitch pluging, the pluging will try to open the file:
  * .../foo/bar/src/file.h                    # because of the "."
  * .../foo/bar/src/file.hpp                  # because of the "."
  * .../foo/bar/include/file.h
  * .../foo/bar/include/file.hpp

If you are currently in the file:
  * .../foo/bar/include/file.hpp
using the FastSwitch pluging, the pluging will try to open the file:
  * .../foo/bar/src/file.cpp


The following examples are using the advance settings of the FastSwitch pluging to be able to switch between files
where the relation between the different directory tree is more complex.

For each example the setting is minimal to expose the current feature. All the settings can be combined to achieve
powerfull fast and versatile switch.

Example 1:
With the following setting :
```
 "C++": [
          [ [".cpp"], ["src"] ],
          [ ["hpp"], ["."] ]
        ]
```
 or
```
 "C++": [
          [ [".cpp"], ["."] ],
          [ ["hpp"], ["."] ]
        ]
```
and with the following directory containing the given files:<BR>
ls ./foo/src => test1.cpp, test1.hpp<BR>
when in the following file: ./foo/src/test1.cpp, you should be able to switch to ./src/test1.hpp<BR>
when in the following file: ./foo/src/test1.hpp should switch to ./src/test1.cpp<BR>

Example 2:
With the following setting :
```
"C++": [
         [ [".cpp"], ["src"] ],
         [ [".h"], ["include"] ]
       ]
```
and with the following directories containing the given file:<BR>
ls ./foo/src => test2.cpp<BR>
ls ./foo/include => test2.h<BR>
using the FastSwitch pluging :<BR>
when in the following file: ./foo/src/test2.cpp it will switch to ./include/test2.h<BR>
when in the following file: ./foo/include/test2.hpp it will switch to ./src/test2.cpp<BR>

Example 3:
With the following setting :
```
"C++": [
         [ [".cpp"], ["../src"] ],
         [ [".h"], ["include/@-1"] ]
       ]
```
and with the following directories containing the given file:<BR>
ls ./foo/src => test3.cpp<BR>
ls ./foo/include/foo => test3.h<BR>
when in the following file: ./foo/src/test3.cpp it will switch to ./foo/include/foo/test3.hpp<BR>
when in the following file: ./foo/include/foo/test3.hpp it will switch to ./foo/src/test3.cpp<BR>

Example 4:
With the following setting :
```
"C++": [
         [ [".cpp"], ["../../src/."] ],
         [ [".h"], ["../include/@-2/."] ]
       ]
```
and with the following directories containing the given file:<BR>
ls ./foo/src/bar => test4.cpp<BR>
ls ./foo/include/foo/bar/ => test4.h<BR>
when in the following file: ./foo/src/bar/test4.cpp it will switch to ./foo/include/foo/bar/test4.hpp<BR>
when in the following file: ./foo/include/foo/bar/test4.hpp it will switch to ./foo/src/bar/test4.cpp<BR>

Example 5:
With the following setting:
```
 "Javascript": [
                 [[".js"], ["public/js"]],
                 [["Spec.js"], ["../test"]]
               ]
```
and with the following directories containing the given file:<BR>
ls ./foo/public/js => test5.js<BR>
ls ./foo/test => test5Spec.js<BR>
when in the following file ./foo/public/js/test5.js it will switch to ./foo/test/test5Spec.js<BR>
when in the following file ./foo/test/test5Spec.js it will switch to ./foo/public/js/test5.js<BR>

Example 6:
With the following settings:
```
"C++":[
        [[".py"], [".", "..", ""] ],
        [['.py'], [".", "./test", "./tests"], {"prefixes": ["test_", "test"]}]
      ]
```
and with the following directories containing the given file:<BR>
ls ./Test6 => test6.cpp<BR>
ls ./Test6/test => test_test6.cpp<BR>
when in the following file ./Test6/test6.cpp it will switch to ./Test6/test/test_test6.cpp<BR>
when in the following file ./Test6/test/test_test6.cpp it will switch to ./Test6/test6.cpp<BR>

Example 7:
With the following settings:
```
"Javascript": [
                [[".controller.js"], ["."]],
                [[".template.html"], ["."]],
                [[".service.js"], ["."]]
              ],
"HTML": [
          [[".template.html"], ["."]],
          [[".service.js"], ["."]],
          [[".controller.js"], ["."]],
        ]
```
and with the following directory containing the given files:<BR>
ls ./Test7 => test7_A.controller.js test7_A.service.js test7_A.template.html test7_B.controller.js test7_B.service.js<BR>
when in the following file ./Test7/test7_A.controller.js it will switch to ./Test7/test7_A.template.html<BR>
when in the following file ./Test7/test7_A.template.html it will switch to ./Test7/test7_A.service.js<BR>
when in the following file ./Test7/test7_A.service.js it will switch to ./Test7/test7_A.controller.js<BR>
when in the following file ./Test7/test7_B.controller.js it will switch to ./Test7/test7_B.service.js<BR>
when in the following file ./Test7/test7_B.service.js it will switch to ./Test7/test7_B.controller.js<BR>

Example 8:
With the following settings:
```
"C++": [
         [[".cpp"],       ["../../src/."],       {"prefixes":[""]}],
         [[".h", ".hpp"], ["../include/@-2/@0"], {"prefixes":[""]}]
       ]
```
and with the following directories containing the given file:<BR>
ls ./Test_8/foo/src/bar => test8_A.cpp test8_B.cpp<BR>
ls ./Test_8/foo/include/foo/bar/ => test8_A.h test8_B.hpp<BR>
when in the following file: ./Test_8/foo/src/bar/test8_A.cpp it will switch to ./foo/include/foo/bar/test8_A.h<BR>
when in the following file: ./Test_8/foo/include/foo/bar/test8_A.h it will switch to ./foo/src/bar/test8_A.cpp<BR>

Example 9:
```
"C++": [
          [[".cpp"], [".", ""]],
          [[".h"],   ["."]],
          [[".cpp"], ["./unittest"], {"prefixes":["t_"]}]
      ]
```
and with the following directories containing the given file:<BR>
ls ./Test_9/ => test9_A.cpp test9_A.h test9_B.cpp test9_B.h<BR>
ls ./Test_9/unittest/t_test9_A.cpp<BR>
when in the following file: ./Test_9/test9_A.cpp it will switch to ./Test_9/test9_A.h<BR>
when in the following file: ./Test_9/test9_A.h it will switch to ./Test_9/unittest/t_test9.cpp<BR>
when in the following file: ./Test_9/unittest/test9_A.cpp it will switch to ./Test_9/test9_A.cpp<BR>
when in the following file: ./Test_9/test9_B.cpp it will switch to ./foo/src/bar/test9_B.h<BR>
when in the following file: ./Test_9/test9_B.h it will switch to ./foo/src/bar/test9_B.cpp<BR>

Installation
------------

1. The easiest way to install FastSwitch is via the excellent Package Control Plugin.
   See http://wbond.net/sublime_packages/package_control#Installation
   * Once package control has been installed, bring up the command palette (cmd+shift+P or ctrl+shift+P)
   * Type Install and select "Package Control: Install Package"
   * Select FastSwitch from the list. Package Control will keep it automatically updated for you
2. If you don't want to use package control, you can manually install it
   * Go to your packages directory and type:
   ```git clone --recursive https://github.com/papaDoc/FastSwitch FastSwitch ```
   * To update run the following command:
   ```git pull && git submodule foreach --recursive git pull origin master```
   * Back in the editor, open up the command palette by pressing cmd+shift+P or ctrl+shift+P
   Type FastSwitch and open up the settings file you want to modify

Use the unit test to validate your changes:

```
python lib/fastswitch.py
```
