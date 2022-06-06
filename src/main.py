import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, sleep
import os
import threading
import wikipediaapi

NUM_THREADS = 100

class PathPuller:

    def __init__(self, start_page, end_page, max_depth=5):
        self.current = start_page
        self.destination = end_page
        self.visited = []
        self.current_path =  [self.current.split('/wiki/')[-1]]

        self.depth = 0
        self.max_depth = max_depth

        self.found = 0


    def get_links_from_page(self, page):
        try:
            html = requests.get(page).text
        except requests.exceptions.ConnectionError:
            return page, []

        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('div', {"id": "bodyContent"})

        self.visited.append(page.split('/wiki/')[-1])
        #print(page.split('/wiki/')[-1].replace('_', ' '))

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
            self.found = 1
            return self.current_path, len(self.visited)

        for i in range(self.max_depth):
            links.append([])
            self.depth = i+1
            set_of_links = links[i]
            with ThreadPoolExecutor(max_workers=NUM_THREADS) as self.executor:
                for new_links in self.executor.map(self.get_links_from_page, [l[-1] for l in set_of_links][0]):
                    if new_links[0] == -1:
                        self.executor.shutdown(cancel_futures=True)
                        self.current_path.append(set_of_links[0][0].split('/wiki/')[-1]) if set_of_links[0][0].split('/wiki/')[-1]!=self.current_path[0] else None
                        self.current_path.append(new_links[1].split('/wiki/')[-1])
                        self.current_path.append(new_links[-1].split('/wiki/')[-1])
                        self.current_path = [n.replace('_', ' ').replace('%27', "'") for n in self.current_path]
                        self.found = 1
                        return self.current_path, len(self.visited)
                    
                    links[i+1].append(new_links)

        return -1, len(self.visited)



def status_monitor(pp):
    while not pp.found:
        os.system('cls' if os.name=='nt' else 'clear')
        print('STATUS MONITOR\n')
        print(f'Active threads: {threading.active_count()}/{NUM_THREADS}')
        print(f'Layer: {pp.depth}')
        print(f'Visited pages: {len(pp.visited)}')
        print(f'Last seen: {pp.visited[-1] if len(pp.visited)>0 else None}')
        sleep(1)


def get_user_input():
    wiki = wikipediaapi.Wikipedia('en')
    while True:
        source = input('Source page>> ')

        source = source.replace(' ', '_')
        source = f'https://wikipedia.org/wiki/{source}' if not '/wiki/' in source else source
        tocheck = source.split('/wiki/')[-1]

        if wiki.page(tocheck).exists():
            print(f'Setting source page: {source}')
            break
        else:
            print(f'\nSource page does not exist: {source}\n')

    print('\n')
    while True:
        dest = input('Destination page>> ')

        dest = dest.replace(' ', '_')
        dest = f'https://wikipedia.org/wiki/{dest}' if not '/wiki/' in dest else dest
        tocheck = dest.split('/wiki/')[-1]

        if wiki.page(tocheck).exists():
            print(f'Setting destination page: {dest}')
            break
        else:
            print(f'\nDestination page does not exist: {dest}\n')

    print('\n')
    while True:
        try:
            range = int(input('Max range>> '))
            break
        except ValueError:
            print(f'\nMust be a number\n')

    return source, dest, range


def main():
    os.system('cls' if os.name=='nt' else 'clear')
    source, dest, range = get_user_input()

    bs = PathPuller(source, dest, max_depth=range)
    
    loading_thread = threading.Thread(target=status_monitor, args=[bs], daemon=True)
    loading_thread.start()
    
    start_timer = perf_counter()
    result, num = bs.search()
    fin = 's' if num!=1 else ''

    loading_thread.join()
    os.system('cls' if os.name=='nt' else 'clear')
    print('RESULT\n')
    print(f'{num} page{fin} visited\nTime: {perf_counter()-start_timer:.2f}s')
    if result!=-1:
        print(result[0], end='')
        for i in result[1:]:
            print(f' --> {i}', end='')

    else:
        print('No connection in specified range')

    print('\n')
    input('Press Enter to restart...')
    main()



if __name__ == '__main__':
    main()
