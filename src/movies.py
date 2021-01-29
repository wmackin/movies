"""
Sign in as user and manage your personal movie list. You can add movies to your watched list, and view the list.

@author: wmackin
"""

import imdb
import mysql.connector

def combinations(number):
    """
    Determines the number of matchup combinations possible from a number of movies
    :param number: movie count
    :return: number of combinations
    """
    result = 0
    for i in range(1, number):
        result += i
    return result

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
    try:
        year = movie['year']
    except KeyError:
        year = 0
    try:
        directors = movie['directors']
    except KeyError:
        directors = ''

    print('Top result info: ')
    print(f'{title} - {year}')
    directStr = ' '.join(map(str, directors))
    print(f'directors: {directStr}')
    print("Type '1' to confirm")
    confirmation = input()
    if confirmation == '1':
        cur.execute("INSERT INTO watch_lists VALUES (%s, %s, %s, %s);", (user, movie_id, title, year))
        cn.commit()
        print(title + " has been added to your watched list")
    else:
        print("Cancelled adding " + title + " to your watch list")

def watched(user, cur):
    """
    Prints watched list of user
    :param user: user adding movie
    :param cur: mySQL cur
    :return: None
    """
    print("Here is every movie you have seen:")
    cur.execute("SELECT title FROM watch_lists WHERE user = %s;", (user,))
    titles = cur.fetchall()
    print(titles)
    for movie in titles:
        print(movie[0])

def get_random_movie(user, cur):
    """
    Gets a random movie that the user has seen
    :param user:
    :param cur:
    :return:
    """
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s ORDER BY RAND();", (user,))
    movie = cur.fetchall()[0][0]
    cur.execute("SELECT title FROM watch_lists WHERE movie_id = %s AND user = %s;", (movie, user))
    title = cur.fetchone()[0]
    cur.execute("SELECT year FROM watch_lists WHERE movie_id = %s AND user = %s;;", (movie, user))
    year = cur.fetchone()[0]
    return movie, title, year

def rank(user, cur, cn):
    """
    Give two random movies for the user to rank
    :param user: user ranking movies
    :param cur: database cursor
    :param cn: database connection
    :return:
    """
    cur.execute("SELECT COUNT(*) FROM watch_lists WHERE user = %s;", (user,))
    movie_count = cur.fetchall()[0][0]
    cur.execute("SELECT COUNT(*) FROM rankings WHERE user = %s;", (user,))
    rank_count = cur.fetchall()[0][0]
    if combinations(movie_count) == rank_count:
        print("No more movies to rank.")
        return
    while True:
        cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s ORDER BY RAND();", (user,))
        movie1, title1, year1 = get_random_movie(user, cur)
        movie2, title2, year2 = get_random_movie(user, cur)
        cur.execute("SELECT * FROM rankings WHERE winner = %s AND loser = %s AND user = %s;", (movie1, movie2, user))
        matches1 = cur.fetchall()
        cur.execute("SELECT * FROM rankings WHERE winner = %s AND loser = %s AND user = %s;", (movie2, movie1, user))
        matches2 = cur.fetchall()
        if len(matches1) == 0 and len(matches2) == 0 and movie1 != movie2:
            break
    user_pick = 0
    while not (user_pick == 1 or user_pick == 2):
        user_pick = int(input(title1 + " (" + str(year1) + ") '1' vs " + title2 +
                      " (" + str(year2) + ") '2'. Type '1' or '2' for your favorite. "))
        print(user_pick)
    if user_pick == 1:
        cur.execute("INSERT INTO rankings VALUES (%s, %s, %s);", (user, movie1, movie2))
    else:
        cur.execute("INSERT INTO rankings VALUES (%s, %s, %s);", (user, movie2, movie1))
    print("Choice", user_pick, "is the winner!")
    cn.commit()

def ranked_list(user, cur):
    """
    Prints the ranked list of movies user has watched
    :param user: user's list to print
    :param cur: database cursor
    :return: none
    """
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s;", (user,))
    movies = cur.fetchall()
    movie_wins = dict()
    movie_losses = dict()
    movie_rankings = dict()
    for movie in movies:
        movie_wins[movie[0]] = 0
        movie_losses[movie[0]] = 0
    cur.execute("SELECT winner FROM rankings WHERE user = %s;", (user,))
    winners = cur.fetchall()
    for winner in winners:
        movie_wins[winner[0]] += 1
    cur.execute("SELECT loser FROM rankings WHERE user = %s;", (user,))
    losers = cur.fetchall()
    for loser in losers:
        movie_losses[loser[0]] += 1
    for movie in movies:
        try:
            movie_rankings[movie[0]] = movie_wins[movie[0]] / (movie_wins[movie[0]] + movie_losses[movie[0]])
        except ZeroDivisionError:
            movie_rankings[movie[0]] = 0
    movie_list = sorted(movie_rankings.keys(), reverse=True, key=movie_rankings.get)
    for movie in movie_list:
        cur.execute("SELECT title FROM watch_lists WHERE movie_id = %s;", (movie,))
        title = cur.fetchall()[0][0]
        print(title)


def main():
    """
    Continually loops commands after a username is entered until exit command is entered.
    :return: none
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
    cur = cn.cursor(buffered=True)

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
            print("'quit' or 'q': Quit program")
            print("'rank' or 'r': Rank movies")
            print("'top' or 't': Print your top movies")
        if (command.lower() == 'l') or (command.lower() == 'list'):
            watched(user, cur)
        if (command.lower() == 'q') or (command.lower() == 'quit'):
            break
        if (command.lower() == 'r') or (command.lower() == 'rank'):
            rank(user, cur, cn)
        if (command.lower() == 't') or (command.lower() == 'top'):
            ranked_list(user, cur)

    cur.close()
    cn.close()

if __name__ == '__main__':
    main()