import os


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from TagVisualizer import TagVisualizerClass

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = { 'name': 'Zardoz' }
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, 'templates', 'BaseTemplate.html')
        self.response.out.write(template.render(path, template_values))
    #end
# end


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/tags', TagVisualizerClass)],
                                      debug=True)


def main():
    run_wsgi_app(application)
#end    


if __name__ == "__main__":
    main()    
