import requests
import json

podcasts = [
    "Loop infinito xataka",
    "El test de touring",
    "Inteligencia artificial Jon hernandez",
    "No tiene nombre el bruno",
    "Inteligencia artificial pocho costa"
]

def search_podcast(term):
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "media": "podcast",
        "entity": "podcast",
        "limit": 1
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["resultCount"] > 0:
            result = data["results"][0]
            return {
                "name": result["collectionName"],
                "feedUrl": result["feedUrl"],
                "artist": result["artistName"],
                "artwork": result["artworkUrl600"]
            }
    except Exception as e:
        print(f"Error searching for {term}: {e}")
    return None

results = {}
for p in podcasts:
    print(f"Searching for: {p}")
    res = search_podcast(p)
    if res:
        print(f"Found: {res['name']} - {res['feedUrl']}")
        results[p] = res
    else:
        print(f"Not found: {p}")

print("\nFinal Results JSON:")
print(json.dumps(results, indent=2))
