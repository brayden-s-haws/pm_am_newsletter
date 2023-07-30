import praw
import datetime
import reddit_creds

def scrape_reddit():
    """ This uses the Reddit API to grab the top posts for the last 24 hours
    :return: dict
    """
    # Set up the Reddit client
    reddit = praw.Reddit(
        client_id='YOUR REDDIT CLIENT ID',
        client_secret='YOUR REDDIT CLIENT SECRET',
        redirect_uri='http://localhost:8080',
        user_agent='YOUR REDDIT AGENT (APP) NAME',
    )

    # Get the subreddit
    subreddit = reddit.subreddit('ProductManagement')

    # Get the current time
    now = datetime.datetime.now()

    # Get the top 3 posts by "hot" from the past day
    posts = subreddit.top(time_filter='day', limit=3)

    reddit_posts = {}
    counter = 1
    # Loop over the posts
    for post in posts:
        # Convert the post's timestamp to datetime
        post_time = datetime.datetime.fromtimestamp(post.created_utc)

        # Calculate the time difference
        time_diff = now - post_time

        # Check if the post is from the past day
        if time_diff < datetime.timedelta(days=1):
            reddit_posts[counter] = {'title':post.title,'url':post.url}
            counter += 1

    return reddit_posts


def get_reddit_posts():
    return scrape_reddit()


if __name__ == "__main__":
    reddit_data = get_reddit_posts()

