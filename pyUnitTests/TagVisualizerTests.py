'''
Created on 01/03/2011

@author: tbelcher
'''

import unittest
import urllib2
import nose.tools as check

from google.appengine.ext import webapp

from TagDAGBuilder import TagDAGBuilderClass
from TagVisualizer import *


class FileTagSourceClass:
    
    type = None
    directory = None
    path = "E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\"
    
    def __init__(self, dataset):
        self.type = dataset
        self.directory = ("shortTagDag" if self.type == "short" else "mediumTagDag" ) 
        self.directory += "\\"
    #end __init__    

    def FetchMasterTagList(self, unused):
        fileName = self.path + self.directory + self.type + "taglist.json"
        fh = open(fileName, "r")
        data = fh.read()
        fh.close()
        return data
    #end FetchMasterTagList
    
    def FetchLinkedTagList(self, unused, tag):
        fileName = self.path + self.directory + tag + "links_" + self.type + ".json"
        if os.path.exists(fileName):
            fh = open(fileName, "r")
            data = fh.read()
            fh.close()
        else:
            data = ""
        #endif        
        return data
    #end FetchLinkedTagList

#end FileTagSourceClass


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass

    def TestPythonURLEncodes(self):
        user1 = "Zardoz 59"
        url1 = "1/76"
        encoded = urllib2.quote(url1, "")
        check.ok_(len(encoded) > 0)
    #end TestPythonURLEncodes    

    def Test_MakeDAGFromFileData(self):
        tv = TagVisualizerClass()
        tv.tsc = FileTagSourceClass("short")
        tv.tdbc.BuildTagDAG("Zardoz59", tv.tsc)
        result = tv.DAGToJSONString_JitFormat()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shortTagDAGJitFormat.json", "w")
        file.write(result)
        file.close()
    #end Test_MakeDAGFromFileData    

    def Test_MakeDAGFromFileData_Big(self):
        tv = TagVisualizerClass()
        tv.tsc = FileTagSourceClass("medium")
        tv.tdbc.BuildTagDAG("Zardoz59", tv.tsc)
        result = tv.DAGToJSONString_JitFormat()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\mediumTagDAGJitFormat.json", "w")
        file.write(result)
        file.close()
    #end Test_MakeDAGFromFileData_Big    

    def Test_QueryMasterTagsForUser(self):
        ntsc = NetworkTagSourceClass() 
        result = ntsc.FetchMasterTagList("Zardoz59")
        file = open("c:\\TEMP\\mastertaglist.json", "w")
        file.write(result)
        file.close()
    #end Test_QueryMasterTagsForUser   

    def Test_MakeDAGFromNetworkFetch(self):
        pass
        #tv = TagVisualizerClass()
        #tv.tdbc.BuildTagDAG("Zardoz59", tv) 
        #result = tv.DAGToJSONString_ArborFormat()
        #result = tv.DAGToJSONString_JitFormat()
        #file = open("c:\\TEMP\\bigpicture.json", "w")
        #file.write(result)
        #file.close()
    #end Test_QueryTagsForUser   



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()