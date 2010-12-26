#===============================================================================
# brobot
# Copyright (C) 2010  Michael Keselman
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#===============================================================================

from core import bot
import string
import random
from datetime import datetime, date, timedelta
import itertools
import operator
import struct
import re
import math
import decimal

def forbidden(*args, **kwargs):
    return 'No (forbidden content)'

FORBIDDEN_FUNCTIONS = ('__import__',
                       'open',
                       'file',
                       'exit',
                       'quit',
                       'compile',
                       'input',
                       'execfile',
                       'exec',
                       'reload',
                       'raw_input',
                       'print',
                       'memoryview')

class PythonEvalPlugin(bot.EventPlugin):
    EVAL_PREFIX = ','
    name = 'python-eval'
    def load(self):
        self.gs = {'string': string,
                   'random': random,
                   'datetime': datetime,
                   'date': date,
                   'timedelta': timedelta,
                   'itertools': itertools,
                   'operator': operator,
                   'struct': struct,
                   're': re}
        
        for x in dir(math):
            if not x.startswith('__'):
                self.gs[x] = getattr(math, x)
        
        for x in dir(decimal):
            if not x.startswith('__'):
                self.gs[x] = getattr(decimal, x)
        
        for func in FORBIDDEN_FUNCTIONS:
            self.gs[func] = forbidden
    
    def process(self, connection, source='', target='', message=''):
        if len(message) > 2 and message[0] == self.EVAL_PREFIX and \
            message[1] == u' ':
            expr = message[2:].strip()
            
            try:
                result = unicode(eval(expr, self.gs, {}))
                msg = result[:100]
                if result != msg:
                    msg += '...'
                
                self.ircbot.privmsg(connection, target, msg)
            except SyntaxError:
                self.ircbot.privmsg(connection, target, 'Syntax Error')
            except Exception, e:
                ename = e.__class__.__name__
                self.ircbot.privmsg(connection, target, '%s: %s' % (ename, e))
            

