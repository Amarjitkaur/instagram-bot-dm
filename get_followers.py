import time
import csv
from instadm import InstaDM


def get_followers(username: str, password: str, user: str, count: int = 1000,
                  headless: bool = True, max_error_count: int = 5) -> str:
    '''
    username = username for authentication
    password = password for authentication
    user = account to scrap data from
    count = number of followers to scrap
    headless = chromedriver headless option
    max_error_count = number of times to ignore error while fetching followers
    '''
    start_time = time.time()
    insta = InstaDM(
        username=username,
        password=password,
        headless=headless
        )
    res = insta.getFollowers(user=user)
    if res:
        followers = res[0][:count]
        next_max_id = res[1]
    else:
        print(res)
        return
    error_count = 0
    call_no = 1
    while next_max_id and len(followers) < count:
        if error_count == max_error_count:
            break
        res = insta.getFollowers(user=user, max_id=next_max_id)
        if res:
            print(
                "Scrapped {} followers. current call no. {}. Errors count {}"
                .format(
                    len(res[0]),
                    call_no,
                    error_count)
                )
            next_max_id = res[1]
            followers.extend(res[0][:count])
            call_no += 1
        else:
            error_count += 1

    fields = ['id', 'username']  # fields to add in csv file
    rows = [
        [i['pk'], i['username']] for i in followers if not i['is_verified']
        ]
    filename = user + '__followers.csv'
    print('Writing followers to {}'.format(filename))
    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)

    print(
        "Fetched {} followers in {} seconds"
        .format(
            len(followers),
            time.time() - start_time
            )
        )
    insta.teardown()
    return filename
