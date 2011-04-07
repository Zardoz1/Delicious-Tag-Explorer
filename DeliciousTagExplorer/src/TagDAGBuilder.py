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
                #else neither they nor we 't know this edge yet so 
                #record it now as a link from us to the other 
                if otherVertex.HasEdgeToVertex(self.key())== False:
                    edge = TagEdge()
                    edge.myOtherVertex = otherVertex
                    edge.edgeCount = count
                    edge.put()
                    self.edges.append(edge.key())
                #endif
            #endif
        #end AddEdge
        
        def GetAllConnectedVertices(self):
            otherVertices = []
            for edgeKey in self.edges:
                thisEdge = db.get(edgeKey)
                t = (thisEdge.myOtherVertex.key().name(), thisEdge.edgeCount)
                otherVertices.append(t) 
            #end foreach
            
            return otherVertices
        #end GetAllConnectedVertices        
    
#end class TagVertex
    

class TagDAGBuilderClass(db.Model):
 
    def LoadJSONTagList(self, jsonString):
        dict = {}
        try:
            dict = json.loads(jsonString)
        except Exception:
            # a if b else c
            logging.error("Failed parsing JSON string; " + (jsonString if jsonString is not None else "NULL"))
        #end try/catch   
        return dict
    #end LoadJSONTagList   
    
    def StoreMasterTagList(self, jsonString):
        dict = {}
        dict = self.LoadJSONTagList(jsonString)
        
        if len(dict) > 0:
            for tag, count in dict.iteritems():
                newVertex = TagVertex(None, tag)
                newVertex.ttlCount = count
                newVertex.put()
            #end for
        else:
            logging.error("Failed parsing master tag list string: " + (jsonString if jsonString is not None else "NULL"))
        #endif    
        return dict
    #end StoreMasterTagList
    
    def AddEdgesForTag(self, parentVertex, jsonString):
        dict = {}
        dict = self.LoadJSONTagList(jsonString)

        if dict is not None and len(dict) > 0:        
            for linkedtag, linkedcount in dict.iteritems():
                # tag must exist since we have loaded the master list
                otherVertexKey = db.Key.from_path("TagVertex", linkedtag)
                otherVertex = db.get(otherVertexKey)
                if otherVertex != None:
                    parentVertex.AddEdge(otherVertex, linkedcount)
                else:
                    logging.info("This parent tag seems to have no vertex in the db: " + linkedtag)
                #endif    
            #end for  
        
            #update ourselves in the datastore
            parentVertex.put()
        else:
            logging.error("Bad or empty json string returned for edges to " + parentVertex.key().name())
        #endif        
        
        return dict  
    #end AddEdgesForTag
    
    def BuildTagDAG(self, user, tagSource):
        # get a list of all tags
        tagsetString = tagSource.FetchMasterTagList(user)
        tagsetDict = self.StoreMasterTagList(tagsetString)
        
        # for each tag get a list of connected tags
        if len(tagsetDict) > 0:
            for tag, count in tagsetDict.iteritems():
                print tag
                parentVertexKey = db.Key.from_path("TagVertex", tag)
                parentVertex = db.get(parentVertexKey)
                if parentVertex != None:
                    linkedTagSetString = tagSource.FetchLinkedTagList(user, tag)
                    if len(linkedTagSetString) > 1:
                        self.AddEdgesForTag(parentVertex, linkedTagSetString)
                    else:
                        logging.info("Failed fetching lined tags for " + tag)    
                    #endif    
                else:
                    logging.info("No parent vertex to fetch linked tags for parent tag " + tag)
                #endif
                #end foreach
        else:
                logging.info("Failed fetching master tag list for user " + user)
        #endif                
    #end BuildTagDAG
        
    def GetTagSet(self):
        return TagVertex.all()
    #end GetTagSet        

    #end class TagDAGBuilderClass
#eof            