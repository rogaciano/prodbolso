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
