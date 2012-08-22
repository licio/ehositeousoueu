import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class UrlSrc(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)
    url = db.LinkProperty()
    isdown = db.BooleanProperty()

class Absurdos(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)
    content = db.StringProperty()

class MainPage(webapp.RequestHandler):
  def get(self):
    import os
    from google.appengine.ext.webapp import template
    template_values = {
	'legal': 'nada',
       }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))
    


class SiteVerifier(webapp.RequestHandler):
  def testasite(self,url):
    from google.appengine.api import urlfetch
    if(url.count('.') < 1 or url.count(' ') > 0):
	#url = 'http://miud.in/24Q'
	absurdo = Absurdos()
	absurdo.content = url
	absurdo.put()
	return 2,url
    	
    urlcount = url.count('/')
    if(urlcount < 2 and urlcount != 0):
	url = 'http://' + url.split("/",1)[0]
    elif(urlcount == 0): 
	url = 'http://' + url
    try:
    	result = urlfetch.fetch(url)
	if(result.status_code >= 400):
		self.putindb(url,0)
		return 3,url
    except urlfetch.DownloadError:
	self.putindb(url,1)
    	return 0,url 
    self.putindb(url,0)
    return 1,url
       
  def putindb(self,url,isdown):
    #print isdown
    urlsrc = UrlSrc()  
    urlsrc.url = url
    if(isdown == 0):
	urlsrc.isdown = False 
	#print urlsrc.isdown
    else:
	urlsrc.isdown = True

    urlsrc.put()
 
  def post(self):
    if (cgi.escape(self.request.get('url'))):
      status,url=self.testasite(cgi.escape(self.request.get('url')))

      if (status == 1):
        mensagem = 'est&aacute; funcionando, o problema &eacute; seu!'
      elif(status ==2):
	mensagem = 'parece uma url para voce?'
      elif(status == 3):
	mensagem = 'existe, mas parece estar com problemas.'
      else:
        mensagem = 'n&atilde;o est&aacute; mesmo funcionando.'
    else:
	mensagem = 'algo precisa ser digitado.'
	url = 'http://miud.in/24Q'
    import os
    from google.appengine.ext.webapp import template
    template_values = {
	'mensagem': mensagem,
	'url': url,
       }
    path = os.path.join(os.path.dirname(__file__), 'resposta.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/verifica', SiteVerifier)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
