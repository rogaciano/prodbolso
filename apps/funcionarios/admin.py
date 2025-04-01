from django.contrib import admin
from .models import Funcionario

# Register your models here.

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'contato', 'email', 'data_admissao', 'ativo')
    list_filter = ('ativo', 'data_admissao')
    search_fields = ('nome', 'email', 'contato')
    date_hierarchy = 'data_admissao'
