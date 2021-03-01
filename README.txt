Evan Tilley
elt2141
2/28/21

This proxy server should work as intended but there are a few assumptions that
I made in its creation, which are outlined below. Also note that the default
port number is 8888, but if a 4th argument is specified on the command line
(i.e. python3 server.py localhost 30047), then the server will run on
port 30047.

I had a lot of trouble thinking about how the "if-modified-since" headers would work.
Based on Piazza responses and lecture notes, here is what I ended up doing.

1. The server will work for requests such "www.example.com/index.html", "www.example.com",
 "example.com", "http://example.com", "http://example.com/index.html", etc. Note that the
 proxy server does not support https:// requests (note that an easy workaround here to "support" this
 would be to essentially remove the "https" from the request (i.e. change it to http) but this is misleading
 and a pretty big security flaw so I did not do that).

2. If a "/" is at the end of the file requested (i.e. "www.example.com/" instead of "www.example.com"), the
proxy server handles this by removing the "/" and treating it as a file rather than a directory.

3. The server sends HTTP 1.0 requests.

4. When a filename is not specified (i.e. http://example.com), the proxy server simply
gets the default response of the server and stores it in a file called "/example.com/default".

5. The proxy server caches (using the if-modified-since method) both get and post requests.

6. The proxy server does not handle requests for images/recursive requests/etc.

7. If a server returns a response other than "200 OK", the response is not cached. For an example
of this, try requesting something like "omegle.com", which, due to CloudFlare security reasons,
returns a 400 Bad Request. This response is returned to the client, but it is not cached.

8. This proxy server supports GET and POST requests.

localhost:8888/httpbin.org/post?beans=asdfasdf