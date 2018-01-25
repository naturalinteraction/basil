import time

# wget -qO- http://127.0.0.1:8080?ciao

from twisted.web import server, resource
from twisted.internet import reactor

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        print(request)
        return "<html>%s Iterations!</html>\n"%n

def main():
    global n
    site = server.Site(Simple())
    reactor.listenTCP(8080, site)
    reactor.startRunning(False)
    n=0
    while True:
        n+=1
        if n%10==0:
            print n
        time.sleep(1.0)
        reactor.iterate()

if __name__=="__main__":
    main()
