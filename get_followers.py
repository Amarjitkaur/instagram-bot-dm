import time
import os
import csv
from instadm import InstaDM

start_time = time.time()
insta = InstaDM(username=os.getenv('username') ,password=os.getenv('password') , headless=False)

user = 'onlyfans'
count = 10000
res,max_id = insta.getFollowers(user=user, count=count)

followers = res
next_max_id = max_id
error_count = 0
call_no = 1
max_error_count = 50
while next_max_id:
    if error_count == max_error_count:
        break
    res = insta.getFollowers(user=user, count=count , max_id=next_max_id)
    if res:
        print("Scrapped {} followers. current call no. {}. Errors count {}".format(len(res[0]) ,call_no , error_count ))
        next_max_id = res[1]
        followers.extend(res[0])
        call_no += 1
    else:
        error_count += 1

fields = ['id','username'] # fields to add in csv file
rows = [[i['pk'] , i['username']] for i in followers if not i['is_verified']] # filtering non verified users
filename = user + '__followers.csv'
print('================== Writing followers to {} =================='.format(filename))
with open(filename , 'w', encoding='utf-8' , newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(rows)

print("Fetched {} followers in {} seconds".format(len(followers) , time.time() - start_time))