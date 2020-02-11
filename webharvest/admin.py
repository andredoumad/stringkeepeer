from django.contrib import admin


from .models import WebharvestThread, WebharvestChatMessage, WebharvestRobot

class WebharvestChatMessage(admin.TabularInline):
    model = WebharvestChatMessage

class WebharvestThreadAdmin(admin.ModelAdmin):
    inlines = [WebharvestChatMessage]
    class Meta:
        model = WebharvestThread 

admin.site.register(WebharvestThread, WebharvestThreadAdmin)


class WebharvestRobotAdmin(admin.ModelAdmin):
    model = WebharvestRobot

admin.site.register(WebharvestRobot, WebharvestRobotAdmin)


# from django.contrib.admin import ModelAdmin, site
# from webharvest.models import WebharvestMessageModel


# class WebharvestMessageModelAdmin(ModelAdmin):
#     readonly_fields = ('timestamp',)
#     search_fields = ('id', 'body', 'user__username', 'recipient__username')
#     list_display = ('id', 'user', 'recipient', 'timestamp', 'characters')
#     list_display_links = ('id',)
#     list_filter = ('user', 'recipient')
#     date_hierarchy = 'timestamp'


# site.register(WebharvestMessageModel, WebharvestMessageModelAdmin)
