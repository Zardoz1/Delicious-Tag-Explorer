'''
Created on 15/02/2011

@author: tbelcher
'''

import unittest
import nose.tools as check
from google.appengine.ext import db
from TagDAGBuilder import (TagDAGBuilderClass, TagVertex, TagEdge)
from MyMetaData import MyUser


class Test(unittest.TestCase):


    def setUp(self):

        #check that the db contents really have been deleted
        tagQuery = TagVertex.all()
        tags = tagQuery.fetch(100)
        check.ok_(len(tags) == 0)
        edgeQuery = TagEdge.all()
        edges = edgeQuery.fetch(100)
        check.ok_(len(edges) == 0)
        userQuery = MyUser.all()
        users = userQuery.fetch(100)
        check.ok_(len(users) == 0)
    #end setUp

    def tearDown(self):
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
        check.ok_(edge.myOwningVertex != None)
        check.ok_(edge.myOwningVertex.key() == t1.key())
        
        v = edge.myOtherVertex
        check.ok_(v != None)
        check.ok_(v.key() == t2.key())
        check.ok_(v.ttlCount == 2)
        check.ok_(t1.HasEdgeToVertex(t2.key()) == True)
        check.ok_(t1.HasEdgeToVertex(t3.key()) == False)
        check.ok_(t1.GetEdgeToVertex(t2.key()).myOtherVertex.key() == t2.key())
        
        # check that trying to get a non-existent edge chucks
        try:
            t1.GetEdgeToVertex(t3.key())
        except Exception:   
            pass
        except:
            check.ok_(0==1, "Wrong type of exception thrown.")
        else:
            check.ok_(0==1, "Expected exception upchuck; none occurred.")
        #end try/catch            

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
        check.ok_(edge.myOwningVertex.key() == t1.key())
        check.ok_(edge.myOtherVertex.key() == t2.key())
        check.ok_(edge.edgeCount == 11)

        edge = db.get(t1.edges[1])
        check.ok_(edge != None)
        check.ok_(edge.myOwningVertex.key() == t1.key())
        check.ok_(edge.myOtherVertex.key() == t3.key())
        check.ok_(edge.edgeCount == 12)

        edge = db.get(t2.edges[0])
        check.ok_(edge != None)
        check.ok_(edge.myOwningVertex.key() == t2.key())
        check.ok_(edge.myOtherVertex.key() == t3.key())
        check.ok_(edge.edgeCount == 13)

        edge = db.get(t2.edges[1])
        check.ok_(edge != None)
        check.ok_(edge.myOwningVertex.key() == t2.key())
        check.ok_(edge.myOtherVertex.key() == t4.key())
        check.ok_(edge.edgeCount == 14)

        edge = db.get(t2.edges[2])
        check.ok_(edge != None)
        check.ok_(edge.myOwningVertex.key() == t2.key())
        check.ok_(edge.myOtherVertex.key() == t6.key())
        check.ok_(edge.edgeCount == 15)

        edge = db.get(t3.edges[0])
        check.ok_(edge != None)
        check.ok_(edge.myOwningVertex.key() == t3.key())
        check.ok_(edge.myOtherVertex.key() == t4.key())
        check.ok_(edge.edgeCount == 16)

        #test negative query paths
        check.ok_(t5.HasEdgeToVertex(t1.key()) == False)
        
        try:
            t6.GetEdgeToVertex(t2.key())
        except Exception:   
            pass
        except:
            check.ok_(0==1, "Wrong type of exception thrown.")
        else:
            check.ok_(0==1, "Expected exception upchuck; none occurred.")
        #end try/catch            
    #end Test_DAGStructureFromGoogleClasses


    def Test_DAGStructureMultipleUsers(self):
        
        #tags for the first user...
        u1 = MyUser(user="Bill", key_name="Bill")
        u1.put()
        u2 = MyUser(user="Ted", key_name="Ted")
        u2.put()
        
        # Bill's tags
        t1 = TagVertex(parent = u1, key_name="Tag1")
        t1.ttlCount = 1
        t1.put()
        t2 = TagVertex(parent = u1, key_name="Tag2")
        t2.ttlCount = 2
        t2.put()
        t3 = TagVertex(parent = u1, key_name="Tag3")
        t3.ttlCount = 3
        t3.put()
        t4 = TagVertex(parent = u1, key_name="Tag4")
        t4.ttlCount = 4
        t4.put()
        t5 = TagVertex(parent = u1, key_name="Tag5")
        t5.ttlCount = 5
        t5.put()
        
        # Ted's tags
        tt1 = TagVertex(parent = u2, key_name="Tag1")
        tt1.ttlCount = 11
        tt1.put()
        tt2 = TagVertex(parent = u2, key_name="Tag2")
        tt2.ttlCount = 12
        tt2.put()
        tt3 = TagVertex(parent = u2, key_name="Tag3")
        tt3.ttlCount = 13
        tt3.put()
        tt4 = TagVertex(parent = u2, key_name="Tag4")
        tt4.ttlCount = 14
        tt4.put()
        tt5 = TagVertex(parent = u2, key_name="Tag5")
        tt5.ttlCount = 15
        tt5.put()
        
        #extract Bill's tags
        q1 = TagVertex.all()
        q1.ancestor(u1.key())
        results = q1.fetch(10)
        check.ok_(len(results) == 5)
        for v in results:
            check.ok_(v.ttlCount > 0 and v.ttlCount < 11)
        #endfor
        
        q2 = TagVertex.all()
        q2.ancestor(u2.key())
        results = q2.fetch(10)
        check.ok_(len(results) == 5)
        for v in results:
            check.ok_(v.ttlCount > 10 and v.ttlCount < 16)
        #endfor    
        
    #end Test_DAGStructureMultipleUsers   

    '''
        Tag1 <-> Tag2  count: 11
        Tag1 <-> Tag3         12
        Tag2 <-> Tag3         13
        Tag2 <-> Tag4         14
        Tag2 <-> Tag6         15
        Tag3 <-> Tag4         16
        Tag5 <-> nothing       0 natch
    '''
    def Test_DAGStructure_VertexEdgeSetQueries(self):

        #multiple users so we can test this feature
        u1 = MyUser(user="Bill", key_name="Bill")
        u1.put()
        u2 = MyUser(user="Ted", key_name="Ted")
        u2.put()

        #first insert all known tags
        t1 = TagVertex(u1, "Tag1")
        t1.ttlCount = 1
        t1.put()
        t2 = TagVertex(u1, "Tag2")
        t2.ttlCount = 2
        t2.put()
        t3 = TagVertex(u1, "Tag3")
        t3.ttlCount = 3
        t3.put()
        t4 = TagVertex(u1, "Tag4")
        t4.ttlCount = 4
        t4.put()
        t5 = TagVertex(u1, "Tag5")
        t5.ttlCount = 5
        t5.put()
        t6 = TagVertex(u1, "Tag6")
        t6.ttlCount = 6
        t6.put()
        t1.AddEdge(t2, 11)
        t1.AddEdge(t3, 12)
        t2.AddEdge(t3, 13)
        t2.AddEdge(t4, 14)
        t2.AddEdge(t6, 15)
        t3.AddEdge(t4, 16)
        
        #some duplicate tags for the second user
        #(just noise - the calls here work from vertex references
        #and so should never see these 'other' tags
        t22 = TagVertex(u2, "Tag2")
        t22.ttlCount = 22
        t22.put()
        t33 = TagVertex(u2, "Tag3")
        t33.ttlCount = 33
        t33.put()
        t44 = TagVertex(u2, "Tag4")
        t44.ttlCount = 44
        t44.put()
        t22.AddEdge(t33, 13)
        t22.AddEdge(t44, 14)
        t33.AddEdge(t44, 16)

        # test getting the set of outgoing edges
        myEdges = t2.GetMyEdges()
        check.ok_(myEdges != None)
        check.ok_(len(myEdges) == 3)
        check.ok_(myEdges.has_key("Tag3"))
        check.ok_(myEdges.has_key("Tag4"))
        check.ok_(myEdges.has_key("Tag6"))
        check.ok_(myEdges["Tag3"].edgeCount == 13)
        check.ok_(myEdges["Tag4"].edgeCount == 14)
        check.ok_(myEdges["Tag6"].edgeCount == 15)
        
        #get the set of connected vertices recorded in a vertex
        myConectees = t3.GetMyAdjacentVertices()
        check.ok_(myConectees != None)
        check.ok_(len(myConectees) == 1)
        check.ok_(myConectees.has_key("Tag4"))
        
        #test getting the set of incoming edges
        otherConectees = t3.GetAdjacentVerticesRecordedElsewhere()
        check.ok_(otherConectees != None)
        check.ok_(len(otherConectees) == 2)
        check.ok_(otherConectees.has_key("Tag1"))
        check.ok_(otherConectees.has_key("Tag2"))

        #get the total set of connected vertices
        connectees = t3.GetAllAdjacentVertices()
        check.ok_(connectees != None)
        check.ok_(len(connectees) == 3)
        check.ok_(connectees.has_key("Tag1"))
        check.ok_(connectees.has_key("Tag2"))
        check.ok_(connectees.has_key("Tag4"))
        
    #end Test_DAGStructure_VertexEdgeSetQueries   

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

        u1 = MyUser(None, "Bill")
        u1.put()
        u2 = MyUser(None, "Ted")
        u2.put()

        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag = TagDAGBuilderClass()
        dict = dag.StoreMasterTagList(u1, file.read())
        file.close()
        
        # add an extra vertex to represent the second user's data
        tv = TagVertex(u2, "wild thing")
        tv.put()

        # check that the returned dictionary is complete
        check.ok_(dict.has_key("28mm") == True)
        check.ok_(dict.has_key("2mm") == True)
        check.ok_(dict.has_key("6mm") == True)
        check.ok_(dict.has_key("accessories") == True)
        check.ok_(dict.has_key("actionscript") == True)
        check.ok_(dict.has_key("activities") == True)
        check.ok_(dict.has_key("d'oh!") == False)
        check.ok_(dict.has_key("wild thing") == False)
        
        #check that the complete set of vertices is correct
        dict2 = {}
        alist = dag.GetCompleteVertexSet()
        for tag in alist:
            dict2[tag.key().name()] = tag.ttlCount
        #endfor    
        check.ok_(dict2.has_key("28mm") == True)
        check.ok_(dict2.has_key("2mm") == True)
        check.ok_(dict2.has_key("6mm") == True)
        check.ok_(dict2.has_key("accessories") == True)
        check.ok_(dict2.has_key("actionscript") == True)
        check.ok_(dict2.has_key("activities") == True)
        check.ok_(dict2.has_key("d'oh!") == False)
        check.ok_(dict2.has_key("wild thing") == True)
        
        #check we can get a set of vertices for each user
        dict3 = {}
        alist = dag.GetCompleteVertexSetForNamedUser("Bill")
        for tag in alist:
            dict3[tag.key().name()] = tag.ttlCount
        #endfor    
        check.ok_(dict3.has_key("28mm") == True)
        check.ok_(dict3.has_key("2mm") == True)
        check.ok_(dict3.has_key("6mm") == True)
        check.ok_(dict3.has_key("accessories") == True)
        check.ok_(dict3.has_key("actionscript") == True)
        check.ok_(dict3.has_key("activities") == True)
        check.ok_(dict3.has_key("d'oh!") == False)
        check.ok_(dict3.has_key("wild thing") == False)

        dict4 = {}
        alist = dag.GetCompleteVertexSetForNamedUser("Ted")
        for tag in alist:
            dict4[tag.key().name()] = tag.ttlCount
        #endfor    
        check.ok_(dict4.has_key("28mm") == False)
        check.ok_(dict4.has_key("2mm") == False)
        check.ok_(dict4.has_key("6mm") == False)
        check.ok_(dict4.has_key("accessories") == False)
        check.ok_(dict4.has_key("actionscript") == False)
        check.ok_(dict4.has_key("activities") == False)
        check.ok_(dict4.has_key("d'oh!") == False)
        check.ok_(dict4.has_key("wild thing") == True)

        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "28mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "28mm")
        check.ok_(testVertex.ttlCount == 62)
        check.ok_(testVertex.parent().key() == u1.key())

        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "2mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "2mm")
        check.ok_(testVertex.ttlCount == 1)

        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "6mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "6mm")
        check.ok_(testVertex.ttlCount == 29)

        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "accessories")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "accessories")
        check.ok_(testVertex.ttlCount == 52)

        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "actionscript")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "actionscript")
        check.ok_(testVertex.ttlCount == 1)

        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "activities")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex.key().name() == "activities")
        check.ok_(testVertex.ttlCount == 3)

        #try to get an existing tag with the wrong user
        testVertexKey = db.Key.from_path("MyUser", "Ted", "TagVertex", "activities")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex == None)

        #try to get a tag that does not exist
        testVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "d'oh!")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex == None)

        # test that an empty tag string does not cause an exception
        dict = dag.StoreMasterTagList(u2, "")
        check.ok_(len(dict) == 0)
        s = None
        dict = dag.StoreMasterTagList(u2, s)
        check.ok_(len(dict) == 0)

    #end Test_AddMasterTagsToDataStore


    '''
       Tags linked to "6mm":
       { "28mm":11, "2mm":1,  "accessories":4,  "acrylic":5,  "activities":6 }

    '''
    def Test_AddEdgesToStoreForOneTag(self):

        u1 = MyUser(None, "Bill")
        u1.put()
        u2 = MyUser(None, "Ted")
        u2.put()

        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag = TagDAGBuilderClass()
        dag.StoreMasterTagList(u2, file.read())
        file.close()

        testVertexKey = db.Key.from_path("MyUser", "Ted", "TagVertex", "6mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex != None)
        check.ok_(testVertex.key().name() == "6mm")

        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dict = dag.AddEdgesForVertex(testVertex, file.read())
        file.close()

        check.ok_(dict.has_key("28mm") == True)
        check.ok_(dict.has_key("2mm") == True)
        check.ok_(dict.has_key("accessories") == True)
        check.ok_(dict.has_key("acrylic") == True)
        check.ok_(dict.has_key("activities") == True)
        check.ok_(dict.has_key("6mm") == False)

        check.ok_(len(testVertex.edges) == 5)
        otherVertices = testVertex.GetMyAdjacentVertices()
        check.ok_(len(otherVertices) == 5)
        check.ok_(otherVertices.has_key("28mm"))
        check.ok_(otherVertices.has_key("2mm"))
        check.ok_(otherVertices.has_key("accessories"))
        check.ok_(otherVertices.has_key("acrylic"))
        check.ok_(otherVertices.has_key("activities"))

        myEdges = testVertex.GetMyEdges()
        check.ok_(myEdges["28mm"].edgeCount == 11)
        check.ok_(myEdges["2mm"].edgeCount == 1)
        check.ok_(myEdges["accessories"].edgeCount == 4)
        check.ok_(myEdges["acrylic"].edgeCount == 5)
        check.ok_(myEdges["activities"].edgeCount == 6)

        otherVertex = dag.GetVertex(u2.key().name(), "28mm")
        myEdges = otherVertex.GetMyEdges()
        check.ok_(len(myEdges) == 0)
        check.ok_(otherVertex.key().name() == "28mm")
        theirEdges = otherVertex.GetAdjacentVerticesRecordedElsewhere()
        check.ok_(len(theirEdges) == 1)
        check.ok_(theirEdges.has_key("6mm"))

        # test no exceptions from an empty json string
        dict = dag.AddEdgesForVertex(testVertex, "")
        check.ok_(len(dict) == 0)

        #test no exceptions from a bad json string
        dict = dag.AddEdgesForVertex(testVertex, " not A { JSON string {{{")
        check.ok_(len(dict) == 0)

    #end Test_AddEdgesToStoreForOneTag


    def Test_EdgeAndVertexAccessors(self):

        u1 = MyUser(None, "Bill")
        u1.put()

        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag = TagDAGBuilderClass()
        dag.StoreMasterTagList(u1, file.read())
        file.close()

        testVertexKey = db.Key.from_path("MyUser", u1.key().name(), "TagVertex", "6mm")
        testVertex = db.get(testVertexKey)
        check.ok_(testVertex != None)
        check.ok_(testVertex.key().name() == "6mm")

        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dict = dag.AddEdgesForVertex(testVertex, file.read())
        file.close()

        testVertex = dag.GetVertex(u1.key().name(), "acrylic")
        check.ok_(testVertex != None)
        check.ok_(testVertex.key().name() == "acrylic")
        check.ok_(testVertex.ttlCount == 14)

        testVertex = dag.GetVertex("Bill", "6mm")
        check.ok_(testVertex != None)
        check.ok_(testVertex.key().name() == "6mm")
        check.ok_(testVertex.ttlCount == 29)

    #end Test_EdgeAndVertexAccessors

    '''
       Tags linked to "2mm":
       { "28mm":4, "6mm":1, "activities":9 }

       Tags linked to "28mm":
       { "2mm":4, "6mm":11 }
    '''
    def Test_AddEdgesToStoreForMultipleTags(self):

        u1 = MyUser(None, "Bill")
        u1.put()
        u2 = MyUser(None, "Ted")
        u2.put()

        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(u2, file.read())
        file.close()

        aVertexKey = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\2mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\28mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        #"28mm":62, "2mm":1, "6mm":29, "accessories":52, "acrylic":14, "actionscript":1, "activities":3

        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "28mm")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)

        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "2mm")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 2)

        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "6mm")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 5)

        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "accessories")
        testVertex = db.get(k)
        
        check.ok_(len(testVertex.edges) == 0)
        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "acrylic")
        testVertex = db.get(k)
        
        check.ok_(len(testVertex.edges) == 0)
        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "actionscript")
        testVertex = db.get(k)
        
        check.ok_(len(testVertex.edges) == 0)
        k = db.Key.from_path("MyUser", u2.key().name(), "TagVertex", "activities")
        testVertex = db.get(k)
        check.ok_(len(testVertex.edges) == 0)
        
    #end Test_AddEdgesToStoreForMultipleTags


    def Test_WriteOutDAG(self):

        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(None, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\2mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\28mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        dagAsJsonString = dag.DumpDAGToJsonString()
        file = open("c:\\temp\\smallTagDAG.json", "w")
        file.write(dagAsJsonString)
        file.close()
    #end Test_WriteOutDAG

    def Test_MakeMediumDAG(self):

        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\mediumtaglist.json", "r")
        dag.StoreMasterTagList(None, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\2mmLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\6mmlinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\28mmLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "accessories")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "accessories")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\accessoriesLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "acrylic")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "acrylic")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\acrylicLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "activities")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "activities")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\activitiesLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "booksearch")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "booksearch")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\booksearchLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "bookshop")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "bookshop")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\bookshopLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "brass")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "brass")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\brassLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "breakfast")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "breakfast")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\breakfastLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "browser")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "browser")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\browserLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "buildings")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "buildings")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\buildingsLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "campaigns")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "campaigns")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\campaignsLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "casting")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "casting")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\castingLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "CDs")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "CDs")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\CDsLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "charts")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "charts")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\chartsLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "tools")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "tools")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\toolsLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        aVertexKey = db.Key.from_path("TagVertex", "cabinets")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "cabinets")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\cabinetsLinks_medium.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        dagAsJsonString = dag.DumpDAGToJsonString()
        file = open("c:\\temp\\mediumTagDAG.json", "w")
        file.write(dagAsJsonString)
        file.close()

    #end Test_MakeMediumDAG


    def Test_GetAdjacentVertices_SmallDag(self):

        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(None, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\2mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\28mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "acrylic")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "acrylic")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\acryliclinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "activities")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "activities")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\activitieslinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("TagVertex", "accessories")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "accessories")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\accessorieslinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        #actionscript has no links

        # walk to depth 1 - should just get the parent tag
        vertexDict = dag.GetDAGSubset(None, "6mm", 1)
        check.ok_(len(vertexDict) == 1)
        check.ok_(vertexDict.has_key("6mm") == True)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == False)
        check.ok_(vertexDict.has_key("activities") == False)
        check.ok_(vertexDict.has_key("acrylic") == False)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == False)

        vertexDict = dag.GetDAGSubset(None, "acrylic", 1)
        check.ok_(len(vertexDict) == 1)
        check.ok_(vertexDict.has_key("6mm") == False)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == False)
        check.ok_(vertexDict.has_key("activities") == False)
        check.ok_(vertexDict.has_key("acrylic") == True)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == False)

        vertexDict = dag.GetDAGSubset(None, "actionscript", 1)
        check.ok_(len(vertexDict) == 1)
        check.ok_(vertexDict.has_key("6mm") == False)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == False)
        check.ok_(vertexDict.has_key("activities") == False)
        check.ok_(vertexDict.has_key("acrylic") == False)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == True)

        # walk to depth 2 - should get 6 tags
        vertexDict = dag.GetDAGSubset(None, "6mm", 2)
        check.ok_(len(vertexDict) == 6)
        check.ok_(vertexDict.has_key("6mm") == True)
        check.ok_(vertexDict.has_key("28mm") == True)
        check.ok_(vertexDict.has_key("2mm") == True)
        check.ok_(vertexDict.has_key("activities") == True)
        check.ok_(vertexDict.has_key("acrylic") == True)
        check.ok_(vertexDict.has_key("accessories") == True)
        check.ok_(vertexDict.has_key("actionscript") == False)

        # walk to depth 2 - should get 3 tags
        vertexDict = dag.GetDAGSubset(None, "activities", 2)
        check.ok_(len(vertexDict) == 3)
        check.ok_(vertexDict.has_key("6mm") == True)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == True)
        check.ok_(vertexDict.has_key("activities") == True)
        check.ok_(vertexDict.has_key("acrylic") == False)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == False)

    #end Test_GetAdjacentVertices_SmallDag

    def Test_GetAdjacentVertices_SmallDag_MultipleUsers(self):

        u1 = MyUser(None, "Bill")
        u1.put()
        u2 = MyUser(None, "Ted")
        u2.put()

        dag = TagDAGBuilderClass()
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(u1, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "2mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "2mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\2mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "28mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "28mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\28mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "acrylic")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "acrylic")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\acryliclinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "activities")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "activities")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\activitieslinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Bill", "TagVertex", "accessories")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "accessories")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\accessorieslinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        #add *some* of the same tags and edges for the second user
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shorttaglist.json", "r")
        dag.StoreMasterTagList(u2, file.read())
        file.close()
        aVertexKey = db.Key.from_path("MyUser", "Ted", "TagVertex", "6mm")
        aVertex = db.get(aVertexKey)
        check.ok_(aVertex.key().name() == "6mm")
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\6mmlinks_short.json", "r")
        dag.AddEdgesForVertex(aVertex, file.read())
        file.close()

        #actionscript has no links

        # walk to depth 1 - should just get the parent tag
        vertexDict = dag.GetDAGSubset("Bill", "6mm", 1)
        check.ok_(len(vertexDict) == 1)
        check.ok_(vertexDict.has_key("6mm") == True)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == False)
        check.ok_(vertexDict.has_key("activities") == False)
        check.ok_(vertexDict.has_key("acrylic") == False)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == False)

        vertexDict = dag.GetDAGSubset("Bill", "acrylic", 1)
        check.ok_(len(vertexDict) == 1)
        check.ok_(vertexDict.has_key("6mm") == False)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == False)
        check.ok_(vertexDict.has_key("activities") == False)
        check.ok_(vertexDict.has_key("acrylic") == True)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == False)

        vertexDict = dag.GetDAGSubset("Bill", "actionscript", 1)
        check.ok_(len(vertexDict) == 1)
        check.ok_(vertexDict.has_key("6mm") == False)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == False)
        check.ok_(vertexDict.has_key("activities") == False)
        check.ok_(vertexDict.has_key("acrylic") == False)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == True)

        # walk to depth 2 - should get 6 tags
        vertexDict = dag.GetDAGSubset("Bill", "6mm", 2)
        check.ok_(len(vertexDict) == 6)
        check.ok_(vertexDict.has_key("6mm") == True)
        check.ok_(vertexDict.has_key("28mm") == True)
        check.ok_(vertexDict.has_key("2mm") == True)
        check.ok_(vertexDict.has_key("activities") == True)
        check.ok_(vertexDict.has_key("acrylic") == True)
        check.ok_(vertexDict.has_key("accessories") == True)
        check.ok_(vertexDict.has_key("actionscript") == False)

        # walk to depth 2 - should get 3 tags
        vertexDict = dag.GetDAGSubset("Bill", "activities", 2)
        check.ok_(len(vertexDict) == 3)
        check.ok_(vertexDict.has_key("6mm") == True)
        check.ok_(vertexDict.has_key("28mm") == False)
        check.ok_(vertexDict.has_key("2mm") == True)
        check.ok_(vertexDict.has_key("activities") == True)
        check.ok_(vertexDict.has_key("acrylic") == False)
        check.ok_(vertexDict.has_key("accessories") == False)
        check.ok_(vertexDict.has_key("actionscript") == False)

    #end Test_GetAdjacentVertices_SmallDag_MultipleUsers

    
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

