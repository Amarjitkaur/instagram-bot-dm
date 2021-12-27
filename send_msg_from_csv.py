import csv
from time import time
from instadm import InstaDM
import os

csv_path = r'''D:\Day Shift\Jaspreet singh\Current Projects\python\instabot\
    project_files\instabot\instagram-bot-dm\send_msg.csv'''
with open(csv_path, 'r') as f:
    csv_reader = csv.reader(f, delimiter=',')
    usernames = [i[1] for i in csv_reader]
    usernames.pop(0)

test_users = usernames
group_size = 2
i = 0
groups = []
while i < len(test_users):
    # print(test_users[i:i+group_size])
    groups.append(test_users[i:i+group_size])
    i += group_size

print(groups)
print(int(len(usernames) / group_size))
start_login = time()
insta = InstaDM(
    username=os.getenv('username'),
    password=os.getenv('password'),
    headless=False
    )
print("Time to login : ", time() - start_login)
start_msg = time()
for group in groups:
    insta.sendGroupMessage(users=group, message='hello !!!')

print("Total to message : ", time() - start_msg)
