https://github.com/donnemartin/system-design-primer/blob/master/solutions/system_design/twitter/README.md

Operations
----------

- Tweet
- Each tweet fanned out / pushed to followers
- Read (get the feed / timeline)
   - Read own timeline
   - Read aggregate of timelines of users we follow
- Search by keyword

Sizing
------

- 100M users
- 500M tweets/day = 15G tweets/mo = 6K tweets/s
- 10 fan-out/tweet = 60K fan-out/s
- 250G reads/mo = 100K reads/s
- 10G search/mo = 4K search/s

Tweet
-----

- tweet_id = 8B
- user_id = 32B
- text = 140B
- media = 10K

- 15G tweets/mo x 10K/tweet = 150T/mo = 540P/3yr

Design
------

```
Client -> LB -> Server -> Tweet -> Queue -> Fan out -> Client
                       -> Read
                       -> Search
```

Tweet, Read, Search, Fan-out are connected to a time series DB, the tweet content DB, user message queue,
and the user-follower DB.

Tweet content
-------------

- user_id x tweet_id x text x media

Tweet service
-------------

8B for tweet_id is enough to store a few hundred years worth of nanoseconds; so we can potentially just look at
the nanosecond-precision clock for every tweet, and that way get both a tweet_id and causal ordering guarantee.

The problem here is that Tweet service is going to be distributed and restartable, so need to solve the clock
synchronization problem. A straightforward solution is to use a global sequencer. 6K atomic increments per second
is easily achievable on a single instance, but there are going to be corner cases with global sequencer service
restart. We can use a global sequencer service, lower the global sequencer request rate by requesting a range
(not necessarily contiguous), then use that range for multiple tweets within the same second, for example.

Another possible solution is TrueTime, like in Spanner. There transactions are identified using a very accurate
system of clocks, and by delaying the transaction start events by the amount of uncertainty - a few ms in their case.
In case of tweets it may be acceptable to delay availability of tweets by, say, 100 ms, and get Tweet service's
clocks accurate to 100 ms (eg re-synch the clocks every 10 seconds). That way tweet ids can be easily ordered in
causal order - lack of synch between some clocks will not be visible.

tweet_id is determined to decide relative order of tweets. It is decided based on the max tweet_id the User has
seen before creating a new tweet, the local clock of the Tweet service instance, and the global sequencer (if we are
using any). So based on the local clock, if the second is the same as the claimed range, use a number from the
range that is greater than the last observed tweet_id. For simplicity we can assume last observed tweet_id is
supplied by the client, but we can maintain is server-side by updating the tweet_id seen by the Fan out, Read and
Search on behalf of the user, although this would mean read operations become write operations.

Once tweet_id is determined, persist in Tweet DB, and throw into Queue for Fan out to pick up for delivery to
followers, updating search, cross-region replication, etc.

User Message Queue
------------------

Not sure if I need it. We can consider this for later, as a cache of time series for most active users.

Tweet DB
--------

This is a distributed cache/K-V store case.

Partition by user_id, so queries for a given user timeline can be routed to specific service instances. Prolific
users / popular with lots of followers will be hot keys. We can solve this by maintaining a (small) dictionary of
hot user_ids, and dedicate several partitions to these, which need to be consulted at tweet/read/search time.

We can determine prolific users by maintaining per-user metrics: storage size consumed, fan-out rate in the last
day, or something of that sort.

Read Service
------------

Given a user_id, retrieves one page of last tweets. If you keep scrolling, you keep requesting from last loaded
offset - last seen tweet_id, which is timestamp.

Or, given a user_id, retrieves a list of users he follows, reads one page of last tweets from each of those
users, and sorts them by tweet_id to ensure causal ordering.

Search Service
--------------

This is a distributed cache/K-V store case again. We map search criteria (eg hashtags) to tweet_id x user_id. Same
considerations for hot search words.
