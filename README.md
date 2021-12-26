<div align="center">

# ✨ LEC_Ditto ✨

<img src="ditto.png" height="auto" width="200">

I'm **Ditto**, and I'm a **bot** 🤖.

<h3>
    <a href="#getting-started">Getting Started</a>
    <span> | </span>
    <a href="#Installation">Installation</a>
    <span> | </span>
    <a href="#Usage">Usage</a>
</h3>

</div>

## Getting Started

**LEC_Ditto** is a bot that tracks the follows and unfollows of Twitter accounts. It's written in **Python** and uses the **Twitter API** to get the data.

### Why Telegram?

Long story short, technically the way the bot works, sending tweets mentioning several accounts, is against Twitter rules and I was **banned** for it 🤐.

I needed a simple way to store the information and have easy access to it to filter and send the tweets. If you try the bot, you will realize that it generates a lot of noise and you are going to need a way to deal with that.

**Telegram** is *"perfect"* for that. You can have the information synced on several devices and you can filter it in a very easy way.

If you still do not want to use it, just comment out lines *87* and *93* of the *main.py* file and the bot will continue working normally.

### Sending tweets

**Not advised; you may end up banned.**

If you still want to send tweets in an automated way using the **API** just remove the comments from lines *110* to *118* of the *main.py* file.

## Requirements

- [Python 3.7+](https://www.python.org/)
- [Poetry 1.1.12](https://python-poetry.org/)
- [Twitter API Keys](https://developer.twitter.com/)
- [Telegram bot tokens](https://core.telegram.org/bots)

## Installation

**Download** the repo using *git* or directly from [*github*](https://github.com/victoravtr/LEC_Ditto/archive/refs/heads/master.zip)

```bash
git clone https://github.com/victoravtr/LEC_Ditto.git
```

**Install** dependencies with *poetry*:

```bash
poetry install
```

Put your **API keys** and **tokens** in the *config.cfg* file.

Put the **accounts** you want to track in the *data/users.json* file. There is a sample file with all LEC players to show you how the format looks like.

**Important:** *"name"* and *"username"* or *"id"* are **required**, the bot will not work without them.

You can choose one between *"username"* and *"id"* and the bot will look for the missing data but *"name"* is **mandatory**. Some players change their *Twitter names* quite often and many of them may not be recognizable, you need to *name* them to know which player you are talking about.

```json
{ 
    "accounts": [
        {
            "name": "G2 Esports",
            "username": "G2esports",
            "id": "1124722303"
        },
                {
            "name": "FNATIC",
            "username": "FNATIC",
            "id": "19976791"
        }
    ]
}
```

## Usage

**Start** the bot with the following command:

```bash
poetry run python3 main.py
```

That's all!🎉
