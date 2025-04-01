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
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        fields = ['tipo_bolso', 'quantidade', 'valor_unitario']
        widgets = {
            'tipo_bolso': forms.Select(attrs={'onchange': 'atualizarValorUnitario(this.value)'}),
            'valor_unitario': forms.NumberInput(attrs={'step': '0.01'}),
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
