
DEBATE_URL = 'http://www.presidency.ucsb.edu/debates.php'
last_fetched_at = None
import urllib.request, time, re, random, hashlib
import bs4


def fetch(url):
    """Load the url compassionately."""
    
    global last_fetched_at
    
    url_hash = hashlib.sha1(url.encode()).hexdigest()
    filename = 'cache/cache-file-{}'.format(url_hash)
    try:
        with open(filename, 'r') as f:
            result = f.read()
            if len(result) > 0:
                print("Retrieving from cache:", url)
                return result
    except:
        pass
    
    print("Loading:", url)
    wait_interval = random.randint(3000,10000)
    if last_fetched_at is not None:
        now = time.time()
        elapsed = now - last_fetched_at
        if elapsed < wait_interval:
            time.sleep((wait_interval - elapsed)/1000)
        
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = { 'User-Agent' : user_agent }
    req = urllib.request.Request(url, headers = headers)
    last_fetched_at = time.time()
    with urllib.request.urlopen(req) as response:
        result = str(response.read())
        with open(filename, 'w') as f:
            f.write(result)
        return result







if __name__ == '__main__':
    debates_html = fetch(DEBATE_URL)
    soup = bs4.BeautifulSoup(debates_html,'lxml')
    tables = soup.find_all('table')
    for table in tables:
        if table['width'] == '700' and table['bgcolor'] == "#FFFFFF":
            print('table found')
            actual_table = table
    rows = actual_table.find_all('tr')
    print(rows[10])
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        try:
            link = row.find('a')['href']
            print(link)
            
        except:
            link = False

        if link:
            cols.append(link)
        print(cols)


