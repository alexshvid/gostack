#!/usr/bin/python

import os
import subprocess

def beroot():
  if os.geteuid() != 0:
    exit("Login as a root")

def run(cmd):
  p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, executable="/bin/bash")
  p.wait()
  out, err = p.communicate()
  if err != None:
    print('error: fail run command ' + cmd + ', error code = ' + str(err))
  return out

def run_std(cmd):
  p = subprocess.Popen(cmd, shell=True, stdin=None, executable="/bin/bash")
  p.wait()

