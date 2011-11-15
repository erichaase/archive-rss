from tech.models import Post, LikeWordCount, DislikeWordCount
from django.contrib import admin

admin.site.register(LikeWordCount)
admin.site.register(DislikeWordCount)

class PostAdmin(admin.ModelAdmin):
    list_display   = ['source', 'title', 'link', 'date', 'rating', 'like']
    list_filter    = ['source', 'date', 'like']
    search_fields  = ['title', 'desc']
    date_hierarchy = 'date'

admin.site.register(Post, PostAdmin)
