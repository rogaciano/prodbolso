from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'contato', 'email', 'data_admissao', 'ativo']
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.data_admissao:
            self.fields['data_admissao'].initial = self.instance.data_admissao.strftime('%Y-%m-%d')
