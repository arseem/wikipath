from tracemalloc import start
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

NUM_THREADS = 1000

class PathPuller:

    def __init__(self, start_page, end_page, max_depth=5):
        self.current = start_page
        self.destination = end_page
        self.visited = []
        self.current_path =  [self.current.split('/wiki/')[-1]]

        self.depth = 0
        self.max_depth = max_depth


    def get_links_from_page(self, page):
        try:
            html = requests.get(page).text
        except requests.exceptions.ConnectionError:
            return page, []

        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('div', {"id": "bodyContent"})

        self.visited.append(page.split('/wiki/')[-1])
        print(page.split('/wiki/')[-1].replace('_', ' '))

        links = []
        for anchor in article.find_all('a'):
            link = anchor.get('href', '/')
            links.append(f'https://wikipedia.org{link}') if link.startswith('/wiki/') and not (':' in link) and (link.split('/wiki/')[-1] not in self.visited) else None
            if link.split('/wiki/')[-1] == self.destination.split('/wiki/')[-1]:
                #self.executor.shutdown(cancel_futures=True)
                return -1, page, link

        return page, links

    def search(self):
        links = [[self.get_links_from_page(self.current)]]
        if links[0][0][0]==-1:
            self.current_path.append(self.destination.split('/wiki/')[-1])
            self.current_path = [n.replace('_', ' ').replace('%27', "'") for n in self.current_path]
            return self.current_path, len(self.visited)

        for i in range(self.max_depth):
            links.append([])
            set_of_links = links[i]
            with ThreadPoolExecutor(max_workers=NUM_THREADS) as self.executor:
                for new_links in self.executor.map(self.get_links_from_page, [l[-1] for l in set_of_links][0]):
                    if new_links[0] == -1:
                        self.executor.shutdown(cancel_futures=True)
                        self.current_path.append(set_of_links[0][0].split('/wiki/')[-1]) if set_of_links[0][0].split('/wiki/')[-1]!=self.current_path[0] else None
                        self.current_path.append(new_links[1].split('/wiki/')[-1])
                        self.current_path.append(new_links[-1].split('/wiki/')[-1])
                        self.current_path = [n.replace('_', ' ').replace('%27', "'") for n in self.current_path]
                        return self.current_path, len(self.visited)
                    
                    links[i+1].append(new_links)

        return -1, len(self.visited)



def main():
    while True:
        source = input('Source page>> ')

        source.replace(' ', '_')
        source = f'https://wikipedia.org/wiki/{source}' if not '/wiki/' in source else source

        try:
            requests.get(source)
            break
        except requests.exceptions.ConnectionError:
            print(f'\nSource page does not exist: {source}\n')

    print('\n')
    while True:
        dest = input('Destination page>> ')

        dest.replace(' ', '_')
        dest = f'https://wikipedia.org/wiki/{dest}' if not '/wiki/' in source else source

        try:
            requests.get(dest)
            break
        except requests.exceptions.ConnectionError:
            print(f'\nDestination page does not exist: {dest}\n')


    bs = PathPuller(source, dest)
    start_timer = perf_counter()
    result, num = bs.search()
    print('\n')
    print(f'{num} pages visited\nTime: {perf_counter()-start_timer:.2f}s')
    if result!=-1:
        print(result[0], end='')
        for i in result[1:]:
            print(f' --> {i}', end='')

    else:
        print('No connection in specified range')



if __name__ == '__main__':
    main()
