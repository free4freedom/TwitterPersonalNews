import twitter
import json

def oauth_login():
    CONSUMER_KEY = 'Il4zL2aYkiv5gK48rOnf20ygT'
    CONSUMER_SECRET = 'uzmhD58Q7VRT6ygeVUUorcMsGr2fZXfnloIS5ZUPRZPQkQYbbn'
    OAUTH_TOKEN = '404911413-2wMh9NfTpr6CkLGIkdrbBsaAMZ7FnGWUcHbn8zh5'
    OAUTH_TOKEN_SECRET = 'Gx2oSgxv13BQ8ROQQATncCn8tjjB6qATpCZirqqZgs55M'

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

twitter_api = oauth_login()

#----------------------------------------------------------------------------------------
#Get tweets from a particular account
#-------------------------------------
import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine

def harvest_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=1000 ) :
    assert(screen_name != None) != (user_id != None)

    #Keyword args for the twitter API call
    kw = {
        'count' : 200, 
        'trim_user' : 'true', 
        'include_rts' : 'true',
        'since_id' : 1
    }

    if screen_name : 
        kw['screen_name'] = screen_name
    else :
        kw['user_id'] = user_id

    max_pages = 16
    results = []

    tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)

    if tweets is None :
        tweets = []

    results += tweets

    #print >> sys.stderr, 'Fetched %i tweets' %len(tweets)
    print "----" + str(len(tweets))
    print tweets[0]
    print tweets[1]
    print tweets[len(tweets)]
    #print type(tweets)

    page_num = 1

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry
    
    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:
    
        # Necessary for traversing the timeline in Twitter's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.
        kw['max_id'] = min([ tweet['id'] for tweet in tweets]) - 1 
    
        tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
        results += tweets

        print "----" + str(len(tweets))
        print tweets
        print type(tweets)
        #print >> sys.stderr, 'Fetched %i tweets' % (len(tweets),)
    
        page_num += 1
        
    print >> sys.stderr, 'Done fetching tweets'

    return results[:max_results]


def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw) :
    #START : Nested Helper Function
    #------------------------------
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e


    #END : Nested Helper Function
    #------------------------------

    wait_period = 2
    error_count = 0

    while True :
        try : 
            return twitter_api_func(*args, **kw)

        except twitter.api.TwitterHTTPError, e :
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None :
                return 

        except URLError, e :
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing ..."
            if error_count > max_errors :
                print >> sys.stderr, "Too many consecutive errors ... bailing out !"
                raise

        except BadStatusLine, e :
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing ..."
            if error_count > max_errors :
                print >> sys.stderr, "Too many consecutive errors ... bailing out !"
                raise



#Sample Usage -
response = harvest_user_timeline(twitter_api, screen_name="the_hindu", \
                               max_results=200)

#print json.dumps(tweets[0], indent=1)

print "Results fetched " + str(len(response))

#Write all the tweets to a file
f = open("the_hindu.txt", "w")

'''
for i in range(len(response)) :
    f.write( response[i]['text'].encode('utf-8') + "\n")
    f.write( response[i]['created_at'].encode('utf-8') + "\n" )
    f.write( str(response[i]['favorite_count']) + "\n")
    f.write( str(response[i]['retweet_count'])  + "\n")

f.close()
'''    
