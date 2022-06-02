import requests
from bs4 import BeautifulSoup

class PathPuller:

    def __init__(self, start_page, end_page, max_depth=5):
        self.current = start_page
        self.destination = end_page
        self.visited = [self.current.split('/wiki/')[-1]]
        self.current_path =  [self.current.split('/wiki/')[-1]]

        self.depth = 0
        self.max_depth = max_depth


    def get_links_from_page(self, page):
        html = requests.get(page).text
        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('div', {"id": "bodyContent"})

        links = []
        for anchor in article.find_all('a'):
            link = anchor.get('href', '/')
            links.append(f'https://wikipedia.org{link}') if link.startswith('/wiki/') and not ':' in link and link.split('/wiki/')[-1] not in self.visited else None
            if link == self.destination:
                self.current_path.append(link.split('/wiki/')[-1])
                return -1

        return links

    def search(self):
        links = [self.get_links_from_page(self.current)]
        if links==-1:
            return self.current_path

        for i in range(self.max_depth):
            links.append([])
            for l in links[i]:
                self.visited.append(l.split('/wiki/')[-1])
                new_links = self.get_links_from_page(l)
                if new_links == -1:
                    return self.current_path
                
                links[i+1].append(new_links)

        return 'No connection in specified range'



