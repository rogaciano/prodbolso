from django.contrib import admin
from .models import Cliente

# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'contato', 'data_cadastro')
    list_filter = ('data_cadastro',)
    search_fields = ('nome', 'telefone', 'email', 'contato')
    date_hierarchy = 'data_cadastro'
