"""
NAME
    dnd_monster_scrape

DESCRIPTION
    A simple web scraper for the site www.aidedd.org, a French website about DnD. The following information can
    be found for all monsters released for DnD 5e. Attributes marked with * are not available for all creatures.

    name
    challenge rating
    create type
    size
    armor class
    health
    alignment
    legendary
    monster source
    * strength
    * dexterity
    * constitution
    * intelligence
    * wisdom
    * charisma

CONTENTS
    DnDScrapeShallow - collect information about all monsters, collected from a single page

    DnDScrapeDeep - if available, collects deeper information about an individual monster
"""

import bs4
import requests
import pandas as pd
import numpy as np
import time


def DnDScrapeShallow(df_name='data/dnd_data.csv'):
    """ The main function that collects monster information, this gets a lot of details including a url that leads
        to more information (not available for all monsters). Information is stored in a dataframe, this can be
        expanded by calling deep scrape afterwards.

    Args:
        df_name : file name to load / save values from

    Return:
        None
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://www.aidedd.org/dnd-filters/monsters.php'
    req = requests.get(url, headers=hdr)

    if req.status_code == 200:
        soup = bs4.BeautifulSoup(req.text, 'html.parser')
        df = pd.DataFrame(columns=['name', 'url', 'cr', 'type', 'size', 'ac', 'hp', 'speed', 'align', 'legendary', 'source'])

        # grab the entire row and then we'll just divy it up and take what we want, first element is not a monster
        results = soup.find_all('tr')
        for row in results[1:]:
            to_add = []

            # name
            col = row.find_all('input')
            to_add.append(col[0]['value'])

            # link
            col = row.find_all('a')
            to_add.append(col[0]['href'] if col else '')

            # challenge rating
            col = row.find_all('td', class_='center')
            to_add.append(col[0].text)
            
            # type
            col = row.find_all('td', class_='col1')
            to_add.append(col[0].text)
            
            # sizes
            col = row.find_all('td', class_='col2')
            to_add.append(col[0].text)

            # armor class and hp are stored in col3
            col = row.find_all('td', class_='col3')
            to_add.append(col[0].text)
            to_add.append(col[1].text)
            
            # speed
            col = row.find_all('td', class_='col6')
            to_add.append(col[0].text)
            
            # alignment
            col = row.find_all('td', class_='col4')
            to_add.append(col[0].text)
            
            # # legendary
            col = row.find_all('td', class_='col5')
            to_add.append(col[0].text)

            # # source
            col = row.find_all('td', class_='colS')
            to_add.append(col[0].text)

            # add to the end of the df
            df.loc[len(df)] = to_add

        df.to_csv(df_name, index=False)
    else:
        print('Connection Error!')

def DnDScrapeDeep(df_name='data/dnd_data.csv', sleep_time=10):
    """ Supplement function that extends the data from the shallow scrape if a url is available.

    Args:
        df_name : file name to load / save values from
        sleep_time : how long to sleep between page accesses

    Return:
        None
    """
    df = pd.read_csv(df_name)

    for i, row in df.iterrows():
        # if there is a url and we haven't fetched it yet
        if not pd.isna(row['url']) and pd.isna(row['str']):
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = requests.get(row['url'], headers=hdr)
            if req.status_code == 200:
                soup = bs4.BeautifulSoup(req.text, 'html.parser')

                # little messy but I just wanted the numbers, the stats are stored like this
                # STR10 (+0)
                results = soup.find_all('div', class_='carac')
                df.loc[i, 'str'] = results[0].text.split()[0][3:]
                df.loc[i, 'dex'] = results[1].text.split()[0][3:]
                df.loc[i, 'con'] = results[2].text.split()[0][3:]
                df.loc[i, 'int'] = results[3].text.split()[0][3:]
                df.loc[i, 'wis'] = results[4].text.split()[0][3:]
                df.loc[i, 'cha'] = results[5].text.split()[0][3:]
            
                print(df.loc[i, 'name'])
                df.to_csv(df_name, index=False)
            else:
                print('Connection Error!')
            time.sleep(sleep_time)

if __name__ == '__main__':
    print('Roll for initiative!')
