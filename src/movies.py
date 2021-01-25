"""
Sign in as user and manage your personal movie list. You can add movies to your watched list, and view the list.

@author: wmackin
"""

import imdb
import mysql.connector

def add(user, moviesDB, cur, cn):
    """
    Add a movie to watched list
    :param user: user adding movie
    :param moviesDB: movie database
    :param cur: mySQL cur
    :param cn: database connection
    :return: None
    """
    movies = moviesDB.search_movie(input("Enter a movie: "))

    print('Searching...')

    movie_id = movies[0].getID()
    movie = moviesDB.get_movie(movie_id)
    title = movie['title']
    year = movie['year']
    rating = movie['rating']
    directors = movie['directors']

    print('Top result info: ')
    print(f'{title} - {year}')
    print(f'rating: {rating}')
    directStr = ' '.join(map(str, directors))
    print(f'directors: {directStr}')
    print("Type '1' to confirm")
    confirmation = input()
    if confirmation == '1':
        cur.execute("INSERT INTO watch_lists VALUES (%s, %s, %s);", (user, movie_id, title))
        cn.commit()
        print(title + " has been added to your watched list")
    else:
        print("Cancelled adding " + title + "to your watch list")

def watched(user, moviesDB, cur, cn):
    """
    Prints watched list of user
    :param user: user adding movie
    :param moviesDB: movie database
    :param cur: mySQL cur
    :param cn: database connection
    :return: None
    """
    print("Here is every movie you have seen:")
    cur.execute("SELECT title FROM watch_lists WHERE user = %s;", (user,))
    titles = cur.fetchall()
    print(titles)
    for movie in titles:
        print(movie[0])

def main():
    """
    Continually loops commands after a username is entered until exit command is entered.
    :return:
    """

    config = {
        'user': 'root',
        'password': 'password',
        'host': 'localhost',
        'database': 'movies',
        'port': 3306,
        'raise_on_warnings': True
    }
    cn = mysql.connector.connect(**config)
    cur = cn.cursor()

    user = input("Enter a username: ")

    moviesDB = imdb.IMDb()
    while True:
        command = input("Enter a command or 'help' for help: ")
        if (command.lower() == 'a') or (command.lower() == 'add'):
            add(user, moviesDB, cur, cn)
        if (command.lower() == 'h') or (command.lower() == 'help'):
            print("'add' or 'a': Add movie to watched list")
            print("'help' or 'h': Open help menu")
            print("'list' or 'l': Print watched list")
            print("'quit' or q: Quit program")
        if (command.lower() == 'l') or (command.lower() == 'list'):
            watched(user, moviesDB, cur, cn)
        if (command.lower() == 'q') or (command.lower() == 'quit'):
            break

    cur.close()
    cn.close()

if __name__ == '__main__':
    main()