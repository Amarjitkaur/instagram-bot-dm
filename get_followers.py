import time
import sqlite3
from instadm import InstaDM

conn = sqlite3.connect('db/instabot.db')
cursor = conn.cursor()


def get_followers(username: str, password: str, user: str, count: int = 1000,
                  headless: bool = True, max_error_count: int = 5,
                  max_id='', proxy=None) -> str:
    '''
    --- get followers and save to db ---
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
        headless=headless,
        proxy=proxy
        )
    res = insta.getFollowers(user=user, max_id=max_id)
    if res:
        fetched_followers = len(res[0][:count])
        next_max_id = res[1]
    else:
        print(res)
        return
    for i in res[0][:count]:
        try:
            cursor.execute("""
            INSERT INTO followers(username, scraped_from)
            VALUES(?,?)
            """, (i.get('username'), user))
        except Exception as e:
            print(e, i.get('username'))
    conn.commit()
    error_count = 0
    call_no = 1
    print(">>>>>>>>>>>>>>>>> next_max_id:", next_max_id)
    while next_max_id and fetched_followers < count:
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
            for i in res[0][:count]:
                try:
                    cursor.execute("""
                    INSERT INTO followers(username, scraped_from)
                    VALUES(?,?)
                    """, (i.get('username'), user))
                except Exception as e:
                    print(e, i.get('username'))
            conn.commit()

            next_max_id = res[1]
            fetched_followers += len(res[0][:count])
            call_no += 1
            print(">>>>>>>>>>>>>>>>> next_max_id:", next_max_id)
        else:
            error_count += 1

    print(
        "Fetched {} followers in {} seconds"
        .format(
            fetched_followers,
            time.time() - start_time
            )
        )
    insta.teardown()
    # return filename
