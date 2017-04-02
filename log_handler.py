# coding=utf-8
import time
from tweepy import TweepError
from logscrape import DNSReader, LogFileReader
from constants.twitter_account_pool import account_pool

from collections import deque
from urllib.parse import urlparse
import asyncio

# reader = DNSReader("/root/app-log")
reader = DNSReader("/mnt/sda1/app/app.log")
reader.clear_lines()

tweet_queue = deque()

# @app.route("/post_tweet", methods=['POST'])
# def post_tweet():
#     body = request.get_json(force=True)
#     msg = body.get('message')
#
#     msg.replace('.', '.​')
#
#     try:
#         api.update_status(msg)
#     except:
#         return jsonify({"Result": "Failure"})
#     return jsonify({"Result": "Success"})
#
# # def get_tweets():
#     public_tweets = api.user_timeline()
#     for t in public_tweets:
#         print(t.text)

suppressed_domains_dict = {}

def suppress_uber_domains(tweet):
    for s in [
        "uber",
        "carbonblack",
        "twitter",
        "127.0.0.1",
        "nick",
        "siddharth",
        ".den"
    ]:
        if s in tweet:
            return True

    return False


def post_tweet():
    twitter_account = None
    for a in account_pool:
        if a.is_disabled == False:
            twitter_account = a
            break

    if not twitter_account:
        print("No twitter account available, deferring")
        time.sleep(10)
        return

    try:
        t = tweet_queue.popleft()
    except IndexError:
        return

    # if suppress_uber_domains(t):
    #     print("Dropping tweet: {}".format(t))
    #     return

    try:
        a.api.update_status(t)
        print("Posted tweet: {}".format(t))
    except TweepError as e:
        if e.api_code in [187, 354]:
            print("Dropping tweet: {}".format(t))
            return
        elif e.api_code in [185, 226, 326]:
            print("Deferring tweet due to account lockdown: {}".format(t))
            a.is_disabled = True
            a.was_disabled_at = time.time()
            tweet_queue.appendleft(t)
        else:
            return


# global iter
# iter = 0
#
# def read_log_events():
#     global iter
#
#     if iter == 0:
#         tweet_queue.append("domain1.com")
#     if iter == 1:
#         tweet_queue.append("domain2.com")
#     if iter == 2:
#         tweet_queue.append("domain3.com")
#
#     iter += 1
#     return


# def read_log_events(file_where):

def restore_api_access():
    for a in account_pool:
        if a.is_disabled and time.time() - a.was_disabled_at > 300:
            a.is_disabled = False
    return


def generate_tweet_string(domain_regex_match, src_ip):
    if not suppress_uber_domains(domain_regex_match) and src_ip != "127.0.0.1":

        if "co.uk" in domain_regex_match:
            dom_string = ".".join(domain_regex_match.split(".")[-3:])
        else:
            dom_string = ".".join(domain_regex_match.split(".")[-2:])

        if "." in dom_string:
            # if suppressed_domains_dict.get(dom_string) is None:
            #     pass
            # elif suppressed_domains_dict.get(dom_string) <= 900:
            #     return None

            suppressed_domains_dict[dom_string] = time.time()
            return "{} visited {}".format(src_ip, dom_string)
        else:
            return None


def event_loop():
    while True:
        # print("Read_Log_Events")
        lines = reader.parse_new_lines()
        # List of tuples [(dom_name, src_ip)]
        if len(lines) > 0:
            print(lines)
        for (d, src) in lines:
            str = generate_tweet_string(d, src)
            if str is not None:
                tweet_queue.append(str)

        # print("Post_Tweet")
        post_tweet()
        # print("Restore_API_ACCESS")
        restore_api_access()
        time.sleep(1)


# loop = asyncio.get_event_loop()
# loop.run_until_complete(event_loop())

event_loop()
