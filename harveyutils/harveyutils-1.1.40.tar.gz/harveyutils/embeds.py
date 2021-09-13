import requests
from datetime import datetime


class Embed:
    def __init__(self):
        self.embed = {}

    def set_title(self, title):
        self.embed["title"] = f"{title}"

    def set_description(self, description):
        self.embed["description"] = f"{description}"

    def set_colour(self, colour):
        self.embed["color"] = f"{int(colour, 16)}"

    def add_field(self, field_name, field_value, inline=False):
        if "fields" in self.embed.keys():
            self.embed["fields"].append(
                {"name": f"{field_name}", "value": f"{field_value}", "inline": inline}
            )
        else:
            self.embed["fields"] = [
                {"name": f"{field_name}", "value": f"{field_value}", "inline": inline}
            ]

    def set_footer(self, footer_text):
        self.embed["footer"] = {"text": f"{footer_text}"}

    def set_timestamp(self):
        self.embed["timestamp"] = datetime.now().isoformat()

    def set_thumbnail(self, img_url):
        self.embed["thumbnail"] = {"url": img_url}

    def send(self, webhook, username="", content="", avatar_url=""):
        """Sends an embed.

        Arguements:
            webhook:String -- A Discord webhook URL
            username:String --
            content:String --
            avatar_url:String --

        Returns:
            success:Bool, status_code:Int -- A bool representing if the webhook successfully sent and the status code response
                from the webhook request.
        """
        json_data = {
            "embeds": [self.embed],
            "username": f"{username}",
            "content": f"{content}",
            "avatar_url": avatar_url,
        }
        res = requests.post(webhook, json=json_data)
        if res.status_code != 204:
            return False, res.status_code
        else:
            return True, res.status_code
