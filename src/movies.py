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

    print('Top results info: ')
    movie_ids = []
    titles = []
    years = []

    for i in range (0,3):
        try:
            movie_ids.append(movies[i].getID())
            movie = moviesDB.get_movie(movie_ids[i])
            titles.append(movie['title'])
            try:
                years.append(movie['year'])
            except KeyError:
                year = 0
            try:
                directors = movie['directors']
            except KeyError:
                directors = ''

            print(str(i + 1) + ". ", end="")
            print(f'{titles[i]} - {years[i]}')
            directStr = ' '.join(map(str, directors))
            print(f'directors: {directStr}')
        except IndexError:
            print("No movies found.")
            break
    print("Type '1', '2', or '3' to confirm a search result, or anything else to cancel. ")
    confirmation = input()
    if confirmation == '1' or confirmation == '2' or confirmation == '3':
        cur.execute("SELECT * FROM watch_lists WHERE movie_id = %s AND user = %s;", (movie_ids[int(confirmation)-1], user))
        duplicates = cur.fetchall()
        if len(duplicates) > 0:
            print("Movie already in watched list.")
            return
        cur.execute("INSERT INTO watch_lists VALUES (%s, %s, %s, %s);", (user, movie_ids[int(confirmation)-1],
                                                                         titles[int(confirmation)-1], years[int(confirmation)-1]))
        cn.commit()
        print(titles[int(confirmation)-1] + " has been added to your watched list")
    else:
        print("Cancelled adding " + titles[0] + " to your watch list")

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
        user_pick = input(title1 + " (" + str(year1) + ") '1' vs " + title2 +
                      " (" + str(year2) + ") '2'. Type '1' or '2' for your favorite. ")
        if user_pick.isdigit():
            user_pick = int(user_pick)
    if user_pick == 1:
        cur.execute("INSERT INTO rankings VALUES (%s, %s, %s);", (user, movie1, movie2))
        selected = title1
    else:
        cur.execute("INSERT INTO rankings VALUES (%s, %s, %s);", (user, movie2, movie1))
        selected = title2
    print(selected, "is the winner!")
    cn.commit()

def ranked_list(top, user, cur):
    """
    Prints the ranked list of movies user has watched
    The formula works as follows:
    1. Rank movies by win count in one list
    2. Rank movies by win% in one list
    Rank movies by sum of their position on 1 and position on 2
    This means that both having lots of votes and a good percentage matter.
    The intention is that recently movies aren't penalized too much, but don't jump straight to the top either.
    :param top: number of top movies to print
    :param user: user's list to print
    :param cur: database cursor
    :return: none
    """
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s;", (user,))
    movies = cur.fetchall()
    movie_wins = dict() #movie id points to number of wins
    movie_losses = dict() #movie id points to number of losses
    movie_rankings = dict() #movie id points to win%
    #count up wins and losses for each movie
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
    #calculate win% for each movie
    for movie in movies:
        try:
            movie_rankings[movie[0]] = movie_wins[movie[0]] / (movie_wins[movie[0]] + movie_losses[movie[0]])
        except ZeroDivisionError:
            movie_rankings[movie[0]] = 0
    movie_list = sorted(movie_wins.keys(), reverse=True, key=movie_wins.get) #get movies sorted by win count
    movie_rankings_sorted = sorted(movie_rankings.keys(), reverse=True, key=movie_rankings.get) #get movies sorted by win%
    movie_ranking_dict = dict() #movie id points to movie score
    counter = 1
    for movie in movie_list:
        movie_ranking_dict[movie] = counter
        counter += 1
    counter = 1
    for movie in movie_rankings_sorted:
        movie_ranking_dict[movie] += counter
        counter += 1
    ranked_movies = sorted(movie_ranking_dict.keys(), key=movie_ranking_dict.get) #final ranking
    i = 1
    for movie in ranked_movies:
        if i > top:
            break
        cur.execute("SELECT title FROM watch_lists WHERE movie_id = %s;", (movie,))
        title = cur.fetchall()[0][0]
        print(str(i) + ". " + title)
        i += 1


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
            print("'sign out' or 's': Sign out")
            print("'top' or 't': Print your top movies")
        if (command.lower() == 'l') or (command.lower() == 'list'):
            watched(user, cur)
        elif (command.lower() == 'q') or (command.lower() == 'quit'):
            break
        elif (command.lower() == 'r') or (command.lower() == 'rank'):
            rank(user, cur, cn)
        elif (command.lower() == 't') or (command.lower() == 'top'):
            top = int(input("How many movies do you want to show? "))
            ranked_list(top, user, cur)
        elif (command.lower() == 's') or (command.lower() == 'sign out') or (command.lower() == 'signout'):
            user = input("Enter a username: ")

    cur.close()
    cn.close()

if __name__ == '__main__':
    main()