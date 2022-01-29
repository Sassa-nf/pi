Pub/Sub
=======

[Handouts](https://static.googleusercontent.com/media/sre.google/en//static/pdf/nalsd-pubsub-handout-a4.pdf)
[Lecture Notes](https://docs.google.com/presentation/d/1X4IP_9Sk0oMfofbB8_srGlKkOQiTxfBhKGEee3NQvnU/)

API
---

- subscribe(topic\_id, consumer\_id)
- push(topic\_id, message)
- pop(topic\_id, consumer\_id) -> message
- list() -> topics

Sizing requirements
-------------------

- ids are 8 bytes
- 5K topics
- push() 10K messages per day per topic
- 10K consumers
- 5 topics per consumer
- avg message size is 5KB, max message size is 100MB
- 95% reads access data that is 10 minutes old or less

SLO
---

- Any two datacentres can cope with peak load
- 99% of messages can be popped in under 1 second
- 99% of operations succeed in under 0.5 second
- Can lose 0.01% of pushed messages per year
- At-least-once delivery
- Retain messages for 100 days
   - Older messages can be discarded; SLOs do not apply to older messages, if they are available

Infra
-----

- 3 DCs across the US
- 100Gbps between DCs
- Network is 99.99% available
- Reliable distributed storage with 1 second replication delay
- Authn/Authz taken care of

Machines:

- 128GB RAM
- 1x2TB SSD or 1x4TB HDD
- 32 cores
- 10 Gbps network


Function
--------

All topics are "append logs" on some storage with one index per topic telling the position of the last published
message. (Basically, a file length) Push service amounts to appending messages to a file and enabling Pop service
to detect that a new message has arrived. Since we will need HA, Push service may need to append messages to more
than one file - so it can be read back from one of the replicas - before acknowledging receipt of the message from
a publisher.

All consumers are represented by the mapping `consumer_id -> read_position` for every topic. Pop service uses
`read_position` to decide the position of the first unconsumed message, and updates `read_position` after the
receipt of the message has been acknowledged by the consumer. This is a small amount of data, but needs to be
replicated along with the topic contents. A failure to replicate this data will still result in at-least-once
delivery goal.

Sizing
------

Push:

5K topics * 10K messages / day / topic = 50M messages / day ~= 600 qps

50M messages / day * 5KB / message = 250GB / day ~= 10GB / hour ~= 2.7MB/s = 22 Mbps

250GB / day * 100 days / retention period = 25TB / retention period

Pop:

10K consumers * 5 topics / consumer * 600 qps / 5K topics = 6K qps
6K messages / second * 5KB / message = 30MB/s = 240Mbps


Operation |  Network | CPU |  RAM  | Disk | IOPS
:-------- | --------:| ---:| -----:| ----:|:----
Push      |  22 Mbps |     |       | 25TB | 600
Pop       | 240 Mbps |     |       | 0    | 0

Based on these estimates, the bottleneck resource is Storage. We need about 6 disks, if we use HDD. This means
we also get 6 * 128GB of RAM, which is 0.75TB that we can use to cache almost 1 hour worth of messages, so we
don't need to touch disk for Pop.

HA
---

Replication requires to double the bottleneck resource, which in this case is disk.

For high availability we replicate this setup 3x like so: 2 DCs should handle entire workload, so 6 machines
are available in each DC; then a loss of one DC means the remaining 2 DCs handle traffic and replication.

We shard the topics across available machines so the distribution of masters is even. We use consistent hashing
for that, eg weighted random, so master and replica are chosen at the same time.

Since we have capacity to replicate 3 ways, we may just as well do that: replication can be done in parallel, so
no extra latency incurred, but having three nodes involed encures we can talk of a quorum to detect network
partitions and outages. Since message queues are already logs, Raft can be used to negotiate the state of the
topics. We don't need to have such a strong agreement on the state of consumers, as that only requires at least
once delivery semantics - some loss of consumer state is acceptable. That is, we will replicate the state of
consumer as best effort, but we don't need expensive quorum negotiation for every consumer state update.
