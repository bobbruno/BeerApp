import codecs
import cookielib
import mechanize
import os
import random
import socket
import time
from urlparse import urlparse
import socks


class Scraper(object):
    """
    Controls all the scraping for a particular website and its subsites.
    scrapeSite method should be overriden to manage navigation through
    the web pages.
    """
    @staticmethod
    def _createConnection(address, timeout=None, source_address=None):
        sock = socks.socksocket()
        sock.connect(address)
        return sock

    def __init__(self, sleepTime=5, maxTries=20,
                 useCache=True, clearCookies=False,
                 cacheDir='./', proxy='127.0.0.1',
                 proxyPort=9050, verbose=False, maxGets=None,
                 uaString='Your friendly neighbourhood spiderbot.'):
        """
        Constructor for the class.
        :param int sleepTime: average time to sleep (in seconds) between calls.
               The scraper will wait a random amount of time based on that
               average after GETting each page.
        :param int maxTries: maximum number of retries before raising an exception.
               Defaults to 20.
        :param bool useCache: defines if the site should be cached or not.
               True by default
        :param bool clearCookies: Defines if the scraper should clear cookies
               before each access
        :param str cacheDir: Directory where cached pages should be stored.
               Defaults to current directory
        :param str proxy: string address of the proxy website.
               Defaults to tor's default address.
        :param int proxyPort: Port number for the proxy.
               Defaults to tor's default port
        :param bool verbose: Defines if the scraper should produce messages
               during its work or not. Defaults to false
        :param int maxGets: if defined, sets a limit on the number of pages,
              after which the scraper will always fail.
        :param str uaString: user-agent string
        """
        self.sleepTime = sleepTime
        self.maxTries = maxTries
        self.useCache = useCache
        self.clearCookies = clearCookies
        self.cacheDir = cacheDir
        self.proxy = proxy
        self.proxyPort = proxyPort
        self.nGets = 0
        self.verbose = verbose
        self.maxGets = maxGets
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,
                              self.proxy, self.proxyPort)
        socket.socket = socks.socksocket
        socket.create_connection = Scraper._createConnection
        socket.setdefaulttimeout(60)
        cookieJar = cookielib.LWPCookieJar()
        self.br = mechanize.Browser()
        self.br.set_cookiejar(cookieJar)
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.uaString = uaString
        self.br.addheaders = [('User-agent', self.uaString)]

    def changeConnParms(self, sleepTime=None, maxTries=None, useCache=None,
                        clearCookies=None, cacheDir=None, proxy=None,
                        proxyPort=None, verbose=None, maxGets=None,
                        uaString=None):
        """
        Changes any of the connection parameters specified.
        :param int sleepTime: average time to sleep (in seconds) between calls.
               The scraper will wait a random amount of time based on that
               average after GETting each page.
        :param int maxTries: maximum number of retries before raising an exception.
        :param bool useCache: defines if the site should be cached or not.
        :param bool clearCookies: Defines if the scraper should clear cookies
               before each access
        :param str cacheDir: Directory where cached pages should be stored.
        :param str proxy: string address of the proxy website.
        :param int proxyPort: Port number for the proxy.
        :param bool verbose: Defines if the scraper should produce messages
               during its work or not.
        :param int maxGets: if defined, sets a limit on the number of pages,
              after which the scrapDefaults to tor's default porter will always fail.
        :param str uaString: user-agent string
        """
        if (sleepTime is not None):
            self.sleepTime = sleepTime
        if (maxTries is not None):
            self.maxTries = maxTries
        if (useCache is not None):
            self.useCache = useCache
        if (clearCookies is not None):
            self.clearCookies = clearCookies
        if (cacheDir is not None):
            self.cacheDir = cacheDir
        if (proxy is not None):
            self.proxy = proxy
        if (proxyPort is not None):
            self.proxyPort = proxyPort
        if (verbose is not None):
            self.verbose = verbose
        if (maxGets is not None):
            self.maxGets = maxGets
        if (uaString is not None):
            self.uaString = uaString
            self.br.addheaders = [('User-agent', self.uaString)]

    def login(self, user='', password='', loginPage=None, loginForm=None,
              startPage=None,):
        """
        Login method for the scraper. Actually just stores the params for later use.
        :param str user: Username to be used for login
        :param str password: password for that user
        :param str loginPage: URL of the login page
        :param str loginForm: name of the Form object to look for
        :param str startPage: URL of an optional starting page to navigate
               from, simulating a real user.
        """
        self.user = user
        self.password = password
        self.loginPage = loginPage
        self.loginForm = loginForm
        self.startPage = startPage

    def beforeFirst(self):
        """
        Gets called before the first call to _getSitePure(). Should deal with
        logins, etc.
        This method should be overriden by any descendants.
        """
        #  First, let's go to the initial page, if it's there
        self.nGets = 1
        if (self.startPage is not None):
            self._getSitePure(self.startPage)
        self._getSitePure(self.loginPage)
        self.br.select_form(name=self.loginForm)
        self.br.form["username"] = self.user
        self.br.form["pwd"] = self.password
        self.br.form.find_control(name="SaveInfo").items[0].selected = False
        resp = self.br.submit()
        self.nGets -= 1

    def _getSitePure(self, site):
        """
        Gets a site directly, with no caching whatsoever
        :param str site: URL of the site that is to be downloaded
        :rtype str
        """

        if (not self.nGets):
            self.beforeFirst()
        tryCounter = 0
        while True:
            try:
                self.nGets += 1
                if self.clearCookies:
                    self.br._ua_handlers['_cookies'].cookiejar.clear_session_cookies()
                if self.verbose:
                    print('Calling open on {}').format(site).encode('utf8')
                retVal = self.br.open(site)
                if self.sleepTime:
                    time.sleep(random.expovariate(1 / float(self.sleepTime)))
                theHTML = retVal.read()
            except Exception, e:
                tryCounter += 1
                if self.verbose:
                    print 'Getting {} did not work ({})'.format(site, str(e)).encode('utf8')
                    if (tryCounter >= self.maxTries // 2):
                        retVal = self.br.open('http://checkip.dyndns.com/')
                        theHTML = retVal.read()
                        print 'Checking: {}'.format(theHTML).encode('utf8')
                if (tryCounter >= self.maxTries):
                    if self.verbose:
                        print 'Could not get {}: Error {}'.format(site, str(e)).encode('utf8')
                    raise e
                else:
                    if self.sleepTime:
                        time.sleep(random.expovariate(1 / float(self.sleepTime)))
                    continue
            else:
                break
        return theHTML

    def getSite(self, site):
        '''
        Returns the HTML of the site requested. Raises an exception if more
        than maxTries attempts are made and the site cannot be recovered.
        :param str site: Site URL
        :rtype str
        '''
        if self.verbose:
            print 'getting {}\n'.format(site).encode('utf8')

        if self.useCache:
            parsedURL = urlparse(site)
            path = parsedURL.path
            if (path == ''):
                path = 'INDEX'
            if (path[0] == '/'):
                path = path[1:]
            if (path[-1] == '/'):
                path = '{}INDEX'.format(path)
            dirPath = os.path.split(path)[0]
            cacheDir = os.path.join(self.cacheDir, parsedURL.netloc, dirPath)
            cacheFile = os.path.join(self.cacheDir, parsedURL.netloc, path)
            if os.path.isfile(cacheFile):
                inputStream = codecs.open(cacheFile, 'r', encoding='utf8')
                html = inputStream.readlines()
                inputStream.close()
                return u''.join(html)
            else:
                theHTML = self._getSitePure(site)
                if not os.path.exists(cacheDir):
                    os.makedirs(cacheDir)
                fstream = codecs.open(cacheFile, 'w', encoding='utf8')
                fstream.write(theHTML.decode('latin-1'))
                fstream.close()
        else:
            theHTML = self._getSitePure(site)
        return theHTML

    def getSiteCollection(self, siteCol):
        """
        Gets a collection of sites passed to it. Returns a dictionary
        of {id: html} for pages successfully recovered. If a page in the
        original collection cannot be recovered, it won't be on the
        returned dictionary.
        :param dict siteCol: dictionary of sites to be recovered,
            formatted as {id: URL}.Id can be any type acceptable
            as a dictionary key.
        :rtype dict
        """
        sites = {}
        for key, url in siteCol.iteritems():
            try:
                theHTML = self.getSite(url)
            except:
                continue
            else:
                sites[key] = theHTML
        return sites
