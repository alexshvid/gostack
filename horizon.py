#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_conf
import osutils

osutils.beroot()

osutils.run_std('apt-get install -y memcached python-memcache')

osutils.run_std('apt-get install -y libapache2-mod-wsgi openstack-dashboard')

osutils.run_std('service apache2 restart')


