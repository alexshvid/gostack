#!/usr/bin/python

import os.path

# both imports are used in context
import openstack_conf
import openstack_pass

def trim_end_crln(s):
  while len(s) > 0:
    if s[-1] == '\n':
      s = s[:-1]
    elif s[-1] == '\r':
      s = s[:-1]
    else:
      break
  return s

#
# Patch file lines
# lines: List(String)
# props: Map(Tuple(old_value, new_value))
# return Tuple(lines: List(String), patched: Boolean)
#

def patch_list(lines, props):
  props = props.copy()
  rez = []
  patched = False
  group = ''
  for line in lines:
    sline = line.strip()
    if len(sline) > 2 and sline[0] == '[' and sline[-1] == ']':
      group = sline

    if '=' in line:
      eq = line.index('=')
      key = line[:eq].strip()
      value = line[eq+1:].strip()

      if props.has_key(key):
        oldv, newv = props[key]
        if (oldv == None or oldv == value) and newv != value:
          line = key + ' = ' + newv
          patched = True
        del props[key]

      elif props.has_key(group + key):
        oldv, newv = props[group + key]
        if (oldv == None or oldv == value) and newv != value:
          line = key + ' = ' + newv
          patched = True
        del props[group + key]

    rez.append(line)

  for key in props:
    oldv, newv = props[key]
    if len(key) > 0 and key[0] == '[' and ']' in key:
      closeb = key.index(']')
      group = key[:closeb+1]
      rkey = key[closeb+1:]

      try:
        rez.insert(rez.index(group)+1, rkey + ' = ' + newv)
      except:
        rez.append(group)
        rez.append(rkey + ' = ' + newv)
    else:
      rez.append(key + ' = ' + newv)
    patched = True

  if patched and len(rez) > 0 and len(rez[-1]) > 0:
    rez.append("")

  return (rez, patched)

#
# Patch file content
# str: String
# props: Map(Tuple(old_value, new_value))
# return Tuple(str: String, patched: Boolean)
#

def patch_str(s, props):
  plines, patched = patch_list(s.split('\n'), props)
  if patched:
    return ('\n'.join(plines), True)
  else:
    return (s, False)

#
# Patch file with props
# filename: String
# props: Map(Tuple(old_value, new_value))
# mkBak: True create .bak file
# return: True successfully patched
#

def patch_file(filename, props, mkBak=False):
  lines = []
  with open(filename,"r") as f:
    for line in f:
      lines.append(trim_end_crln(line))

  plines, patched = patch_list(lines, props)

  if patched and mkBak and not os.path.exists(filename + '.bak'):
    with open(filename + '.bak',"w") as f:
      f.write('\n'.join(lines))

  if patched:
    with open(filename,"w") as f:
      f.write('\n'.join(plines))

  return patched


#
# Template str
# str: String
# return: String
#

def template_str(s):
  rez_list = []
  start = 0
  while 1:
    b = s.find('${', start)
    if b < 0:
      break
    e = s.find('}', b)
    if e < 0:
      break
    rez_list.append(s[start:b])
    code = s[b+2:e]
    try:
      v = eval(code)
      if v.__class__.__name__ != 'str':
        v = str(v)
      rez_list.append(v)
    except e:
      print(e)
      print('error: evaluate %s in str %s' % (code, s) )
    start = e+1
  rez_list.append(s[start:])
  return ''.join(rez_list)

#
# Template list
# lines: List[String]
# return: List[String]
#

def template_list(lines):
  result = []
  for line in lines:
    result.append(template_str(line))
  return result

#
# Template file
# inf: String InputFileName
# outf: String OutputFileName
#

def template_file(inf, outf):
  lines = []
  with open(inf,"r") as f:
    for line in f:
      lines.append(trim_end_crln(line))

  lines = template_list(lines)

  with open(outf,"w") as f:
    f.write('\n'.join(lines))


