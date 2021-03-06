import importlib
import inspect
import sys
from collections import namedtuple
from pprint import pprint

import requests
from bs4 import BeautifulSoup


class ScraperAccess(object):
    @staticmethod
    def get_scrapers():
        """Provides the service with a dict of available scraper classes
        and the required value (site) to call each - No need to edit """
        cls_members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        scraper_dict = {}
        for cls in cls_members:
            try:
                scraper_dict[cls[1].site] = cls[1]
            except Exception as e:
                print(e)
        return scraper_dict

    @staticmethod
    def print_scrapers():
        scrapers = ScraperAccess.get_scrapers()
        for scraper in scrapers:
            scraper_name = scrapers[scraper].__name__
            if scraper_name is not 'AllScrapers':
                this_scraper = getattr(importlib.import_module("scrape"), scraper_name)
                instance = this_scraper()
                pprint(instance.results)


class Scraper:
    """The parent class from which all site scraper classes can
    inherit in order to serialise the API's json output"""

    # Event fields required to be returned from scraping - TBC
    Event = namedtuple('Event', ['site', 'description', 'datetime', 'event_url', 'img_urls', 'title'])
    Event.__new__.__defaults__ = (None,) * len(Event._fields)

    # http://www.wicket.space/walthamstuff?site=demo
    site = 'demo'

    def __init__(self):
        self.events = []
        self.scrape()

    def add_event(self, event):
        event = event._replace(site=self.site)
        self.events.append(event)

    def scrape(self):
        # Add an event
        self.add_event(self.Event(site="this will be replaced with self.site",
                                  description='Exciting stuff is planned!',
                                  datetime='yyyy-mm-ddThh:mm:ss.000Z',
                                  event_url='www.demosite.com/events/exciting',
                                  img_urls=['www.123.com/123.jpg', 'www.xx.com/xx.jpg']))
        # Add another event......
        self.add_event(self.Event(description="Leaving out lots of details. No field is mandatory"))

    @property
    def results(self):
        if self.events:
            return self.events
        else:
            return "No Events Found"


###############################################################################################################
# EXAMPLE SCRAPER CLASSES

# @app.route('/walthamstuff')
# def getScrapedStuff():
#     #http://www.wicket.space/walthamstuff?site=sitename
#     site = request.args.get('site')
#     scraper = scrape.get_scrapers()
#     scraped_site = scraper[site]()
#     return jsonify({'data': scraped_site.results})

class AllScrapers(Scraper):
    site = 'all'

    def scrape(self):
        ScraperAccess.print_scrapers()


class TicketLab(Scraper):
    # http://www.wicket.space/walthamstuff?site=ticketlab
    site = 'ticketlab'

    def scrape(self):
        # add scraping code here
        r = requests.get("https://ticketlab.co.uk/events/e17")
        soup = BeautifulSoup(r.text, "lxml")
        events = soup.find_all(class_ = "Listings-item")
        for event in events:
            event_url = event.find('a')['href']

            self.add_event(self.Event(event_url=event_url))
            r = requests.get(event_url)
            soup = BeautifulSoup(r.text, "lxml")
            elems = soup.find_all('h1')
            for elem in elems:
                print(elem.find_all('span'))
                #//*[@id="main-content"]/section/div[1]/div/h2[2]

class MorrisGallery(Scraper):
    # http://www.wicket.space/walthamstuff?site=morris
    site = 'morris'

    def scrape(self):
        # add scraping code here
        self.add_event(self.Event(event_url="http://www.wmgallery.org.uk/event1"))


class Hornbeam(Scraper):
    # http://www.hornbeam.org.uk/feed/
    site = 'hornbeam'
    def scrape(self):
        r = requests.get("http://www.hornbeam.org.uk/all-events-at-the-hornbeam/")
        soup = BeautifulSoup(r.text, "lxml")
        # add scraping code here
        events = soup.find_all(class_='EventsTable-eventName')
        for event in events:
            title = event.text
            event_url = event.find('a')['href']
            s = requests.get(event.find('a')['href'])
            soup = BeautifulSoup(s.text, "lxml")
            try:
                img_urls = []
                img_urls.append(soup.find(class_='post-thumbnail').find('img')['src'])
            except:
                pass

            try:
                description = soup.find(class_='post-content').text
            except:
                pass


            self.add_event(self.Event(title=title,
                                      description=description,
                                      event_url=event_url,
                                      img_urls=img_urls))


class MillE17(Scraper):
    # http://www.wicket.space/walthamstuff?site=mill
    site = 'mill'

    def scrape(self):

        self.add_event(self.Event(event_url="http://themille17.org/event2",
                                  description="More Stuff Happens"))


class WalthamForest(Scraper):
    def __init__(self):
        super().__init__()

    # https://www.walthamforest.gov.uk/events
    site = 'waltham_forest'

    def scrape(self):
        url = "https://www.walthamforest.gov.uk/events"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        date_months = soup.findAll("div", {"class": "views-field views-field-field-when-is-it-1"})
        date_days = soup.findAll("div", {"class": "views-field views-field-field-when-is-it-2"})
        titles = soup.findAll("div", {"class": "views-field views-field-title"})
        links = soup.findAll("div", {"class": "views-field views-field-view-node"})
        descriptions = soup.findAll("div", {"class": "views-field views-field-body"})

        for i, title in enumerate(titles):
            datetime = date_months[i].find("time").attrs['datetime']
            description = descriptions[i].text
            link = "".join([url, links[i].find("a").attrs['href']])
            self.add_event(self.Event(datetime=datetime, title=title.text, description=description, event_url=link))


if __name__ == "__main__":
    m = TicketLab()
    print(pprint(m.results))



    # pprint(print_scrapers())
    # pprint(AllScrapers().results)
    # print("now get all of them")
    # a = AllScrapers()
    # print(a.results)
