from django.forms import inlineformset_factory
from .models import OrdemServico, ItemOrdemServico
from .forms import ItemOrdemServicoForm

ItemOrdemServicoFormSet = inlineformset_factory(
    OrdemServico,
    ItemOrdemServico,
    form=ItemOrdemServicoForm,
    extra=1,
    can_delete=True
)
