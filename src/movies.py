import imdb

user = input("Enter a username: ")

moviesDB = imdb.IMDb()


def add():
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
        file = open(user + '.txt', 'a')
        file.write(movie_id + '\n')
        print(title + " has been added to your watched list")
        file.close()
    else:
        print("Cancelled adding " + title + "to your watch list")

def watched():
    print("Here is every movie you have seen:")
    file = open(user + '.txt', 'r')
    for line in file:
        movie = moviesDB.get_movie(line)
        title = movie['title']
        print(title)
    file.close()

while True:
    command = input("Enter a command or 'help' for help: ")
    if (command.lower() == 'a') or (command.lower() == 'add'):
        add()
    if (command.lower() == 'h') or (command.lower() == 'help'):
        print("'add' or 'a': Add movie to watched list")
        print("'help' or 'h': Open help menu")
        print("'list' or 'l': Print watched list")
        print("'quit' or q: Quit program")
    if (command.lower() == 'l') or (command.lower() == 'list'):
        watched()
    if (command.lower() == 'q') or (command.lower() == 'quit'):
        break