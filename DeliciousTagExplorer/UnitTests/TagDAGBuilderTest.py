'''
Created on 15/02/2011

@author: tbelcher
'''

import unittest
import nose.tools as check
from TagDAGBuilder import (TagDAGBuilderClass, TagVertex, TagEdge)
from google.appengine.ext import db


class Test(unittest.TestCase):


    def setUp(self):
        pass
    #end setUp

    def tearDown(self):
        allTags = []
        tagQuery = TagVertex.all()

        for tag in tagQuery:
            allTags.append(tag.key())
        #end foreach    
        db.delete(allTags)
    #end tearDown

    '''
        Tag1 <-> Tag2  count: 11
        Tag1 <-> Tag3         12   
        Tag2 <-> Tag3         13
        Tag2 <-> Tag4         14 
        Tag2 <-> Tag6         15 
        Tag3 <-> Tag4         16
        Tag5 <-> nothing       0 natch
    '''
    def Test_DAGStructureFromGoogleClasses(self):
        
        #first insert all known tags
        t1 = TagVertex(None, "Tag1")
        t1.ttlCount = 1
        t1.put()
        
        t2 = TagVertex(None, "Tag2")
        t2.ttlCount = 2
        t2.put()
        
        t3 = TagVertex(None, "Tag3")
        t3.ttlCount = 3
        t3.put()
        
        t4 = TagVertex(None, "Tag4")
        t4.ttlCount = 4
        t4.put()
        
        t5 = TagVertex(None, "Tag5")
        t5.ttlCount = 5
        t5.put()
        
        t6 = TagVertex(None, "Tag6")
        t6.ttlCount = 6
        t6.put()
        
        #now make an edge
        t1.AddEdge(t2, 11)
        #test what we've done...
        check.ok_(len(t1.edges) == 1)
        edgeKey = t1.edges[0]
        edge = db.get(edgeKey)
        check.ok_(edge != None)
        check.ok_(edge.edgeCount == 11)
        v = edge.myOtherVertex
        check.ok_(v != None)
        check.ok_(v.key() == t2.key())
        check.ok_(v.ttlCount == 2)
        check.ok_(t1.HasEdgeToVertex(t2.key()) == True)
        check.ok_(t1.HasEdgeToVertex(t3.key()) == False)
        check.ok_(t1.GetEdgeToVertex(t2.key()).myOtherVertex.key() == t2.key())
        check.ok_(t1.GetEdgeToVertex(t3.key()) == None)
        
        #make the other edges
        t1.AddEdge(t3, 12)
        t2.AddEdge(t3, 13)
        t2.AddEdge(t4, 14)
        t2.AddEdge(t6, 15)
        t3.AddEdge(t4, 16)
        
        #double add some edges to test all paths
        #shouldn't happen in the real app but we'll 
        #cover the path anyway...
        t1.AddEdge(t3, 12)
        t2.AddEdge(t3, 15)
        
        #check.ok_ the structure we've built
        check.ok_(len(t1.edges) == 2)
        check.ok_(len(t2.edges) == 3)
        check.ok_(len(t3.edges) == 1)
        check.ok_(len(t4.edges) == 0)
        check.ok_(len(t5.edges) == 0)
        check.ok_(len(t6.edges) == 0)

        edge = db.get(t1.edges[0])
        check.ok_(edge != None)
        check.ok_(edge.myOtherVertex.key() == t2.key())
        check.ok_(edge.edgeCount == 11)
        
        edge = db.get(t1.edges[1])
        check.ok_(edge != None)
        check.ok_(edge.myOtherVertex.key() == t3.key())
        check.ok_(edge.edgeCount == 12)
        
        edge = db.get(t2.edges[0])
        check.ok_(edge != None)
        check.ok_(edge.myOtherVertex.key() == t3.key())
        check.ok_(edge.edgeCount == 13)
        
        edge = db.get(t2.edges[1])
        check.ok_(edge != None)
        check.ok_(edge.myOtherVertex.key() == t4.key())
        check.ok_(edge.edgeCount == 14)
        
        edge = db.get(t2.edges[2])
        check.ok_(edge != None)
        check.ok_(edge.myOtherVertex.key() == t6.key())
        check.ok_(edge.edgeCount == 15)
        
        edge = db.get(t3.edges[0])
        check.ok_(edge != None)
        check.ok_(edge.myOtherVertex.key() == t4.key())
        check.ok_(edge.edgeCount == 16)
        
        #test negative query paths
        check.ok_(t5.HasEdgeToVertex(t1.key()) == False)
        check.ok_(t6.GetEdgeToVertex(t2.key()) == None)
    #end Test_DAGStructureFromGoogleClasses   

    '''
    { "28mm":62, "2mm":1, "6mm":29, "accessories":52, "acrylic":14, "actionscript":1, "activities":3 }
    '''
    def Test_LoadJSONTagList_ShortList(self):
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        db = TagDAGBuilderClass()
        dict = db.LoadJSONTagList(file.read())
        file.close()

        check.ok_(len(dict) == 7)
        check.ok_(dict["28mm"] == 62)
        check.ok_(dict["2mm"] == 1)
        check.ok_(dict["6mm"] == 29)
        check.ok_(dict["accessories"] == 52)
        check.ok_(dict["acrylic"] == 14)
        check.ok_(dict["actionscript"] == 1)
        check.ok_(dict["activities"] == 3)
    #end Test_LoadMasterTagList_ShortList
    
    def Test_AddMasterTagsToDataStore(self):
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag = TagDAGBuilderClass()
        dict = dag.StoreMasterTagList(file.read())
        file.close()

        check.ok_(dict.has_key("28mm") == True)
        check.ok_(dict.has_key("2mm") == True)
        check.ok_(dict.has_key("6mm") == True)
        check.ok_(dict.has_key("accessories") == True)
        check.ok_(dict.has_key("actionscript") == True)
        check.ok_(dict.has_key("activities") == True)
        check.ok_(dict.has_key("d'oh!") == False)

        testVertexKey = db.Key.from_path("TagVertex", "28mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "28mm")
        check.ok_(testVertex.ttlCount == 62)
        
        testVertexKey = db.Key.from_path("TagVertex", "2mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "2mm")
        check.ok_(testVertex.ttlCount == 1)
        
        testVertexKey = db.Key.from_path("TagVertex", "6mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "6mm")
        check.ok_(testVertex.ttlCount == 29)
        
        testVertexKey = db.Key.from_path("TagVertex", "accessories")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "accessories")
        check.ok_(testVertex.ttlCount == 52)
        
        testVertexKey = db.Key.from_path("TagVertex", "actionscript")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "actionscript")
        check.ok_(testVertex.ttlCount == 1)
        
        testVertexKey = db.Key.from_path("TagVertex", "activities")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "activities")
        check.ok_(testVertex.ttlCount == 3)
        
        testVertexKey = db.Key.from_path("TagVertex", "d'oh!")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex == None)
        
        # test that an empty tag string does not cause an exception
        dict = dag.StoreMasterTagList("")
        check.ok_(len(dict) == 0)
        s = None
        dict = dag.StoreMasterTagList(s)
        check.ok_(len(dict) == 0)
        
    #end Test_AddMasterTagsToDataStore


    '''
       Tags linked to "6mm": 
       { "28mm":11, "2mm":1,  "accessories":4,  "acrylic":5,  "activities":6 }

    '''
    def Test_AddEdgesToStoreForOneTag(self):
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag = TagDAGBuilderClass()
        dag.StoreMasterTagList(file.read())
        file.close()
  
        testVertexKey = db.Key.from_path("TagVertex", "6mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex != None)
        check.ok_(testVertex.key().name() == "6mm")
        
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dict = dag.AddEdgesForTag(testVertex, file.read())
        file.close()
        
        check.ok_(dict.has_key("28mm") == True)
        check.ok_(dict.has_key("2mm") == True)
        check.ok_(dict.has_key("accessories") == True)
        check.ok_(dict.has_key("acrylic") == True)
        check.ok_(dict.has_key("activities") == True)
        check.ok_(dict.has_key("6mm") == False)
        
        check.ok_(len(testVertex.edges) == 5)
        otherVertices = testVertex.GetAllConnectedVertices()
        check.ok_(len(otherVertices) == 5)
        
        tuple1 = ("28mm", 11)
        tuple2 = ("2mm", 1)
        tuple3 = ("accessories", 4)
        tuple4 = ("acrylic", 5)
        tuple5 = ("activities", 6)
        check.ok_(tuple1 in otherVertices)
        check.ok_(tuple2 in otherVertices)
        check.ok_(tuple3 in otherVertices)
        check.ok_(tuple4 in otherVertices)
        check.ok_(tuple5 in otherVertices)
        
        # test no exceptions from an empty json string
        dict = dag.AddEdgesForTag(testVertex, "")
        check.ok_(len(dict) == 0)
        
        #test no exceptions from a bad json string
        dict = dag.AddEdgesForTag(testVertex, " not A { JSON string {{{")
        check.ok_(len(dict) == 0)
        
    #end Test_AddEdgesToStoreForOneTag    
 

    '''
       Tags linked to "2mm": 
       { "28mm":4, "6mm":1, "activities":9 }
       
       Tags linked to "28mm": 
       { "2mm":4, "6mm":11 }
    '''
    def Test_AddEdgesToStoreForMultipleTags(self):
        
        dag = TagDAGBuilderClass()

        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(file.read())
        file.close()
  
        aVertexKey = db.Key.from_path("TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\2mmlinks_short.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\28mmlinks_short.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()

        #"28mm":62, "2mm":1, "6mm":29, "accessories":52, "acrylic":14, "actionscript":1, "activities":3

        k = db.Key.from_path("TagVertex", "28mm")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)

        k = db.Key.from_path("TagVertex", "2mm")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 2)
 
        k = db.Key.from_path("TagVertex", "6mm")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 5)
        
        k = db.Key.from_path("TagVertex", "accessories")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)
        k = db.Key.from_path("TagVertex", "acrylic")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)
        k = db.Key.from_path("TagVertex", "actionscript")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)
        k = db.Key.from_path("TagVertex", "activities")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)
    #end Test_AddEdgesToStoreForMultipleTags
        
    def Test_WriteOutDAG(self):
        
        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\2mmlinks_short.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\28mmlinks_short.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        dagAsJsonString = dag.DAGToJSONString_ArborFormat()
        
        file = open("c:\\temp\\smallTagDAG.json", "w")
        file.write(dagAsJsonString)
        file.close()
    #end Test_WriteOutDAG  
    
    def Test_MakeMediumDAG(self):

        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\mediumtaglist.json", "r")
        dag.StoreMasterTagList(file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\2mmLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\6mmlinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\28mmLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "accessories")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "accessories")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\accessoriesLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "acrylic")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "acrylic")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\acrylicLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "activities")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "activities")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\activitiesLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "booksearch")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "booksearch")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\booksearchLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "bookshop")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "bookshop")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\bookshopLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "brass")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "brass")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\brassLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "breakfast")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "breakfast")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\breakfastLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "browser")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "browser")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\browserLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "buildings")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "buildings")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\buildingsLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "campaigns")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "campaigns")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\campaignsLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "casting")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "casting")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\castingLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "CDs")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "CDs")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\CDsLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "charts")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "charts")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\chartsLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        aVertexKey = db.Key.from_path("TagVertex", "tools")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "tools")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\toolsLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "cabinets")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "cabinets")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\cabinetsLinks_medium.json", "r")
        dag.AddEdgesForTag(aVertex, file.read())
        file.close()
        
        dagAsJsonString = dag.DAGToJSONString_ArborFormat()
        
        file = open("c:\\temp\\mediumTagDAG.json", "w")
        file.write(dagAsJsonString)
        file.close()
        
    #end Test_MakeMediumDAG      

    def Test_EmptyJSONStrings(self):
        dag = TagDAGBuilderClass()
        # test passes if no exceptions thrown here        
        s = ""
        dict = dag.LoadJSONTagList(s)
    #endif    
    
    
#end testclass    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
