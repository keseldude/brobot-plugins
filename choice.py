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
from random import choice

class ChoicePlugin(bot.CommandPlugin):
    name = 'choice'
    def process(self, connection, source, target, args):
        if len(args) > 0:
            expr = u' '.join(args) # undo arg split
            choice_args = expr.split(u' or ')
            self.ircbot.privmsg(connection, target, choice(choice_args).strip())
        