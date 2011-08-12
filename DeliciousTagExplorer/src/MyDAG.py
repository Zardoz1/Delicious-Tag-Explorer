'''
Created on 17/02/2011
@author: tbelcher

Basic classes for representing a DAG in a Google datastore.
These classes don't know what they're storing - they just
represent nodes and edges.
'''

from google.appengine.ext import db
from MyMetaData import (MyUser)


class MyVertex(db.Model):
    #variables
        edges = db.ListProperty(db.Key)
        user = db.ReferenceProperty(MyUser)
    #methods
        def __init__(self, parent=None, key_name=None, **kwds):
            db.Model.__init__(self, parent, key_name, **kwds)
            self.user = (None if parent == None else parent) 
        #end init

        def GetEdgeToVertex(self, otherVertexKey):
            edge = self.GetEdgeWorker(otherVertexKey)
            if edge is None:
                raise Exception()
            #endif
            return edge    
        #end GetEdgeToVertex        
        
        def HasEdgeToVertex(self, otherVertexKey):
            if self.GetEdgeWorker(otherVertexKey) == None:
                return False
            else:
                return True
            #endif
        #end HasEdgeToVertex        
        
        def GetEdgeWorker(self, otherVertexKey):
            for edgeKey in self.edges:
                edge = db.get(edgeKey)
                if edge.myOtherVertex.key() == otherVertexKey:
                    return edge
                #endif    
            #endfor  
            return None
        #end EdgeToVertexWorker   
        
        def GetOwningUser(self):
            return self.parent()
        #end GetOwningUser    
            
#end class MyVertex

class MyEdge(db.Model):    
    #variables
        myOwningVertex = db.ReferenceProperty(MyVertex, None, "owner")
        myOtherVertex = db.ReferenceProperty(MyVertex, None, "connectee")
    #methods
        def __init__(self, parent=None, key_name=None, **kwds):
            db.Model.__init__(self, parent, key_name, **kwds)
        #end init    
#class MyEdge    

#eof