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
            cast_list = []
            try:
                cast = movie['cast']
                counter = 3
                for actor in cast:
                    if counter == 0:
                        break
                    cast_list.append(actor)
                    counter -= 1
            except KeyError:
                cast = ''

            print(str(i + 1) + ". ", end="")
            print(f'{titles[i]} - {years[i]}')
            directStr = ', '.join(map(str, directors))
            print(f'Directors: {directStr}')
            castStr = ', '.join(map(str, cast_list))
            print(f'Starring: {castStr}')
        except IndexError:
            print("End of results.")
            break
    if len(titles) == 0:
        return
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

def remove(user, moviesDB, cur, cn):
    """
    Remove a movie from watched list and rankings
    :param user: user removing movie
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
            cast_list = []
            try:
                cast = movie['cast']
                counter = 3
                for actor in cast:
                    if counter == 0:
                        break
                    cast_list.append(actor)
                    counter -= 1
            except KeyError:
                cast = ''

            print(str(i + 1) + ". ", end="")
            print(f'{titles[i]} - {years[i]}')
            directStr = ', '.join(map(str, directors))
            print(f'Directors: {directStr}')
            castStr = ', '.join(map(str, cast_list))
            print(f'Starring: {castStr}')
        except IndexError:
            print("End of results.")
            break
    if len(titles) == 0:
        return
    print("Type '1', '2', or '3' to confirm a search result, or anything else to cancel. ")
    confirmation = input()
    if confirmation == '1' or confirmation == '2' or confirmation == '3':
        cur.execute("SELECT * FROM watch_lists WHERE movie_id = %s AND user = %s;", (movie_ids[int(confirmation)-1], user))
        duplicates = cur.fetchall()
        if len(duplicates) == 0:
            print("Movie not in watched list.")
            return
        cur.execute("DELETE FROM watch_lists WHERE movie_id = %s AND user = %s", (movie_ids[int(confirmation)-1], user))
        cur.execute("DELETE FROM rankings WHERE winner = %s AND user = %s", (movie_ids[int(confirmation)-1], user))
        cur.execute("DELETE FROM rankings WHERE loser = %s AND user = %s", (movie_ids[int(confirmation)-1], user))
        cn.commit()
        print(titles[int(confirmation)-1] + " has been removed your watched list")
    else:
        print("Cancelled removing " + titles[0] + " to your watch list")

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
    while True:
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
        user_pick = -1
        while not (user_pick == 0 or user_pick == 1 or user_pick == 2):
            user_pick = input(title1 + " (" + str(year1) + ") '1' vs " + title2 +
                          " (" + str(year2) + ") '2'. Type '1' or '2' for your favorite, or '0' to exit ranking. ")
            if user_pick.isdigit():
                user_pick = int(user_pick)
        if user_pick == 1:
            cur.execute("INSERT INTO rankings VALUES (%s, %s, %s);", (user, movie1, movie2))
            selected = title1
        elif user_pick == 2:
            cur.execute("INSERT INTO rankings VALUES (%s, %s, %s);", (user, movie2, movie1))
            selected = title2
        elif user_pick == 0:
            break
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

def top_cast(user, count, moviesDB, cur):
    print("Please wait...")
    appearances = dict()
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s;", (user,))
    movies = cur.fetchall()
    for movie in movies:
        try:
            cur_movie = moviesDB.get_movie(movie[0])
            cast = cur_movie['cast']
            for actor in cast:
                if actor not in appearances:
                    appearances[actor] = 1
                else:
                    appearances[actor] += 1
        except KeyError:
            pass
    ranked_actors = sorted(appearances.keys(), key=appearances.get, reverse=True)
    for actor in ranked_actors:
        if appearances[actor] < count:
            break
        print(appearances[actor], str(actor))

def top_directors(user, count, moviesDB, cur):
    print("Please wait...")
    counts = dict()
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s;", (user,))
    movies = cur.fetchall()
    for movie in movies:
        try:
            cur_movie = moviesDB.get_movie(movie[0])
            directors = cur_movie['director']
            for director in directors:
                if director not in counts:
                    counts[director] = 1
                else:
                    counts[director] += 1
        except KeyError:
            pass
    qualified_directors = dict() #directors who have enough movies in watched list
    for director in counts:
        if counts[director] >= count:
            qualified_directors[director] = [counts[director], 0]

    #go through top movies process
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s;", (user,))
    movies = cur.fetchall()
    movie_wins = dict()  # movie id points to number of wins
    movie_losses = dict()  # movie id points to number of losses
    movie_rankings = dict()  # movie id points to win%
    # count up wins and losses for each movie
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
    # calculate win% for each movie
    for movie in movies:
        try:
            movie_rankings[movie[0]] = movie_wins[movie[0]] / (movie_wins[movie[0]] + movie_losses[movie[0]])
        except ZeroDivisionError:
            movie_rankings[movie[0]] = 0
    movie_list = sorted(movie_wins.keys(), reverse=True, key=movie_wins.get)  # get movies sorted by win count
    movie_rankings_sorted = sorted(movie_rankings.keys(), reverse=True,
                                   key=movie_rankings.get)  # get movies sorted by win%
    movie_ranking_dict = dict()  # movie id points to movie score
    counter = 1
    for movie in movie_list:
        movie_ranking_dict[movie] = counter
        counter += 1
    counter = 1
    for movie in movie_rankings_sorted:
        movie_ranking_dict[movie] += counter
        counter += 1
    ranked_movies = sorted(movie_ranking_dict.keys(), key=movie_ranking_dict.get)  # final ranking
    i = 1
    for movie in ranked_movies:
        try:
            cur_movie = moviesDB.get_movie(movie)
            directors = cur_movie['director']
            for director in directors:
                if director in qualified_directors:
                    qualified_directors[director][1] += i
        except KeyError:
            pass
        i += 1
    print()
    final_rankings = dict()
    for director in qualified_directors:
        final_rankings[director] = qualified_directors[director][1] / qualified_directors[director][0]
    ranked_directors = sorted(final_rankings.keys(), key=final_rankings.get)
    for director in ranked_directors:
        print(qualified_directors[director][0], final_rankings[director], director)

    """
    ranked_directors = sorted(counts.keys(), key=counts.get, reverse=True)
    for director in ranked_directors:
        if counts[director] < count:
            break
        print(counts[director], str(director))
    """

def recommend(user, top, moviesDB, cur):
    cur.execute("SELECT movie_id FROM watch_lists WHERE user = %s;", (user,))
    movies = cur.fetchall()
    movie_wins = dict()  # movie id points to number of wins
    movie_losses = dict()  # movie id points to number of losses
    movie_rankings = dict()  # movie id points to win%
    # count up wins and losses for each movie
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
    # calculate win% for each movie
    for movie in movies:
        try:
            movie_rankings[movie[0]] = movie_wins[movie[0]] / (movie_wins[movie[0]] + movie_losses[movie[0]])
        except ZeroDivisionError:
            movie_rankings[movie[0]] = 0
    movie_list = sorted(movie_wins.keys(), reverse=True, key=movie_wins.get)  # get movies sorted by win count
    movie_rankings_sorted = sorted(movie_rankings.keys(), reverse=True,
                                   key=movie_rankings.get)  # get movies sorted by win%
    movie_ranking_dict = dict()  # movie id points to movie score
    counter = 1
    for movie in movie_list:
        movie_ranking_dict[movie] = counter
        counter += 1
    counter = 1
    for movie in movie_rankings_sorted:
        movie_ranking_dict[movie] += counter
        counter += 1
    ranked_movies = sorted(movie_ranking_dict.keys(), key=movie_ranking_dict.get)  # final ranking
    i = 1
    recommended = dict() #Dictionary of how recommended a movie is
    ia = imdb.IMDb()
    for movie in ranked_movies:
        if i > top:
            break
        current_movie = ia.get_movie(movie, info='recommendations')
        try:
            recommendations = current_movie['recommendations']
        except KeyError:
            recommendations = []
        for rec in recommendations:
            if rec in recommended:
                recommended[rec] += 1
            else:
                recommended[rec] = 1
        i += 1
    recommend_list = sorted(recommended.keys(), reverse=True, key=recommended.get)
    i = 20
    cur.execute("SELECT title FROM watch_lists WHERE user = %s;", (user,))
    id_list = cur.fetchall()
    ids = set()
    for id in id_list:
        ids.add(id[0])
    print("Here are suggestions for you.")
    for movie in recommend_list:
        if i == 0:
            break
        if movie['title'] not in ids:
            print(movie)
            i -= 1

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
        elif (command.lower() == 'rm') or (command.lower() == 'remove'):
            remove(user, moviesDB, cur, cn)
        elif (command.lower() == 't') or (command.lower() == 'top'):
            top = int(input("How many movies do you want to show? "))
            ranked_list(top, user, cur)
        elif (command.lower() == 's') or (command.lower() == 'sign out') or (command.lower() == 'signout'):
            user = input("Enter a username: ")
        elif (command.lower() == 'top cast') or (command.lower() == 'topcast') or (command.lower() == 'tc'):
            count = int(input("What minimum number of movies do you want the list to include?\n"))
            top_cast(user, count, moviesDB, cur)
        elif (command.lower() == 'top director') or (command.lower() == 'top directors') or \
                (command.lower() == 'topdirector') or (command.lower() == 'topdirectors') or (command.lower() == 'td'):
            count = int(input("What minimum number of movies do you want the list to include?\n"))
            top_directors(user, count, moviesDB, cur)
        elif command.lower() == 'rec':
            top = int(input("How many of your top movies would you like to be used? "))
            recommend(user, top, moviesDB, cur)

    cur.close()
    cn.close()

if __name__ == '__main__':
    main()