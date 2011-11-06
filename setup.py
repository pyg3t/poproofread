#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py
This file is a part of PoProofRead.

Copyright (C) 2011 Kenneth Nielsen <k.nielsen81@gmail.com>

PoProofRead is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from distutils.core import setup
import poproofread

long_description = """\
PoProofRead is a simple application for fast and easy 
proofreading and commenting of po and podiff files"""
scripts = ['bin/poproofread-gtk']
# The next two lines have not yet been added to the setup call
#requires = ['gtk (2.24.0)', 'pango']
provides = ['poproofread ({0})'.format(poproofread.__version__)]
data_files = [('../gui', ['gui/poproofread_gtk_gui.glade']),
              ('../graphics', ['graphics/192.png']),
              ('/usr/share/poproofread', ['graphics/192.png']),
              ('/usr/share/applications', ['poproofread.desktop'])
              ]
classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Environment :: X11 Applications',
    'Environment :: X11 Applications :: Gnome',
    'Environment :: X11 Applications :: GTK',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Localization',
    ]

setup(name='PoProofRead',
      version=poproofread.__version__,
      author='Kenneth Nielsen (TLE)',
      author_email='k.nielsen81@gmail.com',
      maintainer='Kenneth Nielsen (TLE)',
      maintainer_email='k.nielsen81@gmail.com',
      url='https://launchpad.net/poproofread',
      description='PoProofRead, a po and podiff file proofreader',
      long_description=long_description,
      download_url='https://launchpad.net/poproofread/+download',
      classifiers=classifiers,
      platforms='any',
      license='GPL',
      packages=['poproofread'],
      scripts=scripts,
      provides=provides,
      data_files=data_files
      )
