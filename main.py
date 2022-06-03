import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

NUM_THREADS = 100
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

        self.visited.append(page.split('/wiki/')[-1])

        links = []
        for anchor in article.find_all('a'):
            link = anchor.get('href', '/')
            links.append(f'https://wikipedia.org{link}') if link.startswith('/wiki/') and not ':' in link and link.split('/wiki/')[-1] not in self.visited else None
            if link == self.destination:
                return -1, link

        return page, links

    def search(self):
        links = [[self.get_links_from_page(self.current)]]
        if links==-1:
            return self.current_path

        for i in range(self.max_depth):
            links.append([])
            set_of_links = links[i]
            with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                for new_links in executor.map(self.get_links_from_page, [l[-1] for l in set_of_links][0]):
                    if new_links[0] == -1:
                        self.current_path.append(set_of_links[0].split('/wiki/')[-1]) if set_of_links[0].split('/wiki/')[-1]!=self.current_path[0] else None
                        self.current_path.append(new_links[0].split('/wiki/')[-1])
                        self.current_path.append(new_links[-1].split('/wiki/')[-1])
                        return self.current_path
                    
                    links[i+1].append(new_links)

        return 'No connection in specified range'


bs = PathPuller('https://wikipedia.org/wiki/Spoon', 'https://wikipedia.org/wiki/Adolf_Hitler')
print(bs.search())

