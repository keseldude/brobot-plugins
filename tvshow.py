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
import urllib
from contextlib import closing
import itertools
import logging

TVRAGE_INFO_URL = 'http://services.tvrage.com/tools/quickinfo.php?show='

def get_tvrage_info(parameter):
    show_name = urllib.quote(parameter)
    url = TVRAGE_INFO_URL + show_name
    
    contents = None
    with closing(urllib.urlopen(url)) as url_obj:
        contents = url_obj.read()
    
    info = {}
    
    if not contents.startswith('<pre>'):
        info['error'] = u'Service currently unavailable. Try again later.'
        return info
    
    for line in itertools.islice(contents.splitlines(), 1, None):
        name, value = line.split('@')
        value = value.decode('utf-8')
        if name == 'Show Name':
            info['name'] = value
        elif name == 'Show URL':
            info['url'] = value
        elif name == 'Latest Episode':
            info['l_num'], info['l_title'], info['l_date'] = value.split('^')
        elif name == 'Next Episode':
            info['n_num'], info['n_title'], info['n_date'] = value.split('^')
        elif name == 'Ended':
            info['ended'] = value
        elif name == 'Status':
            info['status'] = value
    
    if not info:
        info['error'] = u'Show %s not available.' % parameter
    
    return info

class LastShowPlugin(bot.CommandPlugin):
    name = 'last'
    def process(self, connection, source, target, args):
        parameter = u' '.join(args)
        if parameter:
            info = get_tvrage_info(parameter)
            
            if 'error' in info:
                return {'action': self.Action.PRIVMSG,
                        'target': target,
                        'message': (info['error'],)
                        }
            else:
                return {'action': self.Action.PRIVMSG,
                        'target': target,
                        'message': (u'Last episode of %s: %s %s [%s]. %s' % \
                                    (info['name'], info['l_num'],
                                     info['l_title'], info['l_date'],
                                     info['url']),)
                        }
                                    

class NextShowPlugin(bot.CommandPlugin):
    name = 'next'
    def process(self, connection, source, target, args):
        parameter = u' '.join(args)
        if parameter:
            info = get_tvrage_info(parameter)
            if 'error' in info:
                return {'action': self.Action.PRIVMSG,
                        'target': target,
                        'message': (info['error'],)
                        }
            elif 'n_num' not in info:
                if 'status' in info and 'Ended' in info['status']:
                    return {'action': self.Action.PRIVMSG,
                            'target': target,
                            'message': (u'%s is over. It ended %s.' % \
                                        (info['name'], info['ended']),)
                            }
                else:
                    return {'action': self.Action.PRIVMSG,
                            'target': target,
                            'message': (u'Next episode info unavailable.',)
                            }
            else:
                return {'action': self.Action.PRIVMSG,
                        'target': target,
                        'message': (u'Next episode of %s: %s %s [%s]. %s' % \
                                    (info['name'], info['n_num'],
                                     info['n_title'], info['n_date'],
                                     info['url']),)
                        }
    
