import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'DeliciousTagExplorer/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaesessions'))


from google.appengine.dist import use_library
use_library('django', '1.2' )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from gaesessions import get_current_session

from TagVisualizer import (StartVisualizerClass, BranchVisualizerClass)
from StaticVisualizer import StaticVisualizerClass
from StartTagSelector import StartTagSelectorClass


class MainPage(webapp.RequestHandler):
    def get(self):
        
        session = get_current_session()
        if session.is_active():
            session.terminate()

        template_values = { }
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, 'templates', 'Start.html')
        self.response.out.write(template.render(path, template_values))
    #end
# end


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/startTagSelector', StartTagSelectorClass),
                                      ('/tags/startTag', StartVisualizerClass),
                                      ('/tags/branch', BranchVisualizerClass),
                                      ('/test', StaticVisualizerClass)],
                                      debug=True)

def main():
    run_wsgi_app(application)
#end    


if __name__ == "__main__":
    main()    
