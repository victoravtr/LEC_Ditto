""" Functions related to the Twitter API """

import sys
import logging
from time import sleep
from os import environ
import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from utils import exception_info, get_json_content, get_seconds_remaining, save_json_content


USERS_DATA_PATH = 'data/usersData/'

load_dotenv('config.cfg')
CONSUMER_KEY = environ.get('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = environ.get('TWITTER_CONSUMER_SECRET')
ACCESS_KEY = environ.get('TWITTER_ACCESS_KEY')
ACCESS_SECRET = environ.get('TWITTER_ACCESS_SECRET')
BEARER_TOKEN = environ.get('TWITTER_BEARER_TOKEN')

API_ENDPOINT = 'https://api.twitter.com/2/users/'
FOLLOWERS_IDS_PARAMS = '/following?max_results=1000'

API_RATE_LIMITS = {
    'FOLLOWING_LOOKUP': 15,
    'USER_LOOKUP': 300,
    'SEND_TWEET': 75
}
FIFTEEN_MINUTES = 900

HEADERS = {
    'Authorization': 'Bearer ' + BEARER_TOKEN
}


logging.basicConfig(filename='data/log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)


@sleep_and_retry
@limits(calls=API_RATE_LIMITS['FOLLOWING_LOOKUP'], period=FIFTEEN_MINUTES)
def following_request(user_id, pagination_token):
    """ Get the list of accounts the user is following

    Args:
        user_id (str): The user id of the account we want to get the data
        pagination_token (str): The pagination token to get the next page of the followers

    Raises:
        Exception: if the request contains errors

    Returns:
        dict: The response of the request
    """
    url = f"{API_ENDPOINT}{user_id}{FOLLOWERS_IDS_PARAMS}"
    if pagination_token is not '':
        url += f"&pagination_token={pagination_token}"
    try:
        response = requests.request("GET", url, headers=HEADERS)
        while response.status_code == 429:
            seconds_until_reset = get_seconds_remaining(response.headers['x-rate-limit-reset'])
            LOGGER.error(f"API rate limit reached: {response.status_code} Waiting {seconds_until_reset} seconds")
            sleep(seconds_until_reset)
            response = requests.request("GET", url, headers=HEADERS)
        if 'errors' in response.json().keys() or response.status_code != 200:
            raise Exception(response['errors'][0]['message'])
        return response.json()
    except Exception:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)

def get_new_followers_list(user_id, pagination_token):
    """ Get the list of accounts the user is following

    Args:
        user_id (str): The user id of the account we want to get the data
        pagination_token (str): The pagination token to get the next page of the followers

    Returns:
        list: The list of following accounts
    """
    followers_list = []
    response = following_request(user_id, pagination_token)
    if response['meta']['result_count'] == 0:
        return []  # This means user is not following anyone
    for account in response['data']:
        followers_list.append(account)
    while 'next_token' in response['meta'].keys():
        response = following_request(user_id, response['meta']['next_token'])
        for account in response['data']:
            followers_list.append(account)
    return followers_list


@sleep_and_retry
@limits(calls=API_RATE_LIMITS['SEND_TWEET'], period=FIFTEEN_MINUTES)
def send_tweet(tweet):
    """ Sends a tweet

    Args:
        tweet (str): The tweet to send
    """
    logger_message = tweet.replace('\n', ' ')
    LOGGER.info(f"Tweet published: {logger_message}")
    # url = 'https://api.twitter.com/2/tweets'
    # try:
    #     response = requests.post(url, headers=HEADERS, data=tweet)
    #     logger_message = tweet.replace('\n', ' ')
    #     LOGGER.info(f"Tweet published: {logger_message}")
    #     return response.json()
    # except Exception:
    #     LOGGER.error(exception_info(sys.exc_info()))
    #     sys.exit(1)
    # Haven't tested this function yet since I was banned but should work 😁


def get_old_followers_list(user_id):
    """ Get the list of accounts the user is following that we had saved before.
        In case the list doesn't exist, it will be created and saved.

    Args:
        user_id (str): The user id of the account we want to get the data

    Returns:
        list: The list of following accounts
    """
    old_followers_list = get_json_content(f"{USERS_DATA_PATH}{user_id}")
    if old_followers_list is False:
        old_followers_list = get_new_followers_list(user_id, '')
        save_json_content(f"{USERS_DATA_PATH}/{user_id}", old_followers_list)
    return old_followers_list


@sleep_and_retry
@limits(calls=API_RATE_LIMITS['USER_LOOKUP'], period=FIFTEEN_MINUTES)
def check_account(account):
    """ Check if the data of an account is correct. If not gets the correct data

    Args:
        account (dict): The account to check

    Raises:
        Exception: if the request contains errors

    Returns:
        boolean: True if the account's data is correct, False otherwise
        dict: The account's data
    """
    if account['id'] == '':
        response = get_account_by_username(account['username'])
    else:
        response = get_account_by_id(account['id'])
    if response['data']['username'] != account['username'] or response['data']['id'] != account['id']:
        account['username'] = response['data']['username']
        account['id'] = response['data']['id']
        return False, account
    return True, account


@sleep_and_retry
@limits(calls=API_RATE_LIMITS['USER_LOOKUP'], period=FIFTEEN_MINUTES)
def get_account_by_id(user_id):
    """ Get the account data by id

    Args:
        account (str): The user id of the account we want to get the data

    Raises:
        Exception: if the request contains errors

    Returns:
        dict: The response of the request
    """
    url = f"{API_ENDPOINT}{user_id}"
    try:
        response = requests.get(url, headers=HEADERS).json()
        if 'errors' in response.keys():
            raise Exception(response['errors'][0]['message'])
        return response
    except Exception:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)


@sleep_and_retry
@limits(calls=API_RATE_LIMITS['USER_LOOKUP'], period=FIFTEEN_MINUTES)
def get_account_by_username(username):
    """ Get account data by username

    Args:
        username (str): account's username

    Returns:
        dict: account's data
    """
    url = f"{API_ENDPOINT}by/username/{username}"
    try:
        return requests.get(url, headers=HEADERS).json()
    except Exception:
        LOGGER.error(exception_info(sys.exc_info()))
        sys.exit(1)


def username_exists(username):
    """ Check if a username exists

    Args:
        username (str): The username to check

    Returns:
        boolean: True if the username exists, False otherwise
    """
    response = get_account_by_username(username)
    if 'errors' in response.keys():
        return False
    return True
