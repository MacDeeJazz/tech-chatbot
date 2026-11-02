from django.contrib import admin
from .models import ChatLog

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('user_query', 'created_at')
    search_fields = ('user_query', 'bot_response')