
DEBATE_URL = 'http://www.presidency.ucsb.edu/debates.php'
last_fetched_at = None
import json
import urllib.request, time, re, random, hashlib
import bs4
import time
import sys
import nltk
import nltk.data
from nltk.corpus import stopwords
from nltk import FreqDist



def fetch(url):
    """Load the url compassionately."""
    
    global last_fetched_at
    
    url_hash = hashlib.sha1(url.encode()).hexdigest()
    filename = 'cache/cache-file-{}'.format(url_hash)
    try:
        with open(filename, 'r') as f:
            result = f.read()
            if len(result) > 0:
                #print("Retrieving from cache:", url)
                return result
    except:
        pass
    
    #print("Loading:", url)
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

def debate_processing(soup):
    return_list = []
    tables = soup.find_all('table')
    
    for table in tables:
        if table['width'] == '700' and table['bgcolor'] == "#FFFFFF":
            actual_table = table
    rows = actual_table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        try:
            link = row.find('a')['href']
            cols.append(link)
            return_list.append(cols)
        except:
            pass

    return return_list

def get_words_from_speech(link):
    result = fetch(link)
    soup = bs4.BeautifulSoup(result,'lxml')
    return soup



def find_politician_names(debate_soup_dict):
    for debate in debate_soup_dict.keys():
        raw = debate_soup_dict[debate]['soup'].get_text()
        #raw = raw.replace("\\\", "")
        raw = raw.replace("\\", "")
        raw = raw.replace(".", ". ")
        raw = raw.replace("?", "? ")
        raw = raw.replace("!", "! ")
        raw = raw.replace("  ", " ")
        raw = raw.replace("[applause]", "")
        raw = raw.replace("[crosstalk]", "")
        raw = raw.replace("[laughter]" "[Laughter]" "(LAUGHTER)", "")
        tokens = nltk.word_tokenize(raw)
        speech = nltk.Text(tokens)
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = sent_detector.tokenize(raw.strip())

        #find candidate names, most commonly repeated first words of sentences, not common words
        colon_names = []
        dumbWords = stopwords.words('english')

        for sent in sents:
            if ':' in sent:
                sent = sent.split(':')
                possible_name = sent[0]
                if (len(possible_name)<25):
                    colon_names.append(possible_name)


        fdist1 = FreqDist(colon_names)
        fdist2 = FreqDist(sents)
        mostFreq = fdist1.most_common(1)[0][1]
        if mostFreq > 20 :
            debate_soup_dict[debate]['names'] = fdist1.most_common(10)
        else:
            debate_soup_dict[debate]['names'] = fdist2.most_common(10)



if __name__ == '__main__':
    result = fetch(DEBATE_URL)
    soup = bs4.BeautifulSoup(result,'lxml')
    debate_list = debate_processing(soup)
    final_list = {}
    for debate in debate_list:

        if ' ' not in debate[0]:
            debate = debate[1:]
        debate_id = ' '.join(debate[:2])
        try:
            debate_datetime = time.strptime(debate[0].replace('th','').replace('st',''),'%B %d, %Y')
        except:
            debate_datetime = None

        final_list[debate_id] = {}
        final_list[debate_id]['link'] = debate[2]
        final_list[debate_id]['time'] = debate_datetime 
        
        try:
            final_list[debate_id]['soup'] = get_words_from_speech(debate[2])
        except:
            final_list[debate_id]['soup'] = None

    find_politician_names(final_list)






            



