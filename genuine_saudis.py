import queue
from dotenv import load_dotenv
from tweepy import Client, Paginator, User, Response
from db import get_collection
from os import environ
from queue import Queue
from threading import Thread
from logger import get_logger

import harvest_tweets


load_dotenv()
log = get_logger("general", "genuine_dataset.log")


genuine_saudis = get_collection("genuine_saudis")


class Worker(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                user: User = self.queue.get()
                features = harvest_tweets.run(user)

                genuine_saudis.insert_many(features)

            except Exception as e:
                log.error((f"USER ID {user.id}\n........\n{e}\n........\n"))
            finally:
                self.queue.task_done()


bearer_token = environ["ACADEMIC_BEARER_TOKEN"]
tweepy_client = Client(bearer_token=bearer_token, wait_on_rate_limit=True)


response = tweepy_client.get_user(username="verified")
if response.data is None:
    print("Twitter Verified account doesn't exist")
    exit()

verified_profile_id = response.data.id
saudi_arabia = "المملكة العربية السعودية"
location_logger = get_logger("location", "location.log")

# TODO: remove limit. set max results
user_fields = ["created_at", "location", "description", "public_metrics"]
for response in Paginator(tweepy_client.get_users_following, verified_profile_id,
                          max_results=10, user_fields=user_fields,
                          limit=1):
    if response.data is None:
        continue

    queue = Queue()
    for i in range(2):
        worker = Worker(queue)
        worker.daemon = True
        worker.start()

    for user in response.data[:2]:
        user: User

        location_logger.info(f"{user.location}—{user.username}")
        if user.location == saudi_arabia:
            queue.put(user)

    queue.join()
