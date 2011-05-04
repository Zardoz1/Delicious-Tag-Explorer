import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '0.96' )

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

#from TagVisualizer import TagVisualizerClass
from TagVisualizer import BranchVisualizerClass
from StaticVisualizer import StaticVisualizerClass
from StartTagSelector import StartTagSelectorClass

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = { }
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, 'templates', 'Start.html')
        self.response.out.write(template.render(path, template_values))
    #end
# end


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/startTagSelector', StartTagSelectorClass),
                                      ('/tags/branch', BranchVisualizerClass),
                                      ('/test', StaticVisualizerClass)],
                                      debug=True)


def main():
    run_wsgi_app(application)
#end    


if __name__ == "__main__":
    main()    
