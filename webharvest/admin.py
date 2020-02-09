from django.contrib import admin


from .models import WebharvestThread, WebharvestChatMessage

class WebharvestChatMessage(admin.TabularInline):
    model = WebharvestChatMessage

class WebharvestThreadAdmin(admin.ModelAdmin):
    inlines = [WebharvestChatMessage]
    class Meta:
        model = WebharvestThread 


admin.site.register(WebharvestThread, WebharvestThreadAdmin)
