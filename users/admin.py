from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserList, ListItem
# Register your models here.

admin.site.register(CustomUser, UserAdmin)


class ListItemInLine(admin.TabularInline):
    model = ListItem

@admin.register(UserList)
class UserListAdmin(admin.ModelAdmin):
    inlines = [ListItemInLine]

@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    pass