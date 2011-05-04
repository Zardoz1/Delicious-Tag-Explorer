'''
Created on 15/02/2011
@author: tbelcher
'''

import logging
import time
from google.appengine.ext import db
from django.utils import simplejson as json
from MyDAG import *


class TagEdge(MyEdge):
    #variables
        edgeCount = db.IntegerProperty()
    #methods
        def __init__(self, parent=None, key_name=None, **kwds):
            MyEdge.__init__(self,parent, key_name, **kwds)
        #end init    
#end class TagEdge


class TagVertex(MyVertex):
    #variables
        ttlCount = db.IntegerProperty()
    #methods
        def __init__(self, parent=None, key_name=None, **kwds):
            db.Model.__init__(self, parent, key_name, **kwds)
        #end init
        
        def AddEdge(self, otherVertex, count):
            #check first *we* don't already know this edge
            if self.HasEdgeToVertex(otherVertex.key()) == False:
                #AND ALSO if the other vertex already knows the edge to us then the
                #edge between the two vertices is recorded in the db
                #else neither they nor we know this edge yet so 
                #record it now as a link from us to the other 
                if otherVertex.HasEdgeToVertex(self.key())== False:
                    edge = TagEdge()
                    edge.myOwningVertex = self
                    edge.myOtherVertex = otherVertex
                    edge.edgeCount = count
                    edge.put()
                    self.edges.append(edge.key())
                #endif
            #endif
        #end AddEdge

        '''
        Return the set of all adjacent vertices recorded by us
        '''        
        def GetMyEdges(self):
            myEdges = {}
            for edgeKey in self.edges:
                thisEdge = db.get(edgeKey)
                myEdges[thisEdge.myOtherVertex.key().name()] = thisEdge
            #end for
            return myEdges
        #end GetEdges    

        def GetMyAdjacentVertices(self):
            otherVertices = {}
            for edgeKey in self.edges:
                thisEdge = db.get(edgeKey)
                otherVertices[thisEdge.myOtherVertex.key().name()] = thisEdge.myOtherVertex
            #end foreach
            
            return otherVertices
        #end GetMyAdjacentVertices   
        
        def GetAdjacentVerticesRecordedElsewhere(self):
            theirEdges = {}
            query = TagEdge.all()
            query.filter("myOtherVertex =", self)
            
            for edge in query:
                theirEdges[edge.myOwningVertex.key().name()] = edge.myOwningVertex
            #endfor    
            return theirEdges
        #end GetAdjacentVerticesRecordedElsewhere    
        
        '''
        Return the set of all adjacent vertices recorded by us
        PLUS all vertices that record us as being adjacent to them
        '''        
        def GetAllAdjacentVertices(self):
            
            # all vertices that WE record as being adjacent to us
            myAdjacentVertices = self.GetMyAdjacentVertices()

            # plus all vertices that record US as being adjacent to them
            otherAdjacentVertices = self.GetAdjacentVerticesRecordedElsewhere()
           
            return dict(myAdjacentVertices, **otherAdjacentVertices)
        #end GetAllAdjacentVertices
    
#end class TagVertex
    

class TagDAGBuilderClass(db.Model):
 
    def LoadJSONTagList(self, jsonString):
        dict = {}
        try:
            dict = json.loads(jsonString)
        except Exception:
            logging.error("Failed parsing JSON string; " + (jsonString if jsonString is not None else "NULL"))
        #end try/catch   
        return dict
    #end LoadJSONTagList
    
    def StoreMasterTagList(self, myUser, jsonString):
        dict = {}
        dict = self.LoadJSONTagList(jsonString)
        
        if len(dict) > 0:
            for tag, count in dict.iteritems():
                newVertex = TagVertex(myUser, tag)
                newVertex.ttlCount = count
                newVertex.put()
            #end for
        else:
            logging.error("Failed parsing master tag list string: " + (jsonString if jsonString is not None else "NULL"))
        #endif    
        return dict
    #end StoreMasterTagList
    
    def AddEdgesForVertex(self, parentVertex, jsonString):
        dict = {}
        dict = self.LoadJSONTagList(jsonString)

        if dict is not None and len(dict) > 0:        
            for linkedtag, linkedcount in dict.iteritems():
                otherVertexKey = None
                #make sure we're looking only at tags owned by the same person
                user = parentVertex.GetOwningUser()
                if user is not None:
                    #user must exist if we have a valid key
                    otherVertexKey = db.Key.from_path("MyUser", user.key().name(), "TagVertex", linkedtag)
                else:
                    otherVertexKey = db.Key.from_path("TagVertex", linkedtag)    
                #endif

                # tag must exist since we have loaded the master list
                otherVertex = db.get(otherVertexKey)
                if otherVertex != None:
                    parentVertex.AddEdge(otherVertex, linkedcount)
                else:
                    logging.info("This parent tag seems to have no vertex in the db: " 
                                 + linkedtag + "UserName: " 
                                 + (user.name()if user is not None else "None"))
                #endif    
            #end for  
        
            #update ourselves in the datastore
            parentVertex.put()
        else:
            logging.error("Bad or empty json string returned for edges to " + parentVertex.key().name())
        #endif
        
        return dict  
    #end AddEdgesForVertex
    
    def AddEdgesForTag(self, parentTagName, jsonString):
        parentVertex = self.GetVertex(parentTagName)
        if parentVertex is not None:    
            self.AddEdgesForVertex(parentVertex, jsonString)
        else:
            logging.error("No parent vertex to add edges to for tag " + parentTagName)
        #endif                
    #end AddEdgesForTag
    
    def GetCompleteVertexSet(self):
        allTags = []
        tagQuery = TagVertex.all()
        #this is the fetch that turns
        #the query into actual tags
        for tag in tagQuery:
            allTags.append(tag)
        #endfor    
        return allTags
    #end GetCompleteVertexSet 
    
    def GetCompleteVertexSetForNamedUser(self, userName):
        user = MyUser.get_by_key_name(userName)
        if user is not None:
            allTags = []
            q = TagVertex.all()
            q.ancestor(user.key())
            for tag in q:
                allTags.append(tag)
            #endfor
            return allTags    
        else:
            logging.error("Failed getting vertex set; unknown user '" + userName + "'.")
            return None
        #endif        
        
    #end GetCompleteVertexSetForNamedUser   
    
    def GetVertex(self, userName, tagName):
        if userName is not None:
            vertexKey = db.Key.from_path("MyUser", userName, "TagVertex", tagName)
        else:
            vertexKey = db.Key.from_path("TagVertex", tagName)
        #endif    
        return db.get(vertexKey)
    #end GetVertex     
    
    def GetEdge(self, edgeKey):
        return db.get(edgeKey)
    #end GetEdge     

    def GetDAGSubset(self, userName, startTagName, maxDepth):
        vertexDict = {}
        startVertex = self.GetVertex(userName, startTagName)
        self.VertexWalk(startVertex, vertexDict, 1, maxDepth)
        return vertexDict
    #end GetConnectedVertexSet
    
    def VertexWalk(self, parentVertex, vertexDict, currentDepth, maxDepth):
            
        vertexDict[parentVertex.key().name()] = parentVertex
        
        if maxDepth > 0 and currentDepth < maxDepth:
            adjacentVertices = parentVertex.GetAllAdjacentVertices()
            for adjacentVertexObject in adjacentVertices.values():
                self.VertexWalk(adjacentVertexObject, vertexDict, currentDepth + 1, maxDepth)
            #endfor
        #endif            

    '''
    This method build the complete tag graph, fetching all tags, then all links for
    each of those tags
    '''    
    def BuildCompleteTagDAG(self, userName, tagSource):
        # get a list of all tags
        tagsetString = tagSource.FetchMasterTagList(userName)
        tagsetDict = self.StoreMasterTagList(tagsetString)
        
        # for each tag get a list of connected tags
        if len(tagsetDict) > 0:
            for tag, count in tagsetDict.iteritems():
                print tag
                parentVertexKey = db.Key.from_path("MyUser", userName, "TagVertex", tag)
                parentVertex = db.get(parentVertexKey)
                if parentVertex != None:
                    linkedTagSetString = tagSource.FetchLinkedTagList(userName, tag)
                    if len(linkedTagSetString) > 1:
                        self.AddEdgesForVertex(parentVertex, linkedTagSetString)
                    else:
                        logging.info("Failed fetching lined tags for " + tag)    
                    #endif    
                else:
                    logging.info("No parent vertex to fetch linked tags for parent tag " + tag)
                #endif
            #end foreach
        else:
                logging.info("Failed fetching master tag list for userName " + userName)
        #endif                
    #end BuildTagDAG
    
    def DumpDAGToJsonString(self):
        allTags = self.GetCompleteVertexSet()
        nodes = []
        for tag in allTags:
            node = {}
            node["id"] = tag.key().name()
            node["name"] = tag.key().name()
            
            data = {}
            data["count"] = tag.ttlCount
            node["data"] = data
            
            adjacencies = []
            for edgeKey in tag.edges:
                thisEdge = db.get(edgeKey)
                adjacency = {}
                data = {}
                adjacency["nodeTo"] = thisEdge.myOtherVertex.key().name()
                data["count"] = thisEdge.edgeCount
                adjacency["data"] = data
                
                adjacencies.append(adjacency)
            #end for (edges) 
            node["adjacencies"] = adjacencies   
            nodes.append(node)
        #end for (nodes)   
        
        jsonString = json.dumps(nodes)
        return jsonString
    #end DumpDAGToJson      
                
    #end class TagDAGBuilderClass
#eof            