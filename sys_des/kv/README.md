Key-Value Cache
===============

100M users
10G queries a month

- Get value by key
- Store value, if missing
- (Internal function) evict key-values to make space

Function
--------

Cache is a dictionary of `key: value`, where key is query and value is `short` + `long`. However,
in order to implement an eviction policy, need an additional structure that reflects `timestamp` of
last time the entry can be useful and TTL of the entry, as we may want to indicate when the entry
is too stale to be useful.

For example, may store `query: index`, and `index` points at a node in a TreeMap using timestamp as
the key, where `timestamp`, `query`, `ttl`, `short` and `long` are stored.

Then upon get or put we can lookup the index in the dictionary (HashMap), use that to find the stored
value, and update the TreeMap by moving the touched value to the right position based on access
timestamp.

Now if we need to evict entries, we traverse TreeMap, enumerating it left-to-right, and remove those
whose TTL has expired, or such that were Least Recently Used. It means that `query` is stored in TreeMap,
too, so that we can remove entries in the dictionary at the same time.

Sizing
------

10G queries / month = 4K qps

Query footprint:
- 100 bytes query
- 200 bytes short description
- 1K long snippet
- ~50 bytes of overhead from datastructure
- ~50 bytes of overhead to store cache hit stats per entry for monitoring purposes
Total: ~1.4K

Operation | Network | CPU |  RAM  | Disk | IOPS
:-------- | -------:| ---:| -----:| ----:|:----
GET       | 50 Mbps | 0.5 | 0     | 0    | 0
PUT       | 50 Mbps | 0.5 | 6MB/s | 0    | 0

~6MB/s stored means we retain ~24GB/hour, or ~540GB/day.

This means that if we limit TTL to 1 hour, we can do all of this with a single machine. The actual
capacity is likely driven by cache hit rate, which is driven by uniqueness of queries issued by users.
(1 hour is only ~16M queries, so not all users even had a chance to send a single query)

HA
----

We can use master/replica configuration where all PUT requests end up on the master, and master propagates
the changes to the replicas. Whether this is done synchronously or asynchronously is driven by end-user
requirements. Asynchronous replication will lead to weaker consistency guarantees.

We can drive GET traffic to replicas to give master room to breathe.

We can drive GET traffic to the nearest replicas to reduce latency.

We can use heartbeats to detect liveness of master or replicas.

When replica outage is detected, we just start a new one. When a master outage is detected by a quorum of
replicas, they use Paxos or Raft to elect a new master.

Scaling
-------

We partition all key space by hashing. We will use a consistent hashing scheme to limit impact from cluster
size changes.

There are alternatives to pick from:

- Which of the masters contains a given entry is specified externally

In this case external APIs allow to control where hot data resides, and scale out replicas that are under
pressure. However, when autoscaling masters, resharding becomes a nuisance - it is no longer something that
can be decided between the cache nodes themselves.

- Which of the masters contains a given entry is decided internally

In this case there is no external API to decide placement of data, but things autoscale easier.
