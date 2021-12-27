import os
import time
from instadm import InstaDM

start_login = time.time()
insta = InstaDM(
    username=os.getenv('username'),
    password=os.getenv('password'),
    headless=False
    )
print("Time to login = ", time.time() - start_login)
users = ['hardeep.io', 'indr_preet__']
start_send = time.time()
for user in users:
    insta.sendMessage(user=user, message='hello !!')
# for user in users:
#     insta.sendMessage(user=user , message='hey')

print("Time to send = ", time.time() - start_send)
