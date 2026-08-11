
class CustomEmoji:
    def __init__(self, custom_emoji_id: int):
        self.custom_emoji_id = custom_emoji_id
    def __str__(self):
        return f'<tg-emoji emoji-id="{self.custom_emoji_id}"></tg-emoji>'