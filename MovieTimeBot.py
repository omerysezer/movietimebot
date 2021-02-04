import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from fuzzywuzzy import process
from dateutil.parser import parse
import os

bot = commands.Bot(command_prefix='++')
bot.remove_command("help")


def is_date(date):
    try:
        parse(date)
        return True
    except:
        return False


def convert_date(date):
    # converts the date into mm/dd/yyyy
    # if unable to convert to mm/dd/
    try:
        converted_date = parse(date).strftime("%m/%d/%Y")
        return converted_date
    except:
        print("MISSION FAILED")
        return date


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
    embed.add_field(name='Finds all the movies being shown on a certain date',
                    value='++movies date\nex) ++movies 1/1/2021', inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def movietimes(ctx, *, arg):
    if '-' in arg:
        command = arg.split('-')
        movie = command[0].strip()
        date = command[1].strip()

        if not (is_date(date)):
            await ctx.channel.send("That input is invalid. Make sure that you enter a date in a proper format. "
                                   "The best format to use is mm/dd/yy but most formats will work")
        else:
            # sends a message containing all the times for that movie on that date
            date = convert_date(date)
            await ctx.channel.send(await get_movie_times(movie, date) +
                                   "\nIf " + str(date) + " was not the correct date you wanted, please enter the date in the "
                                                    "mm/dd/yyyy format to ensure I get it right next time")


@bot.command()
async def movies(ctx, movie_date):
    date = movie_date
    if not (is_date(date)):
        await ctx.channel.send("That input is invalid. Make sure that you enter a date in a proper format. "
                               "The best format to use is mm/dd/yy but most formats will work however")
    else:
        date = convert_date(date)
        await ctx.channel.send(await show_available_movies(date) +
                               "\nIf " + str(date) + " was not the correct date you wanted, please enter the date in the "
                                                "mm/dd/yyyy format to ensure I get it right next time")


async def get_movie_times(movie_name, movie_date):
    # turns movie name into upper case, removes 'a','the', and leading and trailing spaces, and splits it based on
    # spaces
    movie = movie_name

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
            titles.update({title.strip(): movie_containers.index(container)})

    name_of_movie = list(titles.keys())

    key_of_movie_confidence_level = process.extractOne(movie, name_of_movie)[1]

    if key_of_movie_confidence_level < 80:
        return 'Could not find that movie, please make sure that you have: \n' \
               'A) Spelled the movie name somewhat correctly (obviously i cant find "Saving Private Ryan" if you typed "I jizzed my pants"\n' \
               'B) Have entered a movie that is going to be playing on ' + date + '\n--For a list of movies, please ' \
                                                                                  'enter !movies <date>'
    else:
        key_of_movie = process.extractOne(movie, name_of_movie)[0]

    # var box is created to store the container of the movie found by the bot
    box = movie_containers[titles.get(key_of_movie)]

    # showtime_types stores the containers for each of the types of movie showings
    time_buttons = box.parent.parent.findAll('div', attrs={'class': 'ticketicons'})[0].findAll('a')
    # string to store the times the movie is being shown
    times = '\n'
    if len(time_buttons) > 0:
        for button in time_buttons:
            times += button.string.strip() + '\n'
    else:
        return 'There are no showings of ' + key_of_movie + ' on ' + date + ' at Blackstone 14 Cinema De Lux'

    if len(times) > 0:
        return 'The show times for \"' + key_of_movie + '\" on ' + movie_date + ' at Blackstone 14 Cinema De Lux are: ' + times
    else:
        return 'There are no show times for \"' + key_of_movie + '\" on ' + movie_date + ' at Blackstone 14 Cinema De Lux'


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


bot.run(os.environ['DISCORD_TOKEN'])
