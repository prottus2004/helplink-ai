import json
from datetime import datetime, timedelta
from typing import List, Dict

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False


# Multilingual SOS keywords for flood/disaster detection
FLOOD_QUERIES = [
    # Hindi SOS keywords
    'bachao flood -is:retweet lang:hi',
    'baadhh madad -is:retweet lang:hi',
    'badhh help -is:retweet lang:hi',
    # English SOS from India
    'flood rescue trapped survivors -is:retweet place_country:IN lang:en',
    'SOS flood India stranded -is:retweet lang:en',
    # General flood alerts
    'flood alert India emergency -is:retweet lang:en',
    # Malayalam keywords
    'raksha vellam -is:retweet lang:ml',
    # Tamil
    'udavi tanneer -is:retweet lang:ta',
]

LANGUAGE_MAP = {
    "hi": "Hindi",
    "ml": "Malayalam",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "en": "English",
    "kn": "Kannada",
    "mr": "Marathi",
    "gu": "Gujarati",
}


def fetch_live_sos_tweets(bearer_token: str, max_per_query: int = 5) -> List[Dict]:
    """
    Fetch real SOS-like tweets from India flood keywords via Twitter API v2.
    Returns list of tweet objects compatible with NLP processing pipeline.
    """
    if not bearer_token or not TWEEPY_AVAILABLE:
        print("[Twitter] Tweepy not available or no bearer token - skipping live tweet fetch")
        return []

    all_tweets: List[Dict] = []

    try:
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

        for query in FLOOD_QUERIES:
            try:
                print(f"[Twitter] Searching: {query[:50]}...")
                resp = client.search_recent_tweets(
                    query=query,
                    max_results=max_per_query,
                    tweet_fields=["created_at", "lang"],
                    expansions=[],
                )

                if not resp.data:
                    continue

                for tweet in resp.data:
                    lang_code = tweet.lang or "en"
                    all_tweets.append({
                        "source": "twitter",
                        "raw_message": tweet.text,
                        "language_detected": LANGUAGE_MAP.get(lang_code, lang_code),
                        "language_code": lang_code,
                        "language_confidence": 0.90,
                        "location_extracted": "India (Twitter Location)",
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else datetime.utcnow().isoformat(),
                        "data_source": "Twitter/X Live API (REAL)",
                        "is_real": True,
                        "tweet_id": str(tweet.id),
                    })

            except tweepy.TooManyRequests:
                print("[Twitter] Rate limit hit - stopping early")
                break
            except Exception as e:
                print(f"[Twitter] Error on query '{query}': {e}")
                continue

        print(f"[Twitter] Fetched {len(all_tweets)} real SOS-related tweets")
        return all_tweets

    except Exception as e:
        print(f"[Twitter] Fatal error: {e}")
        return []
