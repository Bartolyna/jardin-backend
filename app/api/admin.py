from django.contrib import admin
from .models import Fundacion


@admin.register(Fundacion)
class FundacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nombre', 'email')
    readonly_fields = ('created_at', 'updated_at')