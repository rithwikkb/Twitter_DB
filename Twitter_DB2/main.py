from pymongo import MongoClient
import re
import sys
from datetime import datetime, timezone
from pprint import pprint

if len(sys.argv) != 2:
    print("Missing arguments: port-number!")
    sys.exit(1)
    

# mongodb connection:
mongo_port = int(sys.argv[1])
mongo_uri = f"mongodb://localhost:{mongo_port}"
database_name = "291db"
collection_name = "tweets"

client = MongoClient(mongo_uri)
database = client[database_name]
collection = database[collection_name]


def searchingtweets():
    # Get user input for keywords
    keywords_input = input("Enter one or more keywords (comma-separated): ")
    keywords = [kw.strip() for kw in keywords_input.split(",")]

    # Search for tweets based on keywords
    regex_patterns = [re.compile(f".*{re.escape(keyword)}.*", re.IGNORECASE) for keyword in keywords]
    query = {"content": {"$all": regex_patterns}}

    # Retrieving tweets with the specified keywords from MongoDB
    matching_tweets = collection.find(query, {})

    # Use a set to keep track of unique tweet IDs
    unique_tweet_ids = set()

    print("Matching Tweets:")
    # Display content of all unique tweets
    for tweet in matching_tweets:
        tweet_id = tweet['id']
        if tweet_id not in unique_tweet_ids:
            unique_tweet_ids.add(tweet_id)
            print("ID: ", tweet_id)
            print("Date: ", tweet['date'])
            print("Content: ", tweet['content'])
            print("User: ", tweet['user']['username'])
            print("----------------------------")

    matching_tweets.rewind()  # Setting the cursor back (exhausted)
    response = int(input('Enter a tweet ID to see all details or enter 0: '))

    if response != 0:
        for tweet in matching_tweets:
            if tweet['id'] == response:
                pprint(tweet)
                break
        else:
            print("No tweet found with the ID entered")

def searchusers():
    # Get user input for keywords
    keyword = input("Enter a keyword: ")

    # Search for tweets based on keywords
    regex_pattern = re.compile(f".*{re.escape(keyword)}.*", re.IGNORECASE)
    query = {
        "$or": [
            {"user.displayname": {"$regex": regex_pattern}},
            {"user.location": {"$regex": regex_pattern}}
        ]
    }

    # Retrieving users with the specified keywords from MongoDB
    matching_users = collection.find(query, {})

    # Use a set to keep track of unique usernames
    unique_id = set()

    print("Matching users:")
    # Display content of all users
    for i in matching_users:
        username = i["user"]["username"]
        user_id = i["user"]["id"]
        if user_id not in unique_id:
            unique_id.add(user_id)
            print("\n1. Username: " + username)
            print("2. Display Name: " + i["user"]["displayname"])
            print("3. Location: " + str(i["user"]["location"]))

    matching_users.rewind()  # Setting the cursor back (exhausted)
    response = input("Enter a user's username to see all details or enter 0: ")

    if response and response != '0':
        for i in matching_users:
            if i['user']['username'] == response:
                pprint(i['user'])
                print("\n")
                break
        else:
            print("No user found with the username entered")
def composetweet():
    content = str(input("Compose a tweet: "))
    current_time = datetime.now(timezone.utc)
    date = current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
    tweet = {
        "url": None,
        "date": date,
        "content": content,
        "renderedContent": None,
        "id": None,
        "user": {
            "username": "291user",
            "displayname": None,
            "id": None,
            "description": None,
            "rawDescription": None,
            "descriptionUrls": [],
            "verified": None,
            "created": None,
            "followersCount": None,
            "friendsCount": None,
            "statusesCount": None,
            "favouritesCount": None,
            "listedCount": None,
            "mediaCount": None,
            "location": None,
            "protected": None,
            "linkUrl": None,
            "linkTcourl": None,
            "profileImageUrl": None,
            "profileBannerUrl": None,
            "url": None
        },
        "outlinks": [],
        "tcooutlinks": [],
        "replyCount": None,
        "retweetCount": None,
        "likeCount": None,
        "quoteCount": None,
        "conversationId": None,
        "lang": None,
        "source": None,
        "sourceUrl": None,
        "sourceLabel": None,
        "media": None,
        "retweetedTweet": None,
        "quotedTweet": None,
        "mentionedUsers": None
    }
    collection.insert_one(tweet)
    print("Sucessfully Tweeted!")

def list_top_tweets(n, type, userChoice):
    """
    List the top n tweets based on type of request.
    param n: number of tweets to list
    param type: type of request such as retweetCount, likeCount, quoteCount
    param moreDetails: boolean to determine if more details should be printed
    
    Display the id, date, content, and username of the person who posted it in descending order. Should also have an option to see all the columns.
    """
    query = list(collection.aggregate([
        # group by all the fields in the document and then sort by the type of request
        {"$group": {"_id": "$id", "date": {"$first": "$date"}, "content": {"$first": "$content"}, "user": {"$first": "$user"}, type: {"$first": "$" + type}, "url": {"$first": "$url"}, "renderedContent": {"$first": "$renderedContent"}, "outlinks": {"$first": "$outlinks"}, "tcooutlinks": {"$first": "$tcooutlinks"}, "replyCount": {"$first": "$replyCount"}, "retweetCount": {"$first": "$retweetCount"}, "likeCount": {"$first": "$likeCount"}, "quoteCount": {"$first": "$quoteCount"}, "conversationId": {"$first": "$conversationId"}, "lang": {"$first": "$lang"}, "source": {"$first": "$source"}, "sourceUrl": {"$first": "$sourceUrl"}, "sourceLabel": {"$first": "$sourceLabel"}, "media": {"$first": "$media"}, "retweetedTweet": {"$first": "$retweetedTweet"}, "quotedTweet": {"$first": "$quotedTweet"}, "mentionedUsers": {"$first": "$mentionedUsers"}}},
        {"$sort": {type: -1}},
        {"$limit": n}]))
    print("\n")
    print("*" * 50 + "\n")
    print("Printing top " + str(n) + " tweets based on " + type + "\n")
    if userChoice == None:
        for i in query:
            print("\n")
            print("1. ID: " + str(i["_id"]))
            print("2. Date: " + str(i["date"]))
            print("3. Content: " + str(i["content"]))
            print("4. Username: " + str(i["user"]["username"]))

    else:
        for i in query:
            if str(i["_id"]) == userChoice:
                pprint(i)
                break


def list_top_users(n, userChoice):
    """
    List the top n users based on followersCount.
    param n: number of users to list
    param moreDetails: boolean to determine if more details should be printed

    For each user, list the username, displayname, and followersCount with no duplicates. Should also have an option to see all the columns.

    """

    # write a query that displays top n users based on followersCount and also removes duplicates
    query = list(collection.aggregate([
        {"$group": {"_id": "$user.id", "user": {"$first": "$user"}}},
        {"$sort": {"user.followersCount": -1}},
        {"$limit": n}]))
    if userChoice == None:
        print("\n")
        print("*" * 50 + "\n")
        print("Printing top " + str(n) + " users based on followersCount\n")
        for i in query:
            print("\n")
            print("1. Username: " + str(i["user"]["username"]))
            print("2. Display Name: " + str(i["user"]["displayname"]))
            print("3. Followers Count: " + str(i["user"]["followersCount"]))
            print("\n")

    else:
        for i in query:
            if str(i["user"]["username"]) == userChoice:
                pprint(i["user"])
                print("\n")
                break
                
def main():
    print("*" * 20)
    print("Welcome to twitter!")
    print("*" * 20 + "\n")
    while True:
        print("Please select an option:")
        print("1. Search for tweets")
        print("2. Search for users")
        print("3. List top tweets")
        print("4. List top users")
        print("5. Compose a tweet")
        print("6. logout")
        option = str(input("Enter option: "))
        if option == '1':
            searchingtweets()
        elif option == '2':
            searchusers()
        elif option == '3':
            n = int(input('How many tweets do you want to see?'))
            if n < 0:
                print("Invalid number")
                continue
            
            type = input('On what basis do you want to display the tweets. Enter 1 for retweetCount, 2 for likeCount, 3 for quoteCount: ')
            if type not in ["1", "2", "3"]:
                print("Invalid type")
                continue
            
            if type == "1":
                type = "retweetCount"
            elif type == "2":
                type = "likeCount"
            else:
                type = "quoteCount"

            list_top_tweets(n,type, userChoice = None)

            moredetails = int(input("Do you want to select a tweet and see more details or not?(1 for yes 0 for no)"))
            if moredetails == 0:
                continue

            else:
                selected_tweet = input("Enter the id of the tweet you want to see more details of: ")
            
                
                list_top_tweets(n,type, userChoice = selected_tweet)

            
        elif option == '4':
            n = int(input('How many users do you want to see?'))
            if n < 0:
                print("Invalid number")
                continue
            
            list_top_users(n, userChoice = None)

            moredetails = int(input("Do you want to select a user and see more details or not?(1 for yes 0 for no)"))
            if moredetails == 0:
                continue

            else:
                selected_user = input("Enter the username of the user you want to see more details of: ")
            
                if selected_user not in [str(i["user"]["username"]) for i in collection.find()]:
                    print("Invalid username")
                    continue

                else:
                    list_top_users(n, userChoice = selected_user)
                
        elif option == '5':
            composetweet()
        else:
            break
        

    # Close the MongoDB connection
    client.close()


if __name__ == "__main__":
    main()
