import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, sleep
import os
import threading
import wikipediaapi

NUM_THREADS = 1000

class PathPuller:

    def __init__(self, start_page, end_page, max_depth=5):
        self.current = start_page
        self.destination = end_page
        self.visited = []
        self.current_path =  []

        self.depth = 0
        self.max_depth = max_depth

        self.found = 0
        self.con_err = []
        self.json_err = 0


    def get_links_from_page(self, page):
        try:
            html = requests.get(page).text
        except requests.exceptions.ConnectionError:
            self.con_err.append(page.split('/wiki/')[-1])
            return page, []

        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find('div', {"id": "bodyContent"})

        self.visited.append(page.split('/wiki/')[-1])
        #print(page.split('/wiki/')[-1].replace('_', ' '))

        links = []
        if article:
            for anchor in article.find_all('a'):
                link = anchor.get('href', '/')
                links.append(f'https://wikipedia.org{link}') if link.startswith('/wiki/') and not (':' in link) and (link.split('/wiki/')[-1] not in self.visited) else None
                if link.split('/wiki/')[-1] == self.destination.split('/wiki/')[-1]:
                    new_links = (-1, page, link)
                    set_of_links = self.set_of_links
                    self.current_path.append(set_of_links[0][0].split('/wiki/')[-1])
                    self.current_path.append(new_links[1].split('/wiki/')[-1])
                    self.current_path.append(new_links[-1].split('/wiki/')[-1])
                    self.current_path = [n.replace('_', ' ').replace('%27', "'") for n in self.current_path]
                    self.found = 1
                    self.executor.shutdown(cancel_futures=True, wait=False)
                    return -1, page, link

        return page, links

    def search(self):
        links = [[self.get_links_from_page(self.current)]]
        if links[0][0][0]==-1:
            self.current_path.append(self.current.split('/wiki/')[-1])
            self.current_path.append(self.destination.split('/wiki/')[-1])
            self.current_path = [n.replace('_', ' ').replace('%27', "'") for n in self.current_path]
            self.found = 1
            return self.current_path, len(self.visited)

        for i in range(self.max_depth):
            links.append([])
            self.depth = i+1
            set_of_links = links[i]
            self.set_of_links = set_of_links
            try:
                with ThreadPoolExecutor(max_workers=NUM_THREADS) as self.executor:
                    for new_links in self.executor.map(self.get_links_from_page, [l[-1] for l in set_of_links][0]):
                        if new_links[0] == -1:
                            return self.current_path, len(self.visited)
                        
                        links[i+1].append(new_links)

            except RuntimeError:
                return self.current_path, len(self.visited)

        self.found = -1
        return -1, len(self.visited)



def status_monitor(pp):
    fcon = ''
    while not pp.found:
        start = perf_counter()
        if pp.con_err:
            fcon = 'Failed connections: '
            if len(pp.con_err)<5:
                for i in pp.con_err[:-1]:
                    fcon+=f'{i}, ' 
                fcon+=str(pp.con_err[:-1])
            else:
                for i in range(1, 5):
                    fcon+=f'{pp.con_err[-i]}, '
                fcon+=pp.con_err[-5]
                if len(pp.con_err)>5:
                    fcon+=f', + {len(pp.con_err)} more\n'
                    
        os.system('cls' if os.name=='nt' else 'clear')
        print(f'''
        STATUS MONITOR\n\n
        Active threads: {threading.active_count()}/{NUM_THREADS}\n
        Layer: {pp.depth}\n
        Visited pages: {len(pp.visited)}\n
        Last seen: {pp.visited[-1] if len(pp.visited)>0 else None}\n
        {fcon}
        ''', flush=True)

        while perf_counter()-start<1:
            pass
    
    print_path(pp.current_path)   
    a = 'NOT ' if pp.found==-1 else ''
    print(f'\n\nPATH {a}FOUND\nTerminating remaining threads...')


def print_path(result):
    if result!=-1:
        for i in result:
            if i!=result[0]:
                print(f' --> {i}', end='')
            else:
                print(f'\n{result[0]}', end='')
    
    else:
        print('No connection in specified range')


def get_user_input():
    wiki = wikipediaapi.Wikipedia('en')

    json_err_check = page_exist_check = 1
    while page_exist_check:
        source = input('Source page>> ')

        source = source.replace(' ', '_')
        source = f'https://wikipedia.org/wiki/{source}' if not '/wiki/' in source else source
        tocheck = source.split('/wiki/')[-1]
        while json_err_check:
            try:
                if wiki.page(tocheck).exists():
                    print(f'Setting source page: {source}')
                    page_exist_check = 0
                else:
                    print(f'\nSource page does not exist: {source}\n')     
                json_err_check = 0
                
            except json.decoder.JSONDecodeError:
                for i in range(10):
                    os.system('cls' if os.name=='nt' else 'clear')  
                    print('Request blocked')
                    print(f'Encountered JSON decoder error, waiting {10-i} seconds...')
                    sleep(1)


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
            max_range = int(input('Max range>> '))
            break
        except ValueError:
            print(f'\nMust be a number\n')

    return source, dest, max_range


def main():
    os.system('cls' if os.name=='nt' else 'clear')
    source, dest, max_range = get_user_input()

    bs = PathPuller(source, dest, max_depth=max_range)
    
    loading_thread = threading.Thread(target=status_monitor, args=[bs], daemon=True)
    loading_thread.start()
    
    start_timer = perf_counter()
    result, num = bs.search()
    fin = 's' if num!=1 else ''

    loading_thread.join()
    os.system('cls' if os.name=='nt' else 'clear')
    print('RESULT\n')
    print(f'{num} page{fin} visited\nTime: {perf_counter()-start_timer:.2f}s')
    print_path(result)

    print('\n')
    input('Press Enter to restart...')
    main()



if __name__ == '__main__':
    main()
