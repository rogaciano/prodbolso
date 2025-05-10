from django import forms
from .models import OrdemServico, ItemOrdemServico, ProducaoOS
from django.utils.dateformat import format
from apps.catalogo.models import TipoBolso

class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ['cliente', 'ficha', 'data_entrega_prevista', 'observacoes']
        widgets = {
            'data_entrega_prevista': forms.DateInput(attrs={'type': 'date'}),
            # limitar observações a uma linha
            'observacoes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'resize-none h-8'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Em formulário novo, não mostrar '---------' como opção vazia no select de cliente
        if not self.instance.pk:
            self.fields['cliente'].empty_label = ''
        # Adicionar o campo status apenas para instâncias existentes (edição)
        if self.instance.pk:
            self.fields['status'] = forms.ChoiceField(
                choices=OrdemServico.STATUS_CHOICES,
                initial=self.instance.status
            )
            
            # Formatar a data para o formato ISO (YYYY-MM-DD) esperado pelo input type="date"
            if self.instance.data_entrega_prevista:
                self.initial['data_entrega_prevista'] = self.instance.data_entrega_prevista.strftime('%Y-%m-%d')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Definir valor_total como 0 inicialmente
        if not instance.pk:  # Se for uma nova instância
            instance.valor_total = 0
        if commit:
            instance.save()
        return instance

class ItemOrdemServicoForm(forms.ModelForm):
    class Meta:
        model = ItemOrdemServico
        fields = ['tipo_bolso', 'cor_linha', 'quantidade', 'valor_unitario', 'custo_producao']
        widgets = {
            'tipo_bolso': forms.Select(attrs={'onchange': 'atualizarValorECusto(this.value)'}),
            'valor_unitario': forms.NumberInput(attrs={'step': '0.01'}),
            'custo_producao': forms.NumberInput(attrs={'step': '0.01', 'readonly': True, 'class': 'bg-gray-100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se não for uma edição (nova instância), não definir valor inicial
        if not self.instance.pk:
            self.fields['valor_unitario'].initial = None
    
    class Media:
        js = ('js/item_ordem_servico.js',)

class ProducaoOSForm(forms.ModelForm):
    class Meta:
        model = ProducaoOS
        fields = ['funcionario', 'data_inicio']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Oculta input de data_inicio e define valor inicial para hoje
            from django.forms import HiddenInput
            from django.utils import timezone
            self.fields['data_inicio'].widget = HiddenInput()
            self.initial['data_inicio'] = timezone.now().date()
