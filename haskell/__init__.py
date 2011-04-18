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
from subprocess import Popen, PIPE
import os.path
import logging

log = logging.getLogger(__name__)

plugin_package = os.path.dirname(os.path.abspath(__file__))

l_file = os.path.join(plugin_package, 'L.hs')

class HaskellEval(bot.CommandPlugin):
    name = 'haskell-eval'
    def eval(self, expr):
        process = Popen(['mueval', '-l', l_file, '-e', expr], stdin=PIPE,
                        stderr=PIPE, stdout=PIPE)
        data = process.communicate()
        log.debug(data)
        if len(data) == 2:
            out, err = data
            if out:
                output = out
            else:
                output = err
            
            lines = output.splitlines()[:5]
            if len(lines) == 1:
                line = lines[0][:117]
                if line != lines[0]:
                    line += u'...'
                result = (line,)
            else:
                result = lines
            
            return result
    
    def process(self, connection, source, target, args):
        expr = u' '.join(args)
        result = self.eval(expr)
        if result is not None:
            return {'action': self.Action.PRIVMSG,
                    'target': target,
                    'message': result}
    

class HaskellType(bot.CommandPlugin):
    name = 'haskell-type'
    def query_ghci(self, expr):
        inp = ":load %s\n:t %s" % (l_file, expr)
        
        process = Popen(['ghci', "-v0"],
                         stdin=PIPE, stderr=PIPE, stdout=PIPE)
        result = process.communicate(input=inp)
        if len(result) == 2:
            output, error = result
            if error:
                return error.splitlines()
            elif output:
                lines = map(str.strip, output.splitlines())
                return (u' '.join(lines), )
    
    def process(self, connection, source, target, args):
        expr = u' '.join(args)
        result = self.query_ghci(expr)
        if result is not None:
            return {'action': self.Action.PRIVMSG,
                'target': target,
                'message': result}
    
