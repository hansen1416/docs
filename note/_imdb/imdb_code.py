import logging
import os
import re
import sys

import numpy as np

# define helper functions if needed
# and put them in `imdb_helper_functions` module.
# you can import them and use here like that:
import imdb_helper_functions as helper

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)

def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
  """
  The function should return a list of all actors that played in the movie.
  An actor should be defined by such a pair: (name_of_actor, url_to_actor_page).
  So, the output of the function is expected to be the list of such pairs.
  """

  actor_list = []

  cast_list = cast_page_soup.find('table', attrs={'class':'cast_list'})

  if not cast_list:
    helper.imdb_debug_log('Can\'t find `cast_list` in soup')
    return actor_list

  title_casts = cast_list.find_all('tr', attrs={'class', re.compile(r'(odd|even)')})
  
  if (not title_casts or not len(title_casts)):
    helper.imdb_debug_log('Empty cast table')

  matched_count = 0
  
  for actor in title_casts:
    tds = actor.find_all('td')
    if len(tds) >= 4:
        
      if 'primary_photo' not in tds[0]['class']:
        helper.imdb_debug_log('Can\'t find `primary_photo` class in `td` 0')
        continue
      
      a = tds[1].find('a', href=True)
      if not a:
        helper.imdb_debug_log('Can\'t find `a` in `td`')
        continue
      
      actor_list.append((helper.imdb_strip_text(a.getText()), helper.imdb_join_link(a['href'])))
      
      matched_count += 1
      
      if num_of_actors_limit and matched_count >= num_of_actors_limit:
        break

  return actor_list


def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None, debug=False):
  """
  - The function should return only those movies, that have already been released.
  - Sometimes actors could be producers, or even directors, or something else. The function should return only those movies, 
    where the actor did an acting job. So, we should omit all the movies, where the actor has not actually played a role.
  - The function should return only full feature movies. So, it should omit other types of videos, 
    which are marked on imdb like that: TV Series, Short, Video Game, Video short, Video, TV Movie, TV Mini-Series, TV Series short and TV Special.
  """

  movies_list = []
  
  filmography = actor_page_soup.find('div', attrs={'id':'filmography'})
  
  if not filmography:
    helper.imdb_debug_log('Can\'t find `filmography` in soup')
    return movies_list
      
  filmo_sec = filmography.find('div', attrs={'class': 'filmo-category-section'})
  
  if not filmo_sec:
    helper.imdb_debug_log('Can\'t find `filmo-category-section` in soup')
    return movies_list

  movies_casts = filmo_sec.find_all('div', attrs={'class', re.compile(r'filmo-row (odd|even)')})

  if (not movies_casts or not len(movies_casts)):
    helper.imdb_debug_log('Empty movies list')

  matched_count = 0

  for movie in movies_casts:

    in_production = movie.find('a', attrs={'class': 'in_production'})
    #  movie in production
    if in_production:
      continue

    # match only released full feature movies
    if re.compile(r'\((pre\-production|post\-production|announced|TV Series|Short|Video Game|Video short|Video|TV Movie|TV Mini-Series|TV Series short|TV Special)').search(movie.getText()):
      continue

    a = movie.find('a', href=True)

    if not a:
      helper.imdb_debug_log('Can\'t find `a` in `filmo-row`')
      continue

    movies_list.append((helper.imdb_strip_text(a.getText()), helper.imdb_join_link(a['href'])))

    matched_count += 1

    if num_of_movies_limit and matched_count >= num_of_movies_limit:
      break

  return movies_list


def get_movie_distance(actor_start_url, actor_end_url, num_of_actors_limit=5, num_of_movies_limit=5):
  """
  - Set current_distance = 1
  - Start with some actor. Get the list of movies for the actor. Get the list of actors for those movies.
    Does a list contain an actor_end?
    If yes:
    return current_distance
    If no:
    Increase current_distance by 1
  - repeat step 2 for all actors, whose movie distance to actor_start is equal to current_distance-1
  - To avoid an infinite loop, we might want to set a limit. 
    For example, if current_distance is equal to 10, and we still have not find a connection between actor_start and actor_end, 
    let's assume that there is no connection between them.
  
  num_of_actors_limit: default 5
  num_of_movies_limit: default 5
  """

  actor_start_name = helper.get_actor_name_by_url(actor_start_url)
  assert actor_start_name, "can't find start actor's name by url {0}".format(actor_start_url)
  actor_end_name = helper.get_actor_name_by_url(actor_end_url)
  assert actor_end_name, "can't find end actor's name by url {0}".format(actor_end_url)
  # update to standard url
  name_url = helper.get_actor_url_by_name([actor_start_name, actor_end_name])

  start_tuple = (actor_start_name, name_url[actor_start_name])
  end_tuple = (actor_end_name, name_url[actor_end_name])

  seen_movies = {}
  # try to load saved movie info
  seen_movies_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/seen_movies.npy'
    
  if os.path.isfile(seen_movies_file):
    seen_movies = np.load(seen_movies_file, allow_pickle = True).item()

  seen_actors = {}
  # try to load saved actor info
  seen_actors_file = os.environ.get('IMDB_STORAGE_PATH', os.getcwd()) + '/seen_actors.npy'

  if os.path.isfile(seen_actors_file):
    seen_actors = np.load(seen_actors_file, allow_pickle = True).item()

  connection = helper.search_actor_connection(start_tuple, end_tuple, start_tuple[0] + '|' + start_tuple[1], saved_actors=seen_actors, saved_movies=seen_movies, \
                            max_depth=4, num_of_actors_limit=num_of_actors_limit, num_of_movies_limit=num_of_movies_limit)

  if connection:
    length = len(connection.split('::'))
    if length >= 3:
      return length - 2
    else:
      return length - 1
  else:
    return None

def get_movie_descriptions_by_actor_soup(actor_page_soup):
    # your code here
    return # your code here