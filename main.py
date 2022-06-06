from datetime import date
from random import randint

import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists

URL = "https://fnbr.co/shop"
r = requests.get(URL)

# deletes some of the unwanted parts of the text and makes sure it is in unicode


def scrub(text):
    import string
    return ''.join(x for x in text if x in string.printable).strip()


soup = BeautifulSoup(r.content, 'html.parser')


items = soup.find_all("div", class_="items-row shop-items slosh-mode")

titles = soup.find_all("h2", class_="shop-section-title")
titles = [i.text for i in titles]

items_and_prices_concatenated = []

for i in items:
    # finds it and only takes the text
    item_names = i.find_all("h4", class_="item-name")
    item_names = [j.text for j in item_names]

    # finds it, takes only the text, scrubs text
    item_prices = i.find_all("p", class_="item-price")
    item_prices = [j.text for j in item_prices]
    item_prices = list(map(scrub, item_prices))

    # concatenates all the the names and prices side by side
    # concatenated = ""
    # for j, k in zip(item_names, item_prices):
    #     concatenated += f"{j}: {k}" + "\n"
    # sort the list alphabetically and then join it with newlines
    concatenated = ''.join(
        sorted([f"{j}: {k}" + "\n" for j, k in zip(item_names, item_prices)]))

    items_and_prices_concatenated.append(concatenated)


def embed_to_discord(titles, items_and_prices_concatenated):
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook with date
    date_today = date.today().strftime("%B %d, %Y")
    random_color = ["FFFFFF", "319236", "4C51F7", "9D4DBB", "F3AF19"]
    embed = DiscordEmbed(title="Fortnite Items - " +
                         date_today, color=random_color[randint(0, 4)])

    # take each title and match it with each of the related items and prices
    for j, k in zip(titles, items_and_prices_concatenated):
        embed.add_embed_field(name=j, value=k, inline=False)

    # set footer
    embed.set_footer(text='Made by Ibby With ❤️')

    # add embed object to webhook(s)
    webhook.add_embed(embed)
    webhook.execute()


def message_alert(find):
    # Webhooks to send to
    content = f"{find} Is In! <@265218135798448128>"
    allowed_mentions = {"users": ["265218135798448128"]}

    webhook = DiscordWebhook(url=env.list(
        "WEBHOOKS"), content=content, allowed_mentions=allowed_mentions)
    webhook.execute()


embed_to_discord(titles, items_and_prices_concatenated)

is_find_in = False
find = "Guff"
for i in items_and_prices_concatenated:
    if find in i:
        is_find_in = True
        break

if is_find_in:
    message_alert(find)
