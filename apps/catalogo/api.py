from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import TipoBolso

def tipo_bolso_detail_api(request, pk):
    """
    API para obter os detalhes de um tipo de bolso, incluindo seu valor padrão
    """
    tipo_bolso = get_object_or_404(TipoBolso, pk=pk)
    data = {
        'id': tipo_bolso.id,
        'nome': tipo_bolso.nome,
        'valor_padrao': float(tipo_bolso.valor_padrao),
        'tempo_estimado_producao': str(tipo_bolso.tempo_estimado_producao) if tipo_bolso.tempo_estimado_producao else None
    }
    return JsonResponse(data)
