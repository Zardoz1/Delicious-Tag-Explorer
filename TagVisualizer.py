'''
Created on 01Mar2011
@author: tbelcher
'''

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

from gaesessions import get_current_session

from TagDAGBuilder import TagDAGBuilderClass
from TagSource import *

class TagVisualizerClass(webapp.RequestHandler):
    
    tdbc = TagDAGBuilderClass()
    tsc = TagSourceFactory().Factory()
    
    def GetCurrentUser(self):
        username = ""
        session = get_current_session()
        if session and session.has_key('name'):
            username = session['name']
        #endif
        return username    
    #end GetCurrentUser
      
    def post(self):
        
        try:        
            # get a list of all tags
            tagsetString = self.tsc.FetchMasterTagList("Zardoz59")
            tagsetDict = self.tdbc.StoreMasterTagList(tagsetString)
            
            jsonString = ""
            
            if tagsetDict.has_key("6mm") :
                testVertexKey = db.Key.from_path("TagVertex", "6mm")
                testVertex = db.get(testVertexKey)
                
                nodes = []
                node = {}
                node["id"] = testVertex.key().name()
                node["name"] = testVertex.key().name()
                    
                data = {}
                data["count"] = testVertex.ttlCount
                node["data"] = data
                    
                adjacencies = []
                for edgeKey in testVertex.edges:
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
                
                jsonString = json.dumps(nodes)
    
            #endif
            
            stuff = { 'tagDAGString': jsonString }
            dir = os.path.dirname(__file__)
            path = os.path.join(dir, 'templates', 'visualizer.html')
            self.response.out.write(template.render(path, stuff))
        except Exception, data:
            logging.error("TagVisualizerClass::post exception raised: " + str(data))
            self.error(404)
        #end try/catch
        
    #end post    

    '''
    ARBOR force-layout json format
    Required structure for our vertices and edges:
    { 
        "nodes": { 
                   "a": {}, "c": {} 
                 }, 
        "edges": { 
                   "a": { "b": {}, "e": {}, "f": {} }, 
                   "c": { "a": {} }, 
                   "b": { "a": {}, "j": {} }   
                 }, 
        "_": "test graph"
    }
    '''
        
    def DAGToJSONString_ArborFormat(self):
        
        allTags = self.tdbc.GetCompleteVertexSet()
        
        #the structure to write out
        nodes = {}
        for tag in allTags:
            attributes = {}
            attributes["count"] = tag.ttlCount
            nodes[tag.key().name()] = attributes 
        #end foreach    

        edges = {}
        for tag in allTags:
            otherVertices = {}
            for edgeKey in tag.edges:
                thisEdge = db.get(edgeKey)
                attributes = {}
                attributes["count"] = thisEdge.edgeCount
                otherVertices[thisEdge.myOtherVertex.key().name()] = attributes
            #end foreach
            edges[tag.key().name()] = otherVertices    
        #end foreach    

        jsonStructure = {}
        jsonStructure["nodes"] = nodes
        jsonStructure["edges"] = edges
        
        jsonString = json.dumps(jsonStructure)
        return jsonString
    #end DAGToJSONString_ArborFormat    
    
    
    '''
    GRAPH-VIZ force layout json structure    
    Required structure for our vertices and edges:
    var json = [  
                  {  
                     "id": "aUniqueIdentifier",  
                     "name": "usually a nodes name",  
                     "data": 
                     {  
                       "some key": "some value",  
                       "some other key": "some other value"  
                     },  
                     "adjacencies": 
                     [  
                         {  
                           nodeTo:"aNodeId",  
                           data: {} //put whatever you want here  
                         },  
                         'other adjacencies go here...'  
                     ]  
                  },
                                    
                  'other nodes go here...'
                ];  
    
    [
        {
            "id" : "WERTEX",
            "name" : "VERTEX",
            "data" : {
                        "count": COUNT // OURS
                        "$color": ??, // FORMATTING
                        "$type": ??,
                        "$dim": ??
                     },
            "adjacencies":
            [
                {
                    "nodeTo": OTHER_VERTEX,
                    "nodeFrom: "VERTEX",
                    "data":
                    {
                        "count": EDGE_COUNT,
                        "$color": ??
                    }
                }
            ]            
        }
    ]
    '''
    def DAGToJSONString_JitFormat(self, vertices):
        
        nodes = []
        for tag in vertices:
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
    #end DAGToJSONString_JitFormat
#end class TagVisualizer


class StartVisualizerClass(TagVisualizerClass):
    
    def get(self):

        startTagName = self.request.get("startTagName")
        username = self.GetCurrentUser()
        
        try:
            logging.info("Generating the start tag: " + startTagName + " for user: " + username)
            jsonString = self.getWorker(startTagName, username, self.tsc)
        
            stuff = { 'tagDAGString': jsonString }
            dir = os.path.dirname(__file__)
            path = os.path.join(dir, 'templates', 'visualizer.html')
            self.response.out.write(template.render(path, stuff))

        except Exception, data:
            logging.error("Failed generating start tag: " + startTagName + "; user:" + username)
            logging.error("StartVisualizerClass::get Exception raised: " + str(data))
            self.error(404)
        #end try/catch   
  
    #end get    
    
    def getWorker(self, startTagName, userName, tsc):
        if startTagName and len(startTagName) > 0 and len(userName) > 0:
            data = tsc.FetchLinkedTagList(userName, startTagName)
            self.tdbc.AddEdgesForTag(userName, startTagName, data)
            vertices = self.tdbc.GetDAGSubset(userName, startTagName, 2)
            if len(vertices) < 1:
                raise Exception("Internal error looking up adjacent tags of depth 1. Start tag = " + startTagName + ". User = " + userName)
            #endif
            jsonString = self.DAGToJSONString_JitFormat(vertices.values())
            return jsonString
        else:
            raise Exception("Bad or empty user session or starting tag.")
        #endif    
    #end getWorker    
    
#end class StartVisualizerClass


class BranchVisualizerClass(TagVisualizerClass):
    
    def get(self):

        parent = self.request.get("parent")
        username = self.GetCurrentUser()
        
        try:
            logging.info("Extending graph from start tag: " + parent + " for user: " + username)
            jsonString = self.getWorker(parent, username, self.tsc)                    
            stuff = { 'tagDAGString': jsonString }

            dir = os.path.dirname(__file__)
            path = os.path.join(dir, 'templates', 'visualizer.html')
            self.response.out.write(template.render(path, stuff))
        except Exception, data:
            logging.error("Failed extending graph for start tag: " + parent + " ")
            logging.error("BranchVisualizerClass::get Exception raised: " + str(data))
            self.error(404)
        #end try/catch   
  
    #end get    

    def getWorker(self, parentTagName, userName, tsc):
        if parentTagName and userName and len(parentTagName) > 0 and len(userName) > 0:
            data = tsc.FetchLinkedTagList(userName, parentTagName)
            self.tdbc.AddEdgesForTag(userName, parentTagName, data)
            vertices = self.tdbc.GetDAGSubset(userName, parentTagName, 1)
            if len(vertices) < 1:
                raise Exception("Internal error looking up adjacent tags of depth 1. Parent tag = " + parentTagName + ". User = " + userName)
            #endif
            jsonString = self.DAGToJSONString_JitFormat(vertices.values())
            return jsonString
    #end getWorker   
    
#end class BranchVisualuzerClass
#eof