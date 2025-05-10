from django import forms
from .models import Transacao

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'tipo', 'categoria', 'forma_pagamento', 'valor', 'data', 'ordem_servico', 'observacoes', 'comprovante']
        widgets = {
            # limitar observações a uma linha
            'observacoes': forms.Textarea(attrs={
                'rows': 1,
                'class': 'resize-none h-8'
            }),
        }
        
    class Media:
        js = ('js/transacao_form.js',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar categorias com base no tipo selecionado
        tipo = None
        if self.data.get('tipo'):
            tipo = self.data.get('tipo')
        elif self.instance and self.instance.pk:
            tipo = self.instance.tipo
            
        if tipo == 'receita':
            self.fields['categoria'].choices = Transacao.CATEGORIA_RECEITA_CHOICES
        elif tipo == 'despesa':
            self.fields['categoria'].choices = Transacao.CATEGORIA_DESPESA_CHOICES

# Formulário de teste simplificado para diagnóstico
class TransacaoTesteForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'tipo', 'valor', 'data', 'forma_pagamento']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir valores padrão para campos não incluídos
        if not self.is_bound:  # Apenas para novos formulários
            self.initial['categoria'] = 'outros'
            
    def clean(self):
        cleaned_data = super().clean()
        # Definir categoria com base no tipo
        tipo = cleaned_data.get('tipo')
        if tipo == 'receita':
            cleaned_data['categoria'] = 'outros'
        elif tipo == 'despesa':
            cleaned_data['categoria'] = 'outros'
        return cleaned_data
