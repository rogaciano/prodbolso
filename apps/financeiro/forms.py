from django import forms
from .models import Transacao

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'tipo', 'categoria', 'valor', 'data', 'ordem_servico', 'observacoes', 'comprovante']
        widgets = {
            # limitar observações a uma linha
            'observacoes': forms.Textarea(attrs={
                'rows': 1,
                'class': 'resize-none h-8'
            }),
        }

# Formulário de teste simplificado para diagnóstico
class TransacaoTesteForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'tipo', 'valor', 'data']
        
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
