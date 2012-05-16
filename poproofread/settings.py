# -*- coding: utf-8 -*-

"""
This file is a part of PoProofRead

Copyright (C) 2011-2012 Kenneth Nielsen <k.nielsen81@gmail.com>

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

import os

class SettingsCommon(object):
    def __init__(self):
        # Default values
        self.settings = {'font_size': 12,
                         'comment_window_height': 100,
                         'window_height': 600,
                         'window_width': 600,
                         'current_dir': os.getenv("HOME")
                         }

    def __getitem__(self, key):
        return self.settings[key]

    def __setitem__(self, key, value):
        self.settings[key] = value


class SettingsFromFile(SettingsCommon):
    def __init__(self):
        # Consider what to do on other platforms
        self.settings_file = (os.environ['HOME'] + os.sep +
                              '.config/poproofread/settings')
        SettingsCommon.__init__(self)
        self.read()

    def read(self):
        try:
            with open(self.settings_file) as f:
                loaded_settings = json.loads(f.read())
                self.settings.update(loaded_settings)
        except IOError:
            pass  # Write real exception here

    def write(self):
        if not os.access(os.path.dirname(self.settings_file), os.F_OK):
            os.mkdir(os.path.dirname(self.settings_file))
        try:
            with open(self.settings_file, 'w') as f:
                f.write(json.dumps(self.settings))
        except IOError:
            pass  # Write real exception here


class SettingsFromSystem(SettingsCommon):
    pass

# Determine if system settings environment is available
try:
    import modulethatdoesnotexist

    class Settings(SettingsFromSystem):
        pass
except ImportError:
    import json
    import os

    class Settings(SettingsFromFile):
        pass
