'''
Created on 01Mar2011
@author: tbelcher
'''


import os
import logging
import urllib2
import time

from google.appengine.api.urlfetch_errors import *
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

from TagDAGBuilder import TagDAGBuilderClass

class NetworkTagSourceClass:

    baseurl = "http://feeds.delicious.com/v2/json/tags/"

    def FetchMasterTagList(self, user):
        url = self.baseurl + urllib2.quote(user)
        logging.info(" > Fetching: " + url)
        result = urllib2.urlopen(url)
        return result.read()
    #end FetchMasterTagList
    
    def FetchLinkedTagList(self, user, tag):
        time.sleep(0.25)
        url = self.baseurl + urllib2.quote(user) + "/" + urllib2.quote(tag, "")
        logging.info(" > Fetching: " + url)
        
        while True:
            count = 0
            try:
                result = urllib2.urlopen(url)
                return result.read()
            except (DownloadError, urllib2.HTTPError), e:
                msg = "Failed Delicious Fetch Request. " + e.__str__() 
                logging.error(msg)
                time.sleep(5)
                count = count + 1
                if count > 5:
                    return ""
                #endif
            #end try/catch                    
        #end while    
    #end FetchLinkedTagList

#end NetworkTagSourceClass


class TagVisualizerClass(webapp.RequestHandler):
    
    tdbc = TagDAGBuilderClass()
    tsc = NetworkTagSourceClass()
      
    def post(self):
        
        try:        
            # get a list of all tags
            tagsetString = self.tsc.FetchMasterTagList("Zardoz59")
            tagsetDict = self.tdbc.StoreMasterTagList(tagsetString)
            
            jsonstring = ""
            
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


class BranchVisualizerClass(TagVisualizerClass):
    
    def get(self):

        parent = self.request.get("parent")
        
        try:
            if parent and len(parent) > 0:
                
                logging.info("Extending graph from start tag: " + parent)

                data = self.tsc.FetchLinkedTagList("Zardoz59", parent)
                self.tdbc.AddEdgesForTag(parent, data)
    
                vertices = self.tdbc.GetDAGSubset("6mm", 0)
                jsonString = self.DAGToJSONString_JitFormat(vertices.values())
                
                stuff = { 'tagDAGString': jsonString }
                dir = os.path.dirname(__file__)
                path = os.path.join(dir, 'templates', 'visualizer.html')
                self.response.out.write(template.render(path, stuff))
            #endif
        except Exception, data:
            logging.error("Failed extending graph for start tag: " + parent + " ")
            logging.error("BranchVisualizerClass::get Exception raised: " + str(data))
            self.error(404)
        #end try/catch   
  
    #end get    
    
#end class BranchVisualuzerClass
#eof