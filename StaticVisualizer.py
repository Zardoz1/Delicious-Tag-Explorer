'''
Created on 07/04/2011
@author: tbelcher

For loading static json into the webbapage so we can experiment with layouts
'''

import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class StaticVisualizerClass(webapp.RequestHandler):
        
    def get(self):
        file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\shortTagDag\\shortTagDAGJitFormat.json", "r")
        #file = open("E:\\eclipse\\testworkspace\\zardoztestzone\\src\\DeliciousTagExplorer\\UnitTests\\mediumTagDag\\mediumTagDAGJitFormat.json", "r")

        result = file.read()
        file.close()
        stuff = { 'tagDAGString': result }
        
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, 'templates', 'visualizer.html')
        self.response.out.write(template.render(path, stuff))
    #end get
#end class StaticVisualizerClass
#eof        
        