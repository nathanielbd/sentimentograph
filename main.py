#! usr/bin/python3
import praw
from praw.models import MoreComments
import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
from textblob import TextBlob

def main():
    argc = len(sys.argv)
    if argc < 3:
        print("Usage: python main.py <subreddit> <topic>")
        print("Do not put the r/ in the subreddit name")
        print("Input:")
        print(sys.argv)
        return
    # allow for multi-word topics
    topic = " ".join(sys.argv[2:])
    # get set up a reddit app at https://ssl.reddit.com/prefs/apps/
    # reddit account needed
    reddit = praw.Reddit(client_id = '<YOUR_CLIENT_ID>', \
            client_secret = '<YOUR_SECRET>', \
            user_agent = 'sentimentograph', \
            username   = '<YOUR_REDDIT_USERNAME>', \
            password   = '<YOUR_REDDIT_PASSWORD>')
    sub     = reddit.subreddit(sys.argv[1])
    search  = sub.search(topic, sort='top', limit=1000)
    labels  = ["Positive", "Negative"]
    now     = datetime.datetime.now()
    n       = now.year - 2005 + 1
    # reddit started in 2005
    x = []
    for i in range(0, n):
        x.append(2005 + i)
    positive = [0]*n
    negative = [0]*n

    for result in search:
        created = time.gmtime(result.created_utc)
        year = created.tm_year - 2005
        title = TextBlob(result.title)
        for sentence in title.sentences:
            if sentence.sentiment.polarity > 0:
                positive[year] += sentence.sentiment.polarity
            else:
                negative[year] -= sentence.sentiment.polarity
        selftext = TextBlob(result.selftext)
        for sentence in selftext.sentences:
            if sentence.sentiment.polarity > 0:
                positive[year] += sentence.sentiment.polarity
            else:
                negative[year] -= sentence.sentiment.polarity

    comments = sub.search(topic, sort='comments', limit=1000)
    for comment in comments:
        created = time.gmtime(comment.created_utc)
        year = created.tm_year - 2005
        title = TextBlob(comment.title)
        for sentence in title.sentences:
            if sentence.sentiment.polarity > 0:
                positive[year] += sentence.sentiment.polarity
            else:
                negative[year] -= sentence.sentiment.polarity
        selftext = TextBlob(comment.selftext)
        for sentence in selftext.sentences:
            if sentence.sentiment.polarity > 0:
                positive[year] += sentence.sentiment.polarity
            else:
                negative[year] -= sentence.sentiment.polarity

    # stacked plot
    y = np.vstack([positive, negative])
    fig, ax = plt.subplots()
    ax.stackplot(x, positive, negative, labels = labels)
    ax.legend(loc = 'upper left')
    plt.xlabel('Year')
    plt.ylabel('Sentiment')
    plt.title("Sentiment of %s on r/%s over time" %(topic, sys.argv[1]))
    plt.show()

    # percentage stacked plot
    totals = [i+j for i,j in zip(positive, negative)]
    normalize = lambda i,j: i/j*100 if j != 0 else 0
    normalized_p = [normalize(i,j) for i,j in zip(positive, totals)]
    normalized_n = [normalize(i,j) for i,j in zip(negative, totals)]
    normalized_labels = ["% Positive", "% Negative"]
    fig, ax = plt.subplots()
    ax.stackplot(x, normalized_p, normalized_n, labels=normalized_labels)
    ax.legend(loc = 'upper left')
    plt.xlabel('Year')
    plt.ylabel('Sentiment %')
    plt.title("Percent Positive and Negative Sentiment of %s on r/%s over time" %(topic, sys.argv[1]))
    plt.show()

if __name__ == "__main__":
    main()
