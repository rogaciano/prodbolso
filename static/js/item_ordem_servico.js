/**
 * Função para atualizar o valor unitário com base no tipo de bolso selecionado
 * 
 * @param {number} tipoBolsoId - ID do tipo de bolso selecionado
 */
function atualizarValorUnitario(tipoBolsoId) {
    if (!tipoBolsoId) return;
    
    console.log("Buscando valor padrão para o tipo de bolso ID:", tipoBolsoId);
    
    // Fazer uma requisição AJAX para obter o valor padrão do tipo de bolso
    fetch(`/api/catalogo/tipos-bolso/${tipoBolsoId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta da API: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Dados recebidos da API:", data);
            // Atualizar o campo de valor unitário com o valor padrão
            document.getElementById('id_valor_unitario').value = data.valor_padrao;
            console.log("Valor unitário atualizado para:", data.valor_padrao);
        })
        .catch(error => {
            console.error('Erro ao obter valor padrão:', error);
        });
}

// Quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado, inicializando script de item de ordem de serviço");
    
    // Verificar se estamos em uma página de criação (não de edição)
    const tipoBolsoSelect = document.getElementById('id_tipo_bolso');
    if (tipoBolsoSelect) {
        console.log("Select de tipo de bolso encontrado");
        
        if (tipoBolsoSelect.value) {
            console.log("Tipo de bolso já selecionado:", tipoBolsoSelect.value);
            // Se já tiver um valor selecionado, atualizar o valor unitário
            atualizarValorUnitario(tipoBolsoSelect.value);
        }
        
        // Adicionar evento onchange para atualizar o valor unitário quando o tipo de bolso mudar
        tipoBolsoSelect.addEventListener('change', function() {
            console.log("Tipo de bolso alterado para:", this.value);
            atualizarValorUnitario(this.value);
        });
    } else {
        console.log("Select de tipo de bolso não encontrado");
    }
});
