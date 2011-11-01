# -*- coding: UTF-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import random
import urllib
import urllib2

import twitter

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

def getApi():
    return twitter.Api(consumer_key='consumer_key',
                       consumer_secret='consumer_secret',
                       access_token_key='access_token_key',
                       access_token_secret='access_token_secret',
                       cache=None)

def translate(text):
    opener = urllib2.build_opener()
    f = opener.open('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?appId=appId&text=' + urllib.quote(text) + '&from=ja&to=fi')
    translatedText = f.readline().decode('utf-8')
    return translatedText[2:len(translatedText) - 1]

def getRandomId():
    rand = random.random()
    query = Voice.all()
    query.order('rand')
    query.filter('rand >', rand)
    voices = query.fetch(1)
    if len(voices) == 0:
        query = Voice.all()
        query.order('rand')
        voices = query.fetch(1)
    voice = voices[0]
    voice.rand = rand
    voice.put()
    return voice.key().name()


class VoiceHandler(webapp.RequestHandler):
    def get(self, id):
        if id == '':
            id = getRandomId()
        newvoices = Voice.all().order('-__key__').fetch(10)
        sexyvoices = Voice.all().order('-eval_per').fetch(10)
        self.response.out.write(template.render('html/voice.html', {'id': id}))

    def post(self, dummyid):
        id = self.request.get('id')
        voice = Voice.get_by_key_name(id)
        voice.eval_count += 1
        if not voice.eval_yes:
            voice.eval_yes = 0
        if self.request.get('result') == 'yes':
            voice.eval_yes += 1
        print voice.eval_yes
        print voice.eval_count
        voice.eval_per = float(voice.eval_yes) / voice.eval_count
        voice.put()


class ProxyHandler(webapp.RequestHandler):
    def get(self, id):
        voice = Voice.get_by_key_name(id)
        opener = urllib2.build_opener() 
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        f = opener.open('http://translate.google.com/translate_tts?tl=fi&q=' + urllib.quote(voice.text.encode('utf-8')))

        self.response.headers['Content-Type'] = 'audio/mpeg'
        self.response.out.write(f.read())
        

class GatherVoiceHandler(webapp.RequestHandler):
    def get(self):
        api = getApi()
        statuses = api.GetMentions()
        for status in statuses:
            key_name = str(status.id)
            if Voice.get_by_key_name(key_name):
                continue
            translatedText = translate(status.text[len('@eroinolisa '):].encode('utf-8'))
            voice = Voice(
                key_name = key_name,
                text = translatedText,
                eval_count = 0,
                eval_yes = 0,
                eval_per = 0.0,
                rand = random.random(),
            )
            voice.put()
            api.PostUpdate(u'@' + status.GetUser().GetScreenName() + u' Please hear my sexy voice http://eroino-lisa.appspot.com/voice/' + key_name, status)


class IndexHandler(webapp.RequestHandler):
    def get(self):
        newvoices = Voice.all().order('-__key__').fetch(10)
        sexyvoices = Voice.all().order('-eval_per').fetch(10)
        self.response.out.write(template.render('html/index.html', {
            'newvoices': newvoices, 'sexyvoices': sexyvoices }))


class Voice(db.Model):
    text = db.StringProperty()
    eval_count = db.IntegerProperty()
    eval_yes = db.IntegerProperty()
    eval_per = db.FloatProperty()
    rand = db.FloatProperty()
        
        
def main():
    application = webapp.WSGIApplication([('/voice/(.*)', VoiceHandler),
                                         ('/proxy/(.*)', ProxyHandler),
                                         ('/cron/gathervoice', GatherVoiceHandler),
                                         ('/', IndexHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
