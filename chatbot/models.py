from django.db import models

class ChatLog(models.Model):
    user_query = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query: {self.user_query[:40]}... ({self.created_at.strftime('%Y-%m-%d %H:%M')})"