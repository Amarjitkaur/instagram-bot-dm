import os
import csv
from instadm import InstaDM
insta = InstaDM(username=os.getenv('username') ,password=os.getenv('password') , headless=False)

user = ''
res = insta.getFollowers(user=user, count=400)

fields = ['id','username'] # fields to add in csv file
data = [[i['pk'] , i['username']] for i in res[0]]
filename = user + '__followers.csv'
print('================== Writing followers to {} =================='.format(filename))
with open(filename , 'w', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(data)