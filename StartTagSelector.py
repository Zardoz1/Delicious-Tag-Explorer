'''
Created on 03/05/2011

@author: tbelcher
'''

import os
import logging
import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from gaesessions import get_current_session

from TagDAGBuilder import TagDAGBuilderClass
from TagSource import NetworkTagSourceClass 
from MyMetaData import MyMetaDataManager


class StartTagSelectorClass(webapp.RequestHandler):

    def post(self):
        
        try:  
            
            (word_list, autocomplete_list) = self.postWorker(NetworkTagSourceClass())
            stuff = { 'tagList' : word_list, 'autocompleteList' : autocomplete_list }
            dir = os.path.dirname(__file__)
            path = os.path.join(dir, 'templates', 'startTagSelector.html')
            self.response.out.write(template.render(path, stuff))
                        
        except Exception, data:
            logging.error("Exception raised: " + str(data))
            self.error(404)
        #end try/catch
        
    #end post    

    def post_worker(self, tagSource):

        userName = cgi.escape(self.request.get('getUserName'))
        if userName is not None:

            tdbc = TagDAGBuilderClass()
            dbm = MyMetaDataManager()
     
            #do we already know this user?
            user = dbm.GetUser(userName)
            if user is None:
                logging.info("Fetching master tag list for NEW user '" + userName + "'")
    
                #see if the user is known to Delicious *and* has some tags
                tagsetString = tagSource.FetchMasterTagList(userName)
                if tagsetString is None or len(tagsetString) < 2:
                    logging.error("NEW user '" + userName + "' has no tags!")
                    raise Exception("The user '" + userName + "' has no tags!")
                #endif
                
                #new user, with tags, if we get here...
                user = dbm.NewUser(userName)
                tdbc.StoreMasterTagList(user, tagsetString)
            else:
                #else we have the tags for them already...    
                logging.info("Regenerating master tag list for KNOWN user '" + userName + "'")
            #endif
            
            #reset the session even if it is the same "user"
            session = get_current_session()
            if session is not None:
                if session.is_active():
                    session.terminate()
                #endif   
                session['user'] = user
                session['name'] = userName
            #endif         
            
            taglist = tdbc.GetCompleteVertexSetForNamedUser(user.key().name())
            #sort alphabetically
            taglist.sort(key=lambda tag: unicode.lower(tag.key().name()))
    
            # compute the average count of tags and only show above-average ones
            # in the cloud.
            for tag in taglist:
                user.IncTagCount(tag.ttlCount)
            #endfor
            user.GenerateTagStats()
            
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
            autocomplete_list = "["
            
            filteredCount = 0
            for tag in taglist:
                autocomplete_list = autocomplete_list + '"' + tag.key().name() + '",\n'
                if tag.ttlCount >= user.tagCountAverage:
                    filteredCount = filteredCount + 1
                    word_list = word_list + '{text: "' + tag.key().name() + ' ", ' 
                    word_list = word_list + "weight: " + str(tag.ttlCount) + "}, " + "\n"
                #endif    
            #endfor
            word_list = word_list.rstrip(", \n") + "]"
            autocomplete_list = autocomplete_list.rstrip(", \n") + "]" 
    
            logging.info("Found " + str(user.numTags) + " for user '" + userName + "'. ")
            logging.info("Returned " + str(filteredCount) + " tags for the cloud.")
        
            return (word_list, autocomplete_list)
        else:
            logging.error("Bad or unknown user passed into StartTagSelectorClass::post() '" + userName + "'")
            raise Exception("Bad or unknown user passed into StartTagSelectorClass::post() '" + userName + "'")
        #endif
        
        return (None, None)
    
    #end post_worker    
    
#end class StartTagSelectorClass
#eof               