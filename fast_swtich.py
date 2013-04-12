from __future__ import print_function
import sublime, sublime_plugin
import os.path
import re
import sys

version = "0.1"
settings = {}

# Verbosity
ERROR   = 0
WARNING = 1
INFO    = 2

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
  global settings

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
  log(50, "replace_current_directory: orig: \"%s\" replacement: \"%s\"" % (orig, replacement))

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
      log(50, "replace_index: The match: [%s] Found a groups: %s" % (m, m.group(0)) )
      idx = int(m.group(0))
      log(50, "replace_index: nb: %d  idx: %d" % (nb, idx) )
      if idx > -nb:
        log(INFO, "Replacing the indicator index in [%s] by [%s]" % (orig, replacements[idx]) )
        new_str = re.sub(pattern2, replacements[idx], orig)
        log(INFO, "The original string [%s] is now: [%s]" % (orig, new_str) )
        orig = new_str
    else:
      log(ERROR, "The index indicator tag \"@\" found in \"%s\" is not followed by a negative number." % orig )
    cnt = cnt + 1
  return orig




class FastSwitchCommand(sublime_plugin.WindowCommand):
  def run(self):
    log(98, "run: Start")
    global settings
    # Set user options
    assign_settings()
    print(" Verbosity: Settings: %d" % settings.get("verbosity"))

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
      log(ERROR,"Can not switch script, file name can not be retrieved. Is a file currently open and active?")
      return


    base, filename =os.path.split(path)
    log(50, "Base: %s, filename: %s" % (base, filename))

    name, ext = os.path.splitext(filename)
    log(50, "Name: %s, ext: %s" % (name, ext))


    # Start working on finding the wife of the current file
    # - No work is done in advance everything is done when needed

    # Find in which of the two list the current extension belongs
    for i in (0,1):
      for j, e in with_index(ext_dir[i][0]): # Index 0 for the extension
        # add '.' if needed
        log(50, "The first char of \"%s\": %s " % (e, e[0]) )
        if e[0] != '.':
          log(50, "Adding a \".\" for extension: %s" % e)
          ext_dir[i][0][j] = '.' + e   # Do the replacement since the husband might be in the second list
        log(50, "Checking if \"%s\" equal \"%s\" "% (ext, ext_dir[i][0][j]) )
        if ext == ext_dir[i][0][j]:
          log(50, "\"%s\" is equal to \"%s\" "% (ext, ext_dir[i][0][j]) )
          wife_idx = (i+1)%2;
          wife_ext = ext_dir[wife_idx][0]
          wife_dir = ext_dir[wife_idx][1]

          # Split the base since the current directory might be needed
          # and because every is with respect to the base - last_dir
          splitted_base, last_dir = os.path.split(base)
          log(50, "Splitted base: %s   last dir: %s" % (splitted_base, last_dir))


          log(INFO, "Looking for file \"%s\" with one of the following extension %s in one of the sub directory %s in the path \"%s\"" % (name, wife_ext, wife_dir, splitted_base))

          for d in wife_dir:
            log(50, "Investigating directory: \"%s\"" % d)
            if "." in d:
              log(INFO, "Might need to replace the current directory indicator \".\" by \"%s\" in \"%s\"  " % (last_dir, d) )
              d = replace_current_directory(d, last_dir)
              log(50, "The new directory: \"%s\"" % d)


            # Need to replace the special caracter with the appropriate directory in the husband's file path
            if "@" in d:
              log(50, "There is a \"@\" in directory \"%s\" need to split the path \"%s\" "  % (d, splitted_base) )
              dirs = []
              head = splitted_base
              # while head:
              for i in (0,1):
                (head, tail) = os.path.split(head)
                log(50, "Adding \"%s\" to dirs: \"%s\"" % (tail, dirs) )
                dirs.append(tail)

              dirs.reverse()
              log(50, "The component of the path: %s" % dirs)
              log(INFO, "Might need to replace the \"@index\" in \"%s\" by one of the following %s" % (d, dirs) )
              d = replace_index(d, dirs)
              log(50, "The new directory: \"%s\"" % d)

            log(50, "The investigation directory with everything replaced: \"%s\"" % d)
            for wife_i, wife_e in with_index(wife_ext):
              log(50, "Investigating for file \"%s\" in directory \"%s\" with extension \"%s\"" % (name, os.path.join(splitted_base, d), wife_e) )
              # add '.' if needed
              if wife_e[0] != '.':
                log(50, "Adding a \".\" for the wife extension: %s" % wife_e)
                wife_ext[wife_i] = '.' + wife_e

              wife = os.path.join(splitted_base, d, name + wife_ext[wife_i])
              log(INFO, "Looking for wife file: %s" % wife)
              if os.path.isfile(wife):
                log(INFO, "Found a wife file: %s" % wife)
                self.window.open_file(wife)
                return

    else:
      log(INFO, "The file extension [%s] not found in the list %s, %s for the syntax [%s]." % (ext, ext_dir[0][0], ext_dir[1][0], syntax))


if __name__ == "__main__":
  import sys

  scc = OppositeFileCommand()
  scc.run()



# Test 1
#  src="c:\src\vortextoolkit\trunk\vortex\vxcablesystem\src\ICD\VxProducer.cpp"
#  include="c:\src\vortextoolkit\trunk\vortex\vxcablesystem\include\VxCableSystem\ICD\VxProducer.cpp"

# Test 2
#  "C++": [
#             [ [".cpp"], ["src"] ],
#             [ ["h", "hpp"], [".", "include"] ]
#           ]
# ls ./src => tata.cpp, tata.hpp
# ./src/tata.cpp should switch to ./src/tata.hpp
# ./src/tata.hpp should switch to ./src/tata.cpp

# Test 3
#  "C++": [
#             [ [".cpp"], ["src"] ],
#             [ ["h", "hpp"], [".", "include", "@-2/."] ]
#           ]
#  ls .../foo/src/bar => titi.cpp
#  ls .../foo/include/foo/bar => titi.h
# ./src/tata.cpp should switch to ./src/tata.hpp
# ./src/tata.hpp should switch to ./src/tata.cpp


