'''
Created on 01/03/2011

@author: tbelcher
'''

import os
os.environ['SERVER_SOFTWARE'] = 'Development'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import string
import urllib2
from decimal import Decimal
import StringIO

import unittest
import nose.tools as check
from mock import Mock
from mock import patch

from google.appengine.ext import webapp
from google.appengine.ext import testbed
from google.appengine.ext import db

import gaesessions

from MyMetaData import MyMetaDataManager, MyUser
from TagDAGBuilder import TagEdge, TagVertex, TagDAGBuilderClass
from TagSource import FileTagSourceClass, TagSourceFactory
from TagVisualizer import TagVisualizerClass, StartVisualizerClass,\
    BranchVisualizerClass
from StartTagSelector import StartTagSelectorClass


class Test(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
    #end setUp

    def tearDown(self):
        _current_session = None
        
        self.testbed.deactivate()
        
        allEdges = []
        edgeQuery = TagEdge.all()
        for edge in edgeQuery:
            allEdges.append(edge.key())
        #end for
        db.delete(allEdges)
        
        allTags = []
        tagQuery = TagVertex.all()
        for tag in tagQuery:
            allTags.append(tag.key())
        #end for
        db.delete(allTags)
        
        allUsers = []
        userQuery = MyUser.all()
        for user in userQuery:
            allUsers.append(user.key())
        #end for
        db.delete(allUsers)
    #end tearDown        

    def TestPythonURLEncodes(self):
        url1 = "1/76"
        encoded = urllib2.quote(url1, "")
        check.ok_(len(encoded) > 0)
    #end TestPythonURLEncodes    

    def Test_SetLocalTagSource(self):
        f = TagSourceFactory()
        x = f.IsRunningLocal()
        check.ok_(x == True)
        tv = TagVisualizerClass()
        check.ok_(isinstance(tv.tsc, FileTagSourceClass))
    #end Test_SetLocalTagSource    

    @patch('gaesessions.Session', spec_set=True)
    def Test_StartTagSelector_NewUser(self, session):
        
        #global _current_session
        gaesessions._current_session = session
        request = webapp.Request({"wsgi.input": StringIO.StringIO(),
                                  "CONTENT_LENGTH": 0,
                                  "METHOD": "GET",
                                })
        request.get = Mock(return_value="Zardoz59")
        
        response = webapp.Response()
        response.out = Mock()
        
        #class under test
        stsc = StartTagSelectorClass()
        stsc.initialize(request, response);
        (word_list, autocomplete_list) = stsc.post_worker(FileTagSourceClass('short'))
        
        check.ok_(word_list is not None)
        check.ok_(autocomplete_list is not None)
                        

                                
    #end Test_StartTagSelector_NewUser
    
    def Test_MakeDAGFromFileData(self):
        dbm = MyMetaDataManager()
        user = dbm.NewUser("Zardoz59")
        tv = TagVisualizerClass()
        tv.tsc = FileTagSourceClass('short')
        tv.tdbc.BuildCompleteTagDAG(user, tv.tsc)
        data = tv.tdbc.GetCompleteVertexSet()
        result = tv.DAGToJSONString_JitFormat(data)
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shortTagDAGJitFormat.json", "w")
        file.write(result)
        file.close()
    #end Test_MakeDAGFromFileData    

    def Test_MakeDAGFromFileData_Big(self):
        dbm = MyMetaDataManager()
        user = dbm.NewUser("Zardoz59")

        tv = TagVisualizerClass()
        tv.tsc = FileTagSourceClass('medium')
        tv.tdbc.BuildCompleteTagDAG(user, tv.tsc)
        data = tv.tdbc.GetCompleteVertexSet()
        result = tv.DAGToJSONString_JitFormat(data)
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\mediumTagDAGJitFormat.json", "w")
        file.write(result)
        file.close()
    #end Test_MakeDAGFromFileData_Big   
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()