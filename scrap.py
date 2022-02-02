from bs4 import BeautifulSoup
import requests
import re
import index


def make_request(url):
    response = requests.get(url)

    return response

def get_links(response):
    soup = BeautifulSoup(response.text,'html.parser')
    main_div = soup.find('div',attrs={'class':'entry-content'})
    links = main_div.find_all('a')
    drive_pattern = "https://drive.google.com/open?id="

    for link in links:
        if drive_pattern in link['href']:
            match = re.search(rf"{re.escape(drive_pattern)}(.*)",link['href'])
            index.main(match.group(1))
            
        

if __name__ == "__main__":
    url ="https://asianclassics.org/library/downloads/"
    response = make_request(url)
    links = get_links(response)
