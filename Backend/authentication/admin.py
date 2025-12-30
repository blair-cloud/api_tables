from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created', 'last_used', 'is_active')
    list_filter = ('created', 'is_active')
    search_fields = ('user__username', 'key')
    readonly_fields = ('key', 'created')
    
    fieldsets = (
        ('Key Information', {
            'fields': ('key', 'user')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created', 'last_used'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent direct addition through admin, use management command instead
        return False

    def has_delete_permission(self, request, obj=None):
        return True
