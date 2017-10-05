# r4

Automatic Geodistribution to S3 and S3-like services on the client and server side

(aka Ridiculously Redundant Redundant storage Router)

## Why should you care?

[Summary of the Amazon S3 Service Disruption in the Northern Virginia (US-EAST-1) Region](https://aws.amazon.com/message/41926/)

The long and the short of it: an S3 was down for a little while, and it practically broke the internet. R4 can fix that problem for you at effectively 0 performance penalty.

## What does it do?

### Client

The R4 client will automatically redistribute requests to S3 or other similar services on the client side. It is implemented (in progress) by patching in a multi-threaded request implementation into the boto3 package. This maintains line for line compatibility while offering the geo-distribution to ensure that your product will work without fail.

### Server

The R4 server system will take in requests designed for a single S3 server or service and redirect the request across multiple servers with the effective performance of the fastest server. This offers the advantage that it will work will all existing clients and is transparent (short of changing the desired endpoint url in configuration). This service will be paid, but it will only be for minimal cost above and beyond the cost for R4 to store your data.
