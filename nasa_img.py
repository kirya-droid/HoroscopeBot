import requests

api_key = "Yor_api_nasa"
def api_nasa():
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&count=1"
    response = requests.get(url)
    image_data = response.json()[0]
    image_url = image_data["url"]
    return image_url