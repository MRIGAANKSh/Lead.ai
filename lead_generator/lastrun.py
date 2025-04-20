# import http.client

# conn = http.client.HTTPSConnection("api.apify.com")
# headers = {
#     'Content-Type': 'application/json',
# }

# # Define the correct endpoint (this is the path part)
# url_path = "/v2/acts/compass~crawler-google-places?token=apify_api_5gjXmwixLft6dhPAlijFzp9bgNUj3u2pOafs"

# # Make the request
# conn.request("GET", url_path, headers=headers)

# response = conn.getresponse()
# data = response.read()

# print(data.decode("utf-8"))
import http.client

conn = http.client.HTTPSConnection("api.apify.com")  # Only the domain
headers = {
    'Content-Type': 'application/json',
}

path = "/v2/acts/compass~crawler-google-places/runs/last?token=apify_api_5gjXmwixLft6dhPAlijFzp9bgNUj3u2pOafs"

conn.request("GET", path, headers=headers)
res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
