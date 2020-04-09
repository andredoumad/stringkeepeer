from django.contrib import admin
from .models import WebharvestThread, WebharvestChatMessage, WebharvestRobot, WebharvestJob, WebharvestSpreadSheet, WebharvestSpreadSheetRecord

class WebharvestChatMessage(admin.TabularInline):
    model = WebharvestChatMessage

class WebharvestThreadAdmin(admin.ModelAdmin):
    inlines = [WebharvestChatMessage]
    list_display = ('updated', 'human', 'message_count', 'spreadsheet')
    # list_filter = ('human')
    class Meta:
        model = WebharvestThread

admin.site.register(WebharvestThread, WebharvestThreadAdmin)

class WebharvestRobotAdmin(admin.ModelAdmin):
    model = WebharvestRobot

admin.site.register(WebharvestRobot, WebharvestRobotAdmin)

class WebharvestJobAdmin(admin.ModelAdmin):
    model = WebharvestJob

admin.site.register(WebharvestJob, WebharvestJobAdmin)


class WebharvestSpreadSheetRecord(admin.TabularInline):
    model = WebharvestSpreadSheetRecord

class WebharvestSpreadSheetAdmin(admin.ModelAdmin):
    model = WebharvestSpreadSheet
    inlines = [WebharvestSpreadSheetRecord]

admin.site.register(WebharvestSpreadSheet, WebharvestSpreadSheetAdmin)


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
