import requests
import json
get_data=requests.get("http://www.theimdbapi.org/api/find/person?name=jim+carrey")
movie_data=json.loads(get_data.text)

for i in range(0,50):
    print(movie_data[0]['filmography']['actor'][i]['title'])
# for data in movie_data[0]:
#     print(data)


#
# # create and instance of the IMDb class
# from imdb import IMDb
# ia = IMDb()
#
# # get a movie and print its director(s)
# the_matrix = ia.get_movie('0133093')
# print(the_matrix['actors'])
#
# # show all the information sets avaiable for Movie objects
# print(ia.get_movie_infoset())
#
# # update a Movie object with more information
# ia.update(the_matrix, ['technical'])
# # show which keys were added by the information set
# print(the_matrix.infoset2keys['technical'])
# # print one of the new keys
# print(the_matrix.get('cinematographic process'))
#
# # search for a person
# for person in ia.search_person('Mel Gibson'):
#     print(person.personID, person['name'])
#     # update it to get the basic information
#     ladd_company = ia.search_company('The Ladd Company')[0]
#     ia.update(ladd_company)
#     # show the available information and print some
#     print(ladd_company.keys())
#     print(ladd_company.get('production companies'))
#
# #get the first result of a company search,
#
# #get 5 movies tagged with a keyword
# dystopia = ia.get_keyword('dystopia', results=5)
# print(dystopia)
# # get a Character object
# deckard = ia.search_character('Rick Deckard')[0]
# ia.update(deckard)
# print(deckard['full-size headshot'])
#
# #get top250 and bottom100 movies
# top250 = ia.get_top250_movies()
# print(top250)
# bottom100 = ia.get_bottom100_movies()