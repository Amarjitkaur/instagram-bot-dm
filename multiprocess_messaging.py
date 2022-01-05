import multiprocessing
import random
import time
import sqlite3
import json
# from create_users_list import get_accounts_list_per_bot
from instadm import InstaDM

conn = sqlite3.connect('db/instabot.db')
cursor = conn.cursor()

message = """
Message to send...
"""

with open('bot_accounts.json', 'r') as bots_file:
    bot_accounts = json.load(bots_file)

with open('proxies_list.txt', 'r') as proxies_file:
    proxies = proxies_file.read().split('\n')
    proxies = [i for i in proxies if i]


def get_proxy():
    """
    return a random proxy from proxies list
    """
    return random.choice(proxies)


def task(val: dict) -> None:
    for bot, accounts in val.items():
        passowrd = [i.get('password')
                    for i in bot_accounts if i.get('username') == bot]
        print(
            bot, 'sending messages to {} accounts.'
            .format(accounts)
            )
        if len(passowrd) < 1:
            print("No password found. skipping process")
            return
        passowrd = passowrd[0]

        if len(accounts) < 1:
            print("No accounts to send message. skipping process")
            return

        insta = InstaDM(username=bot, password=passowrd, headless=False)
        for user in accounts:
            insta.sendMessage(user=user, message="hey")
        insta.teardown()


def get_follower(scraped_from: str = None) -> tuple:
    """scraped_from: IG username (To get followers of a specific ig account)"""
    """ return a follower and set status to sent """
    if scraped_from:
        cursor.execute("""
        SELECT username,id
        FROM followers
        WHERE scraped_from = ?
        AND message_sent = 0
        """, (scraped_from,))
    else:
        cursor.execute("""
        SELECT username,id from followers where message_sent = 0
        """)
    follower = cursor.fetchone()
    if follower:
        cursor.execute("""
        UPDATE followers SET message_sent = 1 WHERE id = ?
        """, (follower[1],))
        conn.commit()
    return follower


def send_msg(bot):
    """
    get a follower from db and send message to him
    """
    passowrd = [i.get('password')
                for i in bot_accounts if i.get('username') == bot]
    if len(passowrd) < 1:
        print("No password found for bot - {}. skipping process".format(bot))
        return
    passowrd = passowrd[0]
    proxy = get_proxy()
    if not proxy:
        print("No proxy found. skipping process for bot", bot)
        return
    insta = InstaDM(
        username=bot,
        password=passowrd,
        headless=False,
        proxy=proxy
        )
    message_sent = 0
    follower = get_follower()
    while follower:
        print("Bot - {} sending message to {}".format(bot, follower[0]))
        insta.sendMessage(user=follower[0], message="hey")
        message_sent += 1
        if message_sent >= 50:
            print(
                """####################
                Bot - {} has sent {} messages. updating proxy
                ####################"""
                .format(bot, message_sent))
            insta.teardown()
            send_msg(bot)
            break
        follower = get_follower()
    print("Stopping bot : ", bot)


if __name__ == '__main__':
    # usernames = get_usernames("onlyfans__followers.csv")
    # usernames = ["hardeep.io", "jain7_nd", "rajput__mandeep", "indr_preet__"]
    bots = [i.get('username') for i in bot_accounts]
    # accounts_lists = get_accounts_list_per_bot(usernames, bots)
    print('starting ==========')
    start = time.time()
    with multiprocessing.Pool(len(bots)) as p:
        p.map(send_msg, bots)
    print(time.time() - start)
