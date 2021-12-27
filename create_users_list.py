import csv
from decimal import Decimal, ROUND_HALF_UP

# Types
AccountsPerBot = list[dict]


def get_usernames(csv_path: str) -> list:
    ''' csv file should have two columns
        first for user id and second for
        username'''
    with open(csv_path, 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        usernames = [i[1] for i in csv_reader]
        usernames.pop(0)  # remove username header
    return usernames


def get_accounts_per_bot(total_users: int, total_bots: int) -> int:
    ''' returns number of accounts that can be devided into bots'''
    return int(Decimal(total_users / total_bots).quantize(0, ROUND_HALF_UP))


def get_accounts_list_per_bot(
        usernames: list,
        bot_accounts: list) -> AccountsPerBot:
    '''return list of dicts where each bot will be assigned
        list of equal number of accounts to which that will
        be responsible to send messages
        after iterating result: [
            {"bot1":['acc1','acc2']},
            {"bot2":['acc3','acc4']},
        ]'''
    if len(bot_accounts) < 1:
        return []
    k, m = divmod(len(usernames), len(bot_accounts))
    return (
            {bot_accounts[i]: usernames[i*k+min(i, m): (i+1)*k+min(i+1, m)]}
            for i in range(len(bot_accounts))
            )

# with open('bot_accounts.json', 'r') as bots_file:
#     bot_accounts = [i.get('username') for i in json.load(bots_file)]

# usernames = get_usernames('onlyfans__followers.csv')
# accounst_list = get_accounts_list_per_bot(usernames , bot_accounts)
# for i in accounst_list:
#     print(i ,'\n\n')
# total_bots = 6
# usernames = get_usernames('onlyfans__followers.csv')
# # accounts_per_bot = get_accounts_per_bot(len(usernames) , total_bots)
# accounts_lists = get_accounts_lists(usernames , total_bots )
# # print(accounts_lists.__next__())
# # print(next(accounts_lists))
# for i in accounts_lists:
#     print(i , '\n\n')
