'''
Created on 03/05/2011

@author: tbelcher
'''

import os
import logging
import cgi

from google.appengine.api.urlfetch_errors import *
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

from TagDAGBuilder import TagDAGBuilderClass
from TagVisualizer import NetworkTagSourceClass 
from MyMetaData import (MyMetaDataManager, MyUser)



class StartTagSelectorClass(webapp.RequestHandler):
    '''
    classdocs
    '''

    def post(self):
        
        try:  
            tdbc = TagDAGBuilderClass()
            tsc = NetworkTagSourceClass()
            dbm = MyMetaDataManager()
            
            userName = cgi.escape(self.request.get('getUserName'))
            if userName is not None:
             
                #do we already know this user?
                user = dbm.GetUser(userName)
                if user is None:
                    logging.info("Fetching master tag list for NEW user '" + username + "'")
                    #new user...
                    user = dbm.NewUser(userName)
                    tagsetString = tsc.FetchMasterTagList(userName)
                    tdbc.StoreMasterTagList(user, tagsetString)
                else:
                    #else we have the tags already...    
                    logging.info("Regenerating master tag list for KNOWN user '" + username + "'")
                #endif
 
                taglist = tdbc.GetCompleteVertexSetForNamedUser(user.key().name())
                
                #form up the expected tag cloud json
            
                '''
                var word_list = [{text: "Lorem", weight: 15},
                                 {text: "Ipsum", weight: 9, url: "http://jquery.com/", title: "jQuery Rocks!"},
                                 {text: "Dolor", weight: 6},
                                 {text: "Sit", weight: 7},
                                 {text: "Amet", weight: 5}
                               ...other words
                '''
                word_list = "["
                
                for tag in taglist:
                    word_list = word_list + '{text: "' + tag.key().name() + ' ", ' 
                    word_list = word_list + "weight: " + str(tag.ttlCount) + "}, " + "\n"
                #endfor
                word_list = word_list.rstrip(',') + "]"

                stuff = { 'tagList' : word_list }
                dir = os.path.dirname(__file__)
                path = os.path.join(dir, 'templates', 'startTagSelector.html')
                self.response.out.write(template.render(path, stuff))
            else:
                logging.error("Bad or unknown user passed into StartTagSelectorClass::post() '" + username + "'")
                self.error(404)
            #endif    
                        
        except Exception, data:
            logging.error("Exception raised: " + str(data))
            self.error(404)
        #end try/catch
        
    #end post    
    
#end class StartTagSelectorClass
#eof               