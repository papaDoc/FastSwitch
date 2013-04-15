FastSwitch
==========

A Sublime Text 2 plugin. To switch between files

A file of a given syntax will switch to a file with the same base name but with a different user defined extension. 
The file will be searched in a list of user define directory. The first file found respecting the criteria will be the one Sublime Text 2 will switch to.

Here is an example of a setting:
```
    // For the settings you define the syntax for which the extension and directory applies  
    // "syntax_X": { ["ext_A1, ext_A2"], ["directory_A1", directory_A2] },  
    //               ["ext_B1", "ext_B2"], ["directory_B1", "directory_B2"]  
    //             }
    // N.B. The "syntax_X" must be the string found in the lower right corner if the SublimeText2  
    // Example: "Plain Text", "C++". "Python", "Markdown"  
    //   
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
    // N.B. The "." means to look in the current directory  
    "C++": [  
             [ ["cpp"], ["src"] ],  
             [ ["h", "hpp"], [".", "include"] ]  
           ]  
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


The following examples are using the advance settings of the FastSwitch pluging to be able to switch between file
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
and with the following directory containing the given files:  
ls ./foo/src => tata.cpp, tata.hpp  
when in the following file: ./foo/src/tata.cpp, you should be able to switch to ./src/tata.hpp  
when in the following file: ./foo/src/tata.hpp should switch to ./src/tata.cpp

Example 2:
With the following setting :  
```
"C++": [  
         [ [".cpp"], ["src"] ],  
         [ [".h"], ["include"] ]  
       ] 
```  
and with the following directories containing the given file:  
ls ./foo/src => tete.cpp  
ls ./foo/include => tete.h  
using the FastSwitch pluging :  
when in the following file: ./foo/src/tete.cpp it will switch to ./include/tete.hpp  
when in the following file: ./foo/include/tete.hpp it will switch to ./src/tete.cpp  

Example 3:
With the following setting :  
```
"C++": [  
         [ [".cpp"], ["../src"] ],  
         [ [".h"], ["include/@-1"] ]  
       ]  
```
and with the following directories containing the given file:  
ls ./foo/src => titi.cpp  
ls ./foo/include/foo => titi.h  
when in the following file: ./foo/src/titi.cpp it will switch to ./foo/include/foo/titi.hpp  
when in the following file: ./foo/include/foo/titi.hpp it will switch to ./foo/src/titi.cpp  

Example 4:  
With the following setting :  
```
"C++": [  
         [ [".cpp"], ["../../src/."] ],  
         [ [".h"], ["../include/@-2/."] ]  
       ]
```
and with the following directories containing the given file:  
ls ./foo/src/bar => toto.cpp  
ls ./foo/include/foo/bar/ => toto.h  
when in the following file: ./foo/src/bar/toto.cpp it will switch to ./foo/include/foo/bar/toto.hpp  
when in the following file: ./foo/include/foo/bar/toto.hpp it will switch to ./foo/src/bar/toto.cpp




