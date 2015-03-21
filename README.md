FastSwitch
==========

A Sublime Text 2/3 plugin. To switch between files

A file of a given syntax will switch to a file with the same base name but with a different user defined extension.
The file will be searched in a list of user define directory. The first file found respecting the criteria will be the one Sublime Text 2/3 will switch to.

Here is an example of a setting:
```
// For the settings you define the syntax for which the extension and directory applies
// "syntax_X": { ["ext_A1, ext_A2"], ["directory_A1", directory_A2] },
//               ["ext_B1", "ext_B2"], ["directory_B1", "directory_B2"]
//             }
// extended syntax:
// N.B. The "syntax_X" must be the string found in the lower right corner if the SublimeText 2/3
// Example: "Plain Text", "C++". "Python", "Markdown"
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
when in the following file: ./Test_8/foo/src/bar/test8.cpp it will switch to ./foo/include/foo/bar/test8.h<BR>
when in the following file: ./Test_8/foo/include/foo/bar/test8.h it will switch to ./foo/src/bar/test8.cpp<BR>




when in the following file ./Test6/test/test_test6.cpp it will switch to ./Test6/test6.cpp

    # ./main.template.html => ./main.controller.js
    # ./main.controller.js => ./main.template.html


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
