import urllib.request
import json
import urllib.parse

def fetch_metadata(game_name):
    """
    Fetches game metadata (description, image) from Steam Store API.
    """
    try:
        # Search for the game
        query = urllib.parse.quote(game_name)
        url = f"http://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        if data and data.get("total", 0) > 0:
            item = data["items"][0]
            app_id = item["id"]
            
            # Get details for the specific app
            details_url = f"http://store.steampowered.com/api/appdetails?appids={app_id}"
            with urllib.request.urlopen(details_url) as response:
                details_data = json.loads(response.read().decode())
                
            if details_data and str(app_id) in details_data and details_data[str(app_id)]["success"]:
                game_info = details_data[str(app_id)]["data"]
                
                genres = []
                if "genres" in game_info:
                    genres = [g["description"] for g in game_info["genres"]]
                    
                return {
                    "description": game_info.get("short_description", ""),
                    "image_url": game_info.get("header_image", ""),
                    "genres": genres
                }
                
        return None
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return None
