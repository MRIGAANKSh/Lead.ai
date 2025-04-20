import http.client

# Extract just the domain
conn = http.client.HTTPSConnection("api.apify.com")

# Path part only
url = "/v2/acts/compass~crawler-google-places/runs?token=apify_api_5gjXmwixLft6dhPAlijFzp9bgNUj3u2pOafs"

# Make the request
conn.request("GET", url)

# Get response
res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
