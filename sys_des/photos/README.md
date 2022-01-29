https://www.youtube.com/watch?v=ohtqI3AHR0k

Scope
=====

1M users
upload 50 photos a day

- search by user, latest, hashtag, topic; get 10 thumbnails per page
- get detail view - original image, one at a time, when clicked on thumbnail

image is 4MB
thumbnail is 256KB

SLO
---

Serve 99.9% of thumbnail pages at 250ms

Serve 99.9% of full image at 200ms

SLOs do not apply to images older than 30 days

Available
---------

Network (99.99% available)

Storage (SLA read 100ms at 95%, write 200ms at 95%)

Storage provides thumbnails on request. Globally replicated, eventually consistent
within minutes.

3 datacentres: Europe, Asia, N.America. Each unavailable for 1 week each quarter for
planned maintenance

HDD: 24GB RAM, 8 cores, 2x2TB HDD, 10Gb ethernet
SSD: 24GB RAM, 8 cores, 2x1TB SSD, 10Gb ethernet

Design
======

Rough sizing:

Storage: 1M users x 50 photos / day x 400 days / year x 4MB / photo = 80PB of storage a year, plus replicate

Storage of 30 day-old photos: 1M x 50 x 30 x 4MB = 6GB x 1M = 6PB

Upload bandwidth: 1M x 50 x 4MB x 30 / 2.5M = 50 x 4MB x 3 x 10 / 2.5 = 50 x 4MB x 3 x 4 = 2400MB / sec = 20Gbps


Storage service does not meet the SLO: we simply don't know how long it takes to read the remaining 4.9% of cases.
Datacentres alone also do not meet the SLO: 1 week per quarter is already ~7% outage.

So we'll have 30 days worth of photos plus thumbnails stored on machines, plus replicate across data centres.

Reading full image is 4MB sequential read, so even HDDs will do (https://gist.github.com/jboner/2841832 - 20ms / MB)

Storing 30 days of photos is 6PB. Each HDD machine has 2TB (the other 2TB is for replica). So we need 3K machines to
store everything for 1 month. Everything that is older than 1 month is deferred to read from Storage Service.

Each machine can serve 400 photos / second (10Gbps / 4MB = 1.6GBps / 4MB = 0.4K). 3K machines can serve 1.2M photos
a second, if load is spread evenly.

```
LB -> Search -> Metadata
             -> Photos
   -> Upload -> Queue -> Photos
                      -> Metadata
                      -> Replicate
             -> Storage Service
   -> GetDetail -> Photos
```

Photos service is a bunch of those HDD servers. Storage for each photo is decided by consistent hash of a photo
to spread the load. Consistent hash (like max random) allows to pick a replica in another data centre, too.

Metadata service fronts an ACID DB, with in-memory distributed cache. It stores photo's hash, to enable discovery
of storage nodes for photos and thumbnails.

Some photos become hot keys, we add key popularity tracking: photo id is mapped to a rank reflecting how many
replicas should be used; then use top N nodes from max random consistent hashing scheme.

Revision
========

Ok, in the video they actually ignored that Storage service SLA is just 95%, and used Storage Service. The
system is focused on storing and retrieving metadata used for searches. Now that metadata is the actual thing
being stored, its size becomes non-negligible.

Let's assume 8KB metadata. Storing it is the same problem as above, but now the scale is 4MB/8KB = 500x smaller.
It means we should probably need about 6 servers. Let's check.

Assuming 8KB x 1M x 50 x 30 = 12TB of metadata is produced every month.

Bottleneck analysis
-------------------

1. Latency. Search kicks off a task at a small number of nodes in parallel (map), and they have 100ms to work
   it out. Then search receives response from the nodes, and combines the results to construct the response
   containing 10 thumbnails (reduce). Based on this, sends 10 requests to Storage Service, which respond in
   100ms. Now we can respond within 200ms target time.

   Each needs to be designed to read a small amount of data, as reading 5MB is going to consume ~100ms, and each
   node then will be able to do no more than 5 perfectly timed searches per second.

   Upload is just 200ms that Storage Service offers, plus a write of metadata.

   Get image now is also just 100ms that Storage Service offers.

Bottleneck | Upload | Search | Get image
:--------- | ------:| ------:| --------:
Latency    |        |
Bandwidth  |        |
IOPS       |        |
