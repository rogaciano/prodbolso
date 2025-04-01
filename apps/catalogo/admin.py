from django.contrib import admin
from .models import TipoBolso

# Register your models here.

@admin.register(TipoBolso)
class TipoBolsoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_padrao', 'tempo_estimado_producao')
    search_fields = ('nome', 'descricao')
    list_filter = ('valor_padrao',)
