from django.contrib import admin

from users.models import Follow


class FollowAdmin(admin.ModelAdmin):
    list_display = ('__str__', )


admin.site.register(Follow, FollowAdmin)
