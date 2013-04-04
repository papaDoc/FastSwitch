FastSwitch
==========

A Sublime Text 2 plugin. To switch between files

A file of a given syntax will switch to a file with the same base name but with a different user defined extension. The file will be seached in a list of user define directory. The first file found respecting the criteria will be the one Sublime Text 2 will switch to.

Here is an example of a setting:
    // For the settings you define the syntax for which the extension and directory applies
    // "syntax_X": { ["ext_A1, ext_A2"], ["directory_A1", directory_A2] },
    //             ["ext_B1", "ext_B2"], ["directory_B1", "directory_B2"]
    //
    // N.B. The "syntax_X" must be the string found in the lower right corner if the SublimeText2
    // Example: "Plain Text", "C++". "Python", "Markdown"
    //           }
    // With the above settings when in mode_X (Ex C++) and you are currently in the file:
    // .../foo/bar/directory_A1/file.ext_A1
    // using the fastswitch pluging then the pluging will try to open the file:
    // foo/bar/directory_B1/file.ext_B1
    // foo/bar/directory_B1/file.ext_B2
    // foo/bar/directory_B2/file.ext_B1
    // foo/bar/directory_B2/file.ext_B2
    // The first existing file will be openned so the order is important.
    //
    // For the C++ syntax, I'm using the following
    // "C++": [
    //         [ ["cpp"], ["src"] ],
    //         [ ["h", "hpp"], [".", "include"] ]
    //        ]
    //
    // With the above settings when in C++ and you are currently in the file:
    // .../foo/bar/src/file.cpp
    // using the fastswitch pluging then the pluging will try to open the file:
    // foo/bar/src/file.h                    # because if the "."
    // foo/bar/src/file.hpp                  # because if the "."
    // foo/bar/include/file.h
    // foo/bar/include/file.hpp
    // You are currently in the file:
    // .../foo/bar/include/file.hpp
    // using the fastswitch pluging then the pluging will try to open the file:
    // foo/bar/src/file.cpp

The following line should be added to the User sublime key map file
  { "keys": ["alt+o"], "command": "fast_switch"}

}
