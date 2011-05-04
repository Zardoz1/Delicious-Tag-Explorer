'''
Created on 04/05/2011

@author: tbelcher
'''
import unittest
import nose.tools as check
from google.appengine.ext import db
from MyMetaData import (MyMetaDataManager, MyUser)


class Test(unittest.TestCase):


    def setUp(self):
        #check that the db contents really have been deleted
        userQuery = MyUser.all()
        users = userQuery.fetch(100)
        check.ok_(len(users) == 0)
    #end setUp    

    def tearDown(self):
        allUsers = []
        userQuery = MyUser.all()
        for user in userQuery:
            allUsers.append(user.key())
        #end for
        db.delete(allUsers)
    #end tearDown   

    
    def Test_ManageUsers(self):
        dbm = MyMetaDataManager()
        doIExist = dbm.HasUser("Bill")
        check.ok_(doIExist == False)
        
        dbm.NewUser("Bill")
        doIExist = dbm.HasUser("Bill")
        check.ok_(doIExist == True)
        
        u2 = MyUser(None, "Ted")
        doIExist = dbm.HasUser("Ted")
        check.ok_(doIExist == False)
        u2.put()
        doIExist = dbm.HasUser("Ted")
        check.ok_(doIExist == True)
        u3 = dbm.GetUser("Ted")
        check.ok_(u3 is not None)
        check.ok_(u3.key() == u2.key())

    #end ManageUsersTest


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()