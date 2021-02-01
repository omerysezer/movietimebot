import discord
import requests
import os
from bs4 import BeautifulSoup
from discord.ext import commands

bot = commands.Bot(command_prefix='++')
bot.remove_command("help")


@bot.event
async def on_ready():
    print('Ready')
    await bot.change_presence(activity=discord.Game(name="++help"))


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        color=discord.Color.blurple(),
        title="Command Help".title(),
        description='These are the available commands')

    embed.set_author(name='Movie Bot',
                     icon_url='https://cdn.discordapp.com/attachments/770330185782001715/800246769853136926/tenor.png')
    embed.set_thumbnail(
        url='https://cdn.discordapp.com/attachments/770330185782001715/800246769853136926/tenor.png')
    embed.add_field(
        name='Find all the showtimes for a movie on a certain date\nNOTE: date must be formatted as day/month/year, ex) 2/12/2020',
        value='++movietimes movie name - date \nex) ++movietimes Saving Private Ryan - 1/1/2021', inline=False)
    embed.add_field(name='Finds all the movies being shown on a certain date', value=';;movies date\nex) ++movies 1/1/2021', inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def movietimes(ctx, *, arg):
    if '-' in arg and '/' in arg:
        command = arg.split('-')
        movie = command[0].strip()
        date = command[1].strip()
        # gets the showtimes for a movie on that date
        # await date_converter(date)
        await ctx.channel.send(await get_movie_times(movie, date))
    else:
        await ctx.channel.send("That input is invalid. Make sure that your format it as \';;movietimes <movie name> - <movie date>\'")


@bot.command()
async def movies(ctx, movie_date):
    date = movie_date
    # await date_converter(date)
    await ctx.channel.send(await show_available_movies(date))


async def get_movie_times(movie_name, movie_date):
    # turns movie name into upper case, removes 'a','the', and leading and trailing spaces, and splits it based on
    # spaces
    movie = movie_name.upper().replace('A ', '').replace('THE ', '').replace(' A', '').replace(' THE', '').replace("'S",
    '').replace("'", '').replace("", '').strip().split(' ')

    date = movie_date
    # date format must be: month/day/year Ex) February 22nd, 2020 must be written as 2/22/2020
    url = 'https://www.showtimes.com/movie-theaters/blackstone-valley-14-cinema-de-lux-8377/?date=' + date
    times_search = requests.get(url)
    soup = BeautifulSoup(times_search.text, 'lxml')

    movie_containers = soup.findAll('div', attrs={'class': 'media-body'})

    titles = {}
    for container in movie_containers:
        title = container.find('a').string
        if title is None:
            continue
        else:
            titles.update({title.strip().upper(): movie_containers.index(container)})


    name_of_movie = titles.keys()
    key_of_movie = []

    # finds if the movie entered is in the dictionary and then gets the key of that movie in the dictionary
    for key in name_of_movie:
        key_split = key.replace(':', '').split(' ')

        for section in key_split:
            for word in movie:
                if word == section:
                    key_of_movie.append(key)

    # checks if there is more than one possible movie, and if so, prompts the user to try again
    if len(key_of_movie) > 1:
        possible_movies = ''
        for title in key_of_movie:
            possible_movies += (str(key_of_movie.index(title) + 1) + ': ' + title + '\n')
        return 'Multiple possible movies, try again and be more specific:\n' + possible_movies
    # checks that the bot could find a movie to check and if not, informs the user
    elif not key_of_movie:
        return 'Could not find that movie, please make sure that you have: \n' \
               'A) Spelled the movie name correctly\n' \
               'B) Have entered a movie that is going to be playing on ' + date + '\n--For a list of movies, please ' \
                                                                                  'enter !movies <date>'

    # if the preceding two checks against possible errors do not run, the program resumes normally

    key_of_movie = str(key_of_movie).replace('[\'', '').replace('\']', '')

    # var box is created to store the container of the movie found by the bot
    box = movie_containers[titles.get(key_of_movie)]

    # showtime_types stores the containers for each of the types of movie showings
    time_buttons = box.parent.parent.findAll('div', attrs={'class': 'ticketicons'})[0].findAll('a')
    # string to store the times the movie is being shown
    times = '\n'
    for button in time_buttons:
        times += button.string.strip() + '\n'

    movie_name = key_of_movie
    return 'The show times for ' + movie_name + ' on ' + movie_date + ' at Blackstone 14 Cinema De Lux are: ' + times


''' show_types = []
    for show_type in showtime_types:
        show_types.append(show_type.find('h3').contents[0])

    # dictionary to store the times for each of the types of showings
    movie_times_with_showtype = {}
    # list to store the times and be added to the dictionary

    # gets the time from the time_buttons, converts to string, and stores it in list movie_times
    # for loop to get fill the dictionary with the key of each type of movie showing and their times
    for show_type in show_types:  # iterates through the types of movie showings
        movie_times = []  # clears the list for the next iteration
        # stores all the buttons which store the tags which store the times of that movie showing
        time_buttons = showtime_types[show_types.index(show_type)].findAll('a')
        for button in time_buttons:  # iterates through the tags that store times
            movie_times.append(button.string)  # gets time from the tag as a string and appends it to the list of times

        movie_times_with_showtype.update({show_type: movie_times})  # updates the dictionary with the movie type and the times for that movie type

    killme = 'The times for ' + fukingmoviename + ' on ' + movie_date + ' are:\n'
    for key in show_types:
        shootme = movie_times_with_showtype.get(key)
        death = '\n'
        for x in shootme:
            death += death + '\n'
        killme += '\n' + key + ':' + death  # FIGURE THIS OUT DUMBASS

    return y'''


async def show_available_movies(date_param):
    date = date_param
    # date format must be: month/day/year Ex) February 22nd, 2020 must be written as 2/22/2020
    url = 'https://www.showtimes.com/movie-theaters/blackstone-valley-14-cinema-de-lux-8377/?date=' + date
    times_search = requests.get(url)
    soup = BeautifulSoup(times_search.text, 'lxml')

    movie_containers = soup.findAll('div', attrs={'class': 'media-body'})

    titles = {}
    for container in movie_containers:
        title = container.find('h2').find('a')
        if title is None:
            continue
        else:
            title = title.string
            titles.update({movie_containers.index(container): title.strip().upper()})

    movies = titles.keys()

    if not movies:
        return "No movies are available on " + date

    available_movies = 'Movies showing at Blackstone 14 Cinema de Lux theater on ' + date + ':\n'
    for movie in movies:
        available_movies += str(movie + 1) + ':    ' + titles[movie] + '\n'

    return available_movies


async def date_converter(entered_date):
    date = entered_date


bot.run(os.environ['DISCORD_TOKEN'])
