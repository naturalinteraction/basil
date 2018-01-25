import time

# wget -qO- http://127.0.0.1:50000?ciao

from twisted.web import server, resource
from twisted.internet import reactor

class WebPage(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        print(request)
        return "<html>%s Iterations!</html>\n"%n

def StartWebServer():
    site = server.Site(WebPage())
    reactor.listenTCP(50000, site)
    reactor.startRunning(False)

def WebServerIterate():
    reactor.iterate()

def main():
    global n
    StartWebServer ()
    n=0
    while True:
        n+=1
        if n%10==0:
            print n
        time.sleep(0.1)

        WebServerIterate()

if __name__=="__main__":
    main()
