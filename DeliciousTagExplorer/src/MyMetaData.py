'''
    Created on 03/05/2011
    @author: tbelcher
'''

from google.appengine.ext import db


class MyUser(db.Model):

    displayName = db.StringProperty(db.Key)
    #nb not a datastore property!
    numTags = 0
    #nb not a datastore property
    tagCountAverage = 0

    def __init__(self, parent=None, key_name=None, **kwds):
        db.Model.__init__(self, parent, key_name, **kwds)
        self.displayName = key_name
    #end init   
    
    def IncTagCount(self, number):
        self.numTags = self.numTags + 1
        self.tagCountAverage = self.tagCountAverage + number
    #end IncTagCount   
    
    def GenerateTagStats(self):
        if self.numTags == 0:
            raise Exception("User " + self.key().name() + " has no tags!")
        #endif
        self.tagCountAverage = (0 if self.numTags == 0 else (self.tagCountAverage / self.numTags))
        return self.tagCountAverage
    #end GenerateTagStats 

#end class MyUser


class MyMetaDataManager(object):

    def NewUser(self, userName):
        if userName is None or len(userName) <= 2:
            raise Exception("Can't create new user; bad or empty user name.")
        #endif
                    
        user = MyUser(None, userName)
        user.put()
        return user
    #end NewUser    

    def GetUser(self, userName):
        if userName is None or len(userName) <= 2:
            return None
        else:
            u = MyUser.get_by_key_name(userName)
            return u
        #endif 
    #end GetUser
        
    def HasUser(self, userName):
        return self.GetUser(userName) is not None
    #end GetUser    

#end class MyMetaDataManager


#eof        