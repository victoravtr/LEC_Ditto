""" Main logic of the program """
import logging
from logging.handlers import RotatingFileHandler
from deepdiff import DeepDiff
from telegram import telegram_bot_sendtext
from twitter import check_account, get_new_followers_list, get_old_followers_list, send_tweet, username_exists
from utils import get_file_content, get_json_content, get_pickle_content, save_json_content, save_pickle_content

USERS_JSON_FILE = 'data/users.json'
USERS_DATA_PATH = 'data/usersData/'
PICKLE_FILE = 'data/outfile.pickle'
BLACKLIST_FILE = 'data/blacklist'
logging.basicConfig(handlers=[RotatingFileHandler('data/log.txt', maxBytes=524288, backupCount=10)],
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.info("Bot started")


def get_differences(old_following, new_following):
    """ Returns a list of differences between two lists

    Args:
        old_following (list): Latest snapshot we have of the following list
        new_following (list): Newest snapshot from Twitter API of the following list

    Returns:
        DeepDiff: A DeepDiff object that contains the differences between the two lists
    """
    differences = DeepDiff(old_following, new_following,
                     ignore_order=True, group_by='id', view='tree')
    return differences


def get_index(data):
    """ Returns the index of the last account we have checked

    Args:
        data (dict): The data from the JSON file

    Returns:
        int: The index of the last account we have checked
    """
    pickle_content = get_pickle_content(PICKLE_FILE)
    if pickle_content == []:
        pickle_content = {'continue': False, 'content': ''}
        save_pickle_content(PICKLE_FILE, pickle_content)
    index = 0
    if pickle_content['continue']:
        for account in data['accounts']:
            index += 1
            if pickle_content['content'] == account:
                break
    return index


def main():
    """ Main function that runs the bot"""
    data = get_json_content(USERS_JSON_FILE)
    index = get_index(data)
    # There are some users that that deactivate and reactivate their account quite often.
    # This generates a lot of noise in the log so if you want to get rid of it, you
    # can put them in the blacklist file.
    blacklist = [user.strip() for user in get_file_content(BLACKLIST_FILE).split('\n')]
    while True:
        total_accounts = len(data['accounts'])
        remaining_accounts = total_accounts - index
        for account in data['accounts'][index:]:
            LOGGER.info(f"Testing: {account['name']} ID: {account['id']}")
            correct, account = check_account(account)
            if correct is False:
                LOGGER.info(
                    f"Account with id {account['id']} has changed: {account}")
                save_json_content(USERS_JSON_FILE, data)

            old_followers_list = get_old_followers_list(account['id'])
            new_followers_list = get_new_followers_list(account['id'], '')
            differences = get_differences(old_followers_list, new_followers_list)

            for case in differences:
                if case == 'dictionary_item_removed':
                    for item in differences[case]:
                        if item.t1['username'] not in blacklist and username_exists(item.t1['username']):
                            tweet = f"🔴 SOURCES:\n{account['name']} (@{account['username']}) unfollowed {item.t1['name']} (@{item.t1['username']}) 📉"
                            send_tweet(tweet)
                            telegram_bot_sendtext(tweet)
                elif case == 'dictionary_item_added':
                    for item in differences[case]:
                        if item.t2['username'] not in blacklist:
                            tweet = f"🔴 SOURCES:\n{account['name']} (@{account['username']}) followed {item.t2['name']} (@{item.t2['username']}) 📈"
                            send_tweet(tweet)
                            telegram_bot_sendtext(tweet)
                elif case == 'values_changed':
                    pass
                elif case == 'type_changes':
                    pass
                else:
                    LOGGER.info(f"New item: {item}")
            save_json_content(f"{USERS_DATA_PATH}/{account['id']}", new_followers_list)
            save_pickle_content(PICKLE_FILE, {'continue': True, 'content': account})
            print(f"Remaining accounts: {remaining_accounts}")
            remaining_accounts -= 1
        LOGGER.info(" ---------- LOOP FINISHED ---------- ")
        index = 0


if __name__ == "__main__":
    main()
