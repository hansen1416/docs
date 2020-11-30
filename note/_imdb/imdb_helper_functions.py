import logging
import os
import re
import requests
import sys

from bs4 import BeautifulSoup
import numpy as np
import urllib

import imdb_code

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def imdb_debug_log(msg):
  if os.environ.get("IMDB_DEBUG"):
    log.debug(msg)
    
def imdb_strip_text(text_string):
  return text_string.strip('\r\n ')

def imdb_join_link(link):
  return urllib.parse.urljoin('https://www.imdb.com', link)
  
def test_url_validity(url):
  regex = re.compile(
      r'^(?:http|ftp)s?://' # http:// or https://
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
      r'localhost|' #localhost...
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
      r'(?::\d+)?' # optional port
      r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  
  assert re.match(regex, url) is not None, "invalid url {0}".format(url)
  
def get_actor_movie_soup(actor_url):
  headers = {'Accept-Language': 'en',
           'X-FORWARDED-FOR': '2.21.184.7'}

  test_url_validity(actor_url)
  
  response = requests.get(actor_url, headers = headers)

  return BeautifulSoup(response.text, features="html.parser")

def get_actor_url_by_name(names):
  """
  get actors' standard url by names
  """
  if type(names) is str:
    names = [names]

  actors_url_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/actors_url.npy'

  actors_url = {}

  if os.path.isfile(actors_url_file):
    actors_url = np.load(actors_url_file, allow_pickle = True).item()

  if len(actors_url) == 10:
    return {key: actors_url[key] for key in names}

  headers = {'Accept-Language': 'en',
              'X-FORWARDED-FOR': '2.21.184.8'}

  search_url = 'https://www.imdb.com/find?q={0}&ref_=nv_sr_sm'

  for name in names:
    response = requests.get(search_url.format(name.replace(' ', '+')), headers=headers)

    soup = BeautifulSoup(response.text)

    findSection = soup.find_all('div', attrs={'class': 'findSection'})

    for section in findSection:
      sectionHeader = section.find('h3', attrs={'class': 'findSectionHeader'})

      if sectionHeader.text != 'Names':
        continue

      secTable = section.find('table', attrs={'class': 'findList'})

      if not secTable:
        continue

      namesTr = secTable.find_all('tr')

      for tr in namesTr:
        tds = tr.find_all('td')

        if 'Actor' in tds[1].text or 'Actress' in tds[1].text:
          actors_url[name] = imdb_join_link(tds[1].find('a', href=True)['href'])
          break

  np.save(actors_url_file, actors_url)

  return actors_url
  
def get_actor_name_by_url(actor_url):
  """
  get actor's name by url
  """
  actors_url_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/actors_url.npy'

  actors_url = {}

  if os.path.isfile(actors_url_file):
    actors_url = np.load(actors_url_file, allow_pickle = True).item()

  for name, url in actors_url.items():
    if url == actor_url:
      return name

  soup = get_actor_movie_soup(actor_url)

  h1 = soup.find('h1')
  
  if not h1:
    return ''
    
  itemprop = h1.find('span', attrs={'class': 'itemprop'})

  if not itemprop:
    return ''

  return imdb_strip_text(itemprop.text)


def check_saved_data():
  seen_movies = {}

  seen_movies_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/seen_movies.npy'
  
  if os.path.isfile(seen_movies_file):
    seen_movies = np.load(seen_movies_file, allow_pickle = True).item()

  seen_actors = {}

  seen_actors_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/seen_actors.npy'

  if os.path.isfile(seen_actors_file):
    seen_actors = np.load(seen_actors_file, allow_pickle = True).item()

  return seen_actors, seen_movies


def get_movies_by_actor(actor_url, saved_actors=None, num_of_movies_limit=None):
  """
  first try to read actor info from pre saved file,
  if not exists, scrap from IMDB
  """
  if saved_actors and actor_url in saved_actors:
    actors_movies = saved_actors[actor_url]
  else:
    seen_actors = {}

    seen_actors_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/seen_actors.npy'

    if os.path.isfile(seen_actors_file):
      seen_actors = np.load(seen_actors_file, allow_pickle = True).item()

    if actor_url in seen_actors:
      actors_movies = seen_actors[actor_url]
    else:
      imdb_debug_log('Unseen actor url {0}, start fetching'.format(actor_url))
      actor_soup = get_actor_movie_soup(actor_url)

      actors_movies = imdb_code.get_movies_by_actor_soup(actor_soup)

      seen_actors[actor_url] = actors_movies

      np.save(seen_actors_file, seen_actors)
      imdb_debug_log('New actor url {0}, saved into {1}'.format(actor_url, seen_actors_file))
    
  if num_of_movies_limit:
    return actors_movies[:num_of_movies_limit]
  else:
    return actors_movies


def get_actors_by_movie(movie_url, saved_movies=None, num_of_actors_limit=None):
  """
  first try to read movie info from pre saved file,
  if not exists, scrap from IMDB
  """
  if saved_movies and movie_url in saved_movies:
    movies_actors = saved_movies[movie_url]
  else:
    seen_movies = {}

    seen_movies_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/seen_movies.npy'
    
    if os.path.isfile(seen_movies_file):
      seen_movies = np.load(seen_movies_file, allow_pickle = True).item()

    if movie_url in seen_movies:
      movies_actors = seen_movies[movie_url]
    else:
      imdb_debug_log('Unseen movie url {0}, start fetching'.format(movie_url))
      movie_soup = get_actor_movie_soup(movie_url)

      movies_actors = imdb_code.get_actors_by_movie_soup(movie_soup)

      seen_movies[movie_url] = movies_actors

      np.save(seen_movies_file, seen_movies)
      imdb_debug_log('New movie url {0}, saved into {1}'.format(movie_url, seen_movies_file))

  if num_of_actors_limit:
    return movies_actors[:num_of_actors_limit]
  else:
    return movies_actors

def search_actor_connection(start_actor_tuple, target_actor_tuple, path, saved_actors=None, saved_movies=None, max_depth=None, num_of_actors_limit=None, num_of_movies_limit=None):
  """
  search connection between actors recurrsively
  """
  if len(path.split('::')) >= max_depth:
    imdb_debug_log('path {0} exceed max depth {1}'.format(path, max_depth))
    return None
  
  imdb_debug_log('search connection movie between {0} {1} and {2} {3}'.format(start_actor_tuple[0], start_actor_tuple[1], target_actor_tuple[0], target_actor_tuple[1]))
  test_url_validity(target_actor_tuple[1])
  # get actor's movie list
  movies_tuple_list = get_movies_by_actor(start_actor_tuple[1], saved_actors, num_of_movies_limit=num_of_movies_limit)

  all_actors = {}

  for movie_tuple in movies_tuple_list:

    test_url_validity(movie_tuple[1])

    actors = get_actors_by_movie(movie_tuple[1], saved_movies, num_of_actors_limit=num_of_actors_limit)
    # if tar get actor found, return the path, if not we need to go deeper in all the movies in next level
    if target_actor_tuple in actors:
      full_path = path + '|' + movie_tuple[0] + '|' + movie_tuple[1] + '::' + target_actor_tuple[0] + '|' + target_actor_tuple[1]
      imdb_debug_log('found path between {0} {1} and {2} {3}, full path {4}'.format(start_actor_tuple[0], start_actor_tuple[1], \
                                                                                    target_actor_tuple[0], target_actor_tuple[1], full_path))
      return full_path

    all_actors[movie_tuple] = actors

  imdb_debug_log('going deeper into {0} movies of {1} {2}'.format(len(movies_tuple_list), start_actor_tuple[0], start_actor_tuple[1]))

  for movie_tulpe, actor_tuple_list in all_actors.items():
    for actor_tuple in actor_tuple_list:
        
      if actor_tuple == start_actor_tuple:
        continue

      result = search_actor_connection(actor_tuple, target_actor_tuple, \
                            path + '|' + movie_tulpe[0] + '|' + movie_tulpe[1] + '::' + actor_tuple[0] + '|' + actor_tuple[1], \
                            saved_actors=saved_actors, saved_movies=saved_movies,
                            max_depth=max_depth, num_of_actors_limit=num_of_actors_limit, num_of_movies_limit=num_of_movies_limit)

      if result:
        return result

  return None