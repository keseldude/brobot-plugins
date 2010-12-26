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
from core.irc.structures import User
from datetime import datetime, timedelta
import shelve

prefix = 'seen-info'

class SeenInfo(object):
    def __init__(self, channel, nick, time):
        self.channel = channel
        self.nick = nick
        self.time = time
    

class SeenPlugin(bot.CommandPlugin):
    name = 'seen'
    def format_timedelta(self, delta):
        message = ''
        if delta.days > 0:
            message += '%s days ' % delta.days
        
        hours = delta.seconds // 3600
        seconds = delta.seconds - (hours * 3600)
        minutes = seconds // 60
        seconds = seconds - (minutes * 60)
        
        if hours > 0:
            message += '%s hours ' % hours
        if minutes > 0:
            message += '%s min ' % minutes
        if seconds > 0:
            message += '%s sec ' % seconds
        
        return message.strip()
    
    def process(self, connection, source, target, args):
        if len(args) == 1:
            nick = args[0].lower().encode('utf-8')
            if nick == source.nick:
                self.ircbot.privmsg(connection, target, u'I see you!')
                return
            
            key = '%s_%s_%s' % (prefix, connection.server.host, nick)
            
            message = u'I have not seen %s.' % nick
            
            shelf = shelve.open(self.shelf_path)
            try:
                if shelf.has_key(key):
                    seen_info = shelf[key]
                    delta = datetime.utcnow() - seen_info.time
                    message = u'I last saw %s in %s %s ago.' % \
                                (seen_info.nick, seen_info.channel,
                                 self.format_timedelta(delta))
            finally:
                shelf.close()
            
            self.ircbot.privmsg(connection, target, message)
    

class UserTrackPlugin(bot.EventPlugin):
    name = 'user-track'
    def process(self, connection, source='', target='', args=None, message=''):
        if isinstance(source, User):
            key = '%s_%s_%s' % (prefix, connection.server.host, source.nick)
            
            now = datetime.utcnow()
            
            shelf = shelve.open(self.shelf_path)
            try:
                shelf[key] = SeenInfo(target, source.nick, now)
            finally:
                shelf.close()
    
