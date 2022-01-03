import multiprocessing
import time
import json
from create_users_list import get_accounts_list_per_bot
from instadm import InstaDM

with open('bot_accounts.json', 'r') as bots_file:
    bot_accounts = json.load(bots_file) 


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
            insta.sendMessage(user=user, message="hey ")


if __name__ == '__main__':
    # usernames = get_usernames("onlyfans__followers.csv")
    usernames = ["hardeep.io", "jain7_nd", "rajput__mandeep", "indr_preet__"]
    bots = [i.get('username') for i in bot_accounts]
    accounts_lists = get_accounts_list_per_bot(usernames, bots)
    print('starting ==========')
    start = time.time()
    
    with multiprocessing.Pool(len(bot_accounts)) as p:
        p.map(task, accounts_lists)
    print(time.time() - start)
