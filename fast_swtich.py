from __future__ import print_function
import sublime, sublime_plugin
import os.path
import re
import sys

version = "0.1"
settings = {}

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

def replace_all(seq, obj, replacement):
    for i, elem in with_index(seq):
        if elem == obj:
            seq[i] = replacement


def replace_current_directory(seq, replacement):
  '''
    Replace all single dot by replacement
    Ex: "."       => "src"
        "@-1/."   => "@-1/src"
        "../tata" => "../tata"
  '''
  pattern = "(?<!\.)(\.)(?!\.)"
  s = "."
  for i, elem in with_index(seq):
      seq[i] = re.sub(pattern, replacement, elem)


def replace_index(seq, replacement):
  '''
    Replacement is the splitted path of the file in view
  '''
  log(1, "replace_index: seq: [%s] replacement: [%s]" % (seq, replacement))
  nb = len(replacement)
  for i, elem in with_index(seq):
    log(1, "replace_index: i: [%d] elem: [%s]" % (i, elem))
    if '@' in elem:
      log(1, "replace_index: There is a \"@\" in elem: [%s]" % elem)
      m = re.search('(?<=@)-?[0-9]+', elem)
      if m:
        log(1, "replace_index: The match: [%s] Found a groups: %s" % (m, m.group(0)) )
        idx = int(m.group(0))
        log(1, "replace_index: nb: %d  idx: %d" % (nb, idx) )
        if idx > -nb and idx < nb:
          log(1, "replace_index: replace with %s" % replacement[idx])
        for g in m.groups():
          log(1, "replace_index: group: [%s]" % g)




class FastSwitchCommand(sublime_plugin.WindowCommand):
  def run(self):
    log(98, "run: Start")
    global settings
    # Set user options
    assign_settings()
    print(" Verbosity: Settings: %d" % settings.get("verbosity"))

    log(1, "Settings: all: %s" % settings)

    syntax = syntax_name(self.window.active_view())
    log(1, "Syntax: %s" % syntax)

    ext_dir = settings.get(syntax)
    if None == ext_dir:
      log(0, "Setting not found for the syntax %s" % syntax)
      return
    else:
      log(2, "Using settings for syntax %s: %s" % (syntax, ext_dir))


    # Get the current active file name and active folder
    path = self.window.active_view().file_name()
    log(1, "Current active file: %s" % path)
    if not path:
      log(0,"Can not switch script, file name can not be retrieved. Is a file currently open and active?")
      return


    base, filename =os.path.split(path)
    log(50, "Base: %s, filename: %s" % (base, filename))

    name, ext = os.path.splitext(filename)
    log(50, "Name: %s, ext: %s" % (name, ext))

    # Adding a '.' infront of the extension who don't already have the '.'
    for i in (0,1):
      tmp = []
      # add '.' if needed
      for e in ext_dir[i][0]:
        if e[0] == '.':
          tmp.append(e)
        else:
          log(2, "Adding a \".\" for extension: %s" % e)
          tmp.append('.'+ e)
      ext_dir[i][0] = tmp
      if ext in ext_dir[i][0]:
        idx = i;
    else:
      log(0, "The file extension [%s] not found in the list %s, %s for the syntax [%s]." % (ext, ext_dir[0][0], ext_dir[1][0], syntax))


    # Remove directory in the husband base
    splitted_base, last_dir = os.path.split(base)
    log(0, "Splitted base: %s   last dir: %s" % (splitted_base, last_dir))

    dirs = []
    head = splitted_base
    while head:
      (head, tail) = os.path.split(head)
      dirs += tail

    log(0, "The component of the path: %s", dirs)

    idx = (idx+1)%2;
    wife_ext = ext_dir[idx][0]
    wife_dir = ext_dir[idx][1]


    log(50, "Looking for file [%s] with one of the following extension [%s] in one of the directory [%s]." % (name, wife_ext, wife_dir))

    # If the list of directory has the current directory as an entry to seach
    # replace the "." by the current directory
    replace_current_directory(wife_dir, last_dir)
    log(50, "Replacing \".\" by \"%s\" if in the list" % last_dir)
    log(50, "Looking for file [%s] with one of the following extension [%s] in one of the directory [%s]." % (name, wife_ext, wife_dir))
    replace_index(wife_dir, ["tata", "tete", "titi"])
    log(50, "After replacing the index: Looking for file [%s] with one of the following extension [%s] in one of the directory [%s]." % (name, wife_ext, wife_dir))


    for d in wife_dir:
      for e in wife_ext:
        wife = os.path.join(splitted_base, d, name + e)
        log(1, "Looking for wife file: %s" % wife)
        if os.path.isfile(wife):
          self.window.open_file(wife)
          return
    else:
      log(1, "No counter part found for file: %s" % path)





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


