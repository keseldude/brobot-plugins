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
from datetime import datetime
import shelve

prefix = 'messages_'

class Messages(object):
    def __init__(self):
        self.messages = []
        self.notified = False
    
    def add(self, message):
        self.messages.append(message)
        self.notified = False
    
    def mark_notified(self):
        self.notified = True
    
    def mark_unnotified(self):
        self.notified = False
    

class Message(object):
    def __init__(self, nick, message):
        self.nick = nick
        self.message = message
        
        self.time = datetime.utcnow().ctime() + ' UTC'
    

class TellPlugin(bot.CommandPlugin):
    name = 'tell'
    def process(self, connection, source, target, args):
        if len(args) > 1:
            target_nick = args[0]
            raw_message = ' '.join(args[1:])
            message = Message(source.nick, raw_message)
            
            key = prefix + target_nick.encode('utf-8')
            
            shelf = shelve.open(self.shelf_path)
            try:
                if shelf.has_key(key):
                    messages = shelf[key]
                else:
                    messages = Messages()
                messages.add(message)
                messages.mark_unnotified()
                
                shelf[key] = messages
            finally:
                shelf.close()
            
            return {'action': self.Action.PRIVMSG,
                    'target': target,
                    'message': (u'Consider it done.',)
                    }
    

class ReadPlugin(bot.CommandPlugin):
    name = 'read'
    def process(self, connection, source, target, args):
        msgs = []
        key = prefix + source.nick
        shelf = shelve.open(self.shelf_path)
        try:
            if shelf.has_key(key):
                messages = shelf[key]
                for message in messages.messages:
                    msgs.append(u'%s said: %s [%s]' % (message.nick,
                                                       message.message,
                                                       message.time))
                del shelf[key]
        finally:
            shelf.close()
        
        if msgs:
            return {'action': self.Action.PRIVMSG,
                    'target': target,
                    'message': msgs
                    }
        else:
            return {'action': self.Action.PRIVMSG,
                    'target': target,
                    'message': (u'You have no messages.',)
                    }
    

class NotifyMessagesPlugin(bot.EventPlugin):
    name = 'notify-message'
    def process(self, connection, source='', target='', message=''):
        if message[0] != self.ircbot.command_prefix:
            key = prefix + source.nick
            shelf = shelve.open(self.shelf_path)
            try:
                if shelf.has_key(key):
                    messages = shelf[key]
                    if not messages.notified:
                        self.ircbot.privmsg(connection, target,
                            '%s: You have %d new message(s). /msg %s %s%s' % \
                                (source, len(messages.messages),
                                 connection.server.nick,
                                 self.ircbot.command_prefix, ReadPlugin.name))
                        messages.mark_notified()
                        shelf[key] = messages
            finally: 
                shelf.close()
    
