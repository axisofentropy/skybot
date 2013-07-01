"""
twitter.py: written by Scaevolus 2009
retrieves most recent tweets
"""

import random
import re
from time import strptime, strftime

from util import hook

import twitter

def hasapikey(bot):
    api_key = bot.config.get("api_keys", {}).get("twitter", None)
    return api_key

@hook.command('twitter')
def fetch_twitter(inp, bot=None):
    ".twitter <user>/<user> <n>/<id>/#<hashtag>/@<user> -- gets last/<n>th "\
    "tweet from <user>/gets tweet <id>/gets random tweet with #<hashtag>/"

    if not hasapikey(bot):
        return None
    api = twitter.Api(**hasapikey(bot))

    def format_status(status):
        time = strftime('%Y-%m-%d %H:%M:%S',
             strptime(status.created_at,
             '%a %b %d %H:%M:%S +0000 %Y'))
        return "%s %s: %s" % (time, status.user.screen_name, status.text)

    # Tweet ID
    if re.match(r'^\d+$', inp):
        try:
            status = api.GetStatus(inp)
        except twitter.TwitterError, e:
            return 'error: ' + e.message[0]['message']
        return format_status(status)

    # Twitter screen name
    elif re.match(r'^\w{1,15}$', inp):
        try:
            results = api.GetUserTimeline(screen_name=inp)
        except twitter.TwitterError, e:
            return 'error: ' + e.message[0]['message']
        return format_status(results[0])

    # Twitter screen name and Nth tweet
    elif re.match(r'^\w{1,15}\s+\d+$', inp):
        name, num = inp.split()
        if int(num) > 199:
            return 'error: only supports up to the 199th tweet'
        try:
            results = api.GetUserTimeline(screen_name=name, count=200)
        except twitter.TwitterError, e:
            return 'error: ' + e.message[0]['message']
        try:
            return format_status(results[int(num)])
        except IndexError:
            return 'error: Not that many tweets returned.'

    # Hashtag search, random result
    elif re.match(r'^#\w+$', inp):
        try:
            results = api.GetSearch(inp)
        except twitter.TwitterError, e:
            return 'error: ' + e.message[0]['message']
        try:
            return format_status(random.choice(results))
        except IndexError:
            return 'error: No results.'

    # Not recognized
    else:
        return 'error: invalid request'
