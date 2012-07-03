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
import lastfm
import logging

log = logging.getLogger('')

log.debug(lastfm.__file__)

class LastFMPlugin(bot.CommandPlugin):
    def load(self):
        api_key = self.ircbot.settings['lastfm_api_key']
        self.lastfm_api = lastfm.Api(api_key)
    

class NPPlugin(LastFMPlugin):
    name = 'now-playing'
    def process(self, connection, source, target, args):
        if len(args) > 0:
            username = args[0]
            try:
                user = self.lastfm_api.get_user(username)
            except lastfm.LastfmError as e:
                log.error(e)
                return
            np = user.now_playing
            if not np:
                np = user.recent_tracks[0]
            return self.privmsg(target, np)

class ArtistTagsPlugin(LastFMPlugin):
    name = 'artist-tags'
    def process(self, connection, source, target, args):
        if len(args) > 0:
            search = u' '.join(args)
            artist = self.lastfm_api.get_artist(search)
            top_tags = map(lambda a: a.name, artist.top_tags[:8])
            format = u'Top Tags: %s' % u', '.join(top_tags)
            return self.privmsg(target, format)

class SimilarArtistPlugin(LastFMPlugin):
    name = 'similar-artists'
    def process(self, connection, source, target, args):
        if len(args) > 0:
            search = u' '.join(args)
            artist = self.lastfm_api.get_artist(search)
            similar_artists = map(lambda a: a.name, artist.similar[:5])
            format = u'Similar Artsts: %s' % u', '.join(similar_artists)
            return self.privmsg(target, format)

