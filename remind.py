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
from core.irc.structures import Channel
from datetime import datetime, timedelta
from threading import Timer
import time
import re
import itertools
import shelve
import logging

log = logging.getLogger(__name__)

class Reminder(object):
    def __init__(self, nick, task, future_time, server, target):
        self.nick = nick
        self.task = task
        self.future_time = future_time
        self.server = server
        self.target = target
    
    def __eq__(self, other):
        return self.nick == other.nick and self.task == other.task and \
               self.future_time == other.future_time and self.target == other.target


key = 'reminders'

class ReminderPlugin(bot.CommandPlugin):
    name = 'remind'
    TIME_SPLIT_RE = re.compile(r'([hswdm])')
    TIME_UNITS = {'s': lambda x: {'seconds': x},
                  'm': lambda x: {'minutes': x},
                  'h': lambda x: {'hours': x},
                  'd': lambda x: {'days': x}}
    def load(self):
        self.syntax = u'Syntax: %s%s <nick|me> <AdBhCmDs> <task>' % \
                                    (self.ircbot.command_prefix, self.name)
        load_timer = Timer(3, self.load_reminders)
        load_timer.daemon = True
        load_timer.start()
    
    def process(self, connection, source, target, args):
        if len(args) < 2:
            return {'action': self.Action.PRIVMSG,
                    'target': target,
                    'message': (self.syntax,)
                    }
        
        nick = args[0]
        
        if unicode.isdigit(nick[0]):
            nick = source.nick
        else:
            if nick.lower() == u'me':
                nick = source.nick
            else:
                channel = self.ircbot.find_channel(connection.server, target)
                if channel is None:
                    return {'action': self.Action.PRIVMSG,
                            'target': target,
                            'message': (self.syntax,)
                            }
                elif not channel.in_channel(nick):
                    return {'action': self.Action.PRIVMSG,
                            'target': target,
                            'message': (u'User not in channel.',)
                            }
            args = args[1:]
        
        amount_of_time = self.TIME_SPLIT_RE.split(args[0])
        delta = self.get_timedelta(amount_of_time)
        if delta is None:
            return {'action': self.Action.PRIVMSG,
                    'target': target,
                    'message': (self.syntax,)
                    }
        
        future_time = datetime.utcnow() + delta
        
        task = u' '.join(args[1:])
        
        reminder = Reminder(nick, task, future_time, connection.server, target)
        self.store_reminder(reminder)
        
        timer = Timer(delta.total_seconds(), self.remind, args=(reminder,
                                                                connection))
        timer.start()
        
        message_object = u'you' if nick == source.nick else nick
        return {'action': self.Action.PRIVMSG,
                'target': target,
                'message': (u'Okay, I will remind %s to %s on %s UTC.' % \
                            (message_object, task, future_time.ctime()),)
                }
    
    def get_timedelta(self, amount_of_time):
        deltadict = {}
        
        for amt, unit in itertools.izip(itertools.islice(amount_of_time, 0,
                                                         None, 2),
                                        itertools.islice(amount_of_time, 1,
                                                         None, 2)):
            if unit not in self.TIME_UNITS: #error message
                return None
            
            amount = int(amt)
            if amount < 0: #error message
                return None
            
            deltadict.update(self.TIME_UNITS[unit](amount))
        
        return timedelta(**deltadict)
    
    def load_reminders(self):
        reminders = []
        shelf = shelve.open(self.shelf_path)
        try:
            if shelf.has_key(key):
                reminders = shelf[key]
        finally:
            shelf.close()
        
        for reminder in reminders:
            connection = self.ircbot.find_connection(reminder.server)
            if connection is None:
                self.remove_reminder(reminder)
            else:
                delta = reminder.future_time - datetime.utcnow()
                timer = Timer(delta.total_seconds(), self.remind, args=(reminder, connection))
                timer.start()
    
    def store_reminder(self, reminder):
        shelf = shelve.open(self.shelf_path)
        try:
            if shelf.has_key(key):
                reminders = shelf[key]
            else:
                reminders = []
            
            reminders.append(reminder)
            shelf[key] = reminders
        finally:
            shelf.close()
    
    def remove_reminder(self, reminder):
        shelf = shelve.open(self.shelf_path)
        try:
            if shelf.has_key(key):
                reminders = shelf[key]
                reminders.remove(reminder)
                shelf[key] = reminders
        except ValueError:
            log.error(u'Unable to remove reminder... something is wrong')
        finally:
            shelf.close()
    
    def remind(self, reminder, connection):
        message = u'%s: Reminding you to %s.' % (reminder.nick, reminder.task)
        
        if reminder.future_time < datetime.utcnow() - timedelta(minutes=2):
            message = message + u" (Sorry I'm so late!)"
        
        channel = Channel(connection.server, reminder.target)
        
        self.remove_reminder(reminder)
        
        if channel not in self.ircbot.channels:
            self.ircbot.privmsg(connection, reminder.nick, message)
        else:
            self.ircbot.privmsg(connection, reminder.target, message)
    
