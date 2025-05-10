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

/**
 * Função para atualizar tanto o valor unitário quanto o custo de produção
 * com base no tipo de bolso selecionado
 * 
 * @param {number} tipoBolsoId - ID do tipo de bolso selecionado
 */
function atualizarValorECusto(tipoBolsoId) {
    if (!tipoBolsoId) return;
    
    console.log("Buscando valores para o tipo de bolso ID:", tipoBolsoId);
    
    // Primeiro tentamos a nova API
    fetch(`/api/tipos-bolso/${tipoBolsoId}/`)
        .then(response => {
            if (!response.ok) {
                // Se a nova API falhar, tentamos a API antiga
                return fetch(`/api/catalogo/tipos-bolso/${tipoBolsoId}/`);
            }
            return response;
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta da API: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Dados recebidos da API:", data);
            
            // Atualizar o campo de valor unitário
            const valorUnitarioField = document.getElementById('id_valor_unitario');
            if (valorUnitarioField) {
                valorUnitarioField.value = data.valor_padrao || data.valor_unitario || 0;
                console.log("Valor unitário atualizado para:", valorUnitarioField.value);
            }
            
            // Atualizar o campo de custo de produção
            const custoProdField = document.getElementById('id_custo_producao');
            if (custoProdField) {
                custoProdField.value = data.custo_producao || 0;
                custoProdField.setAttribute('readonly', 'readonly');
                custoProdField.classList.add('bg-gray-100');
                console.log("Custo de produção atualizado para:", custoProdField.value);
            }
            
            // Recalcular subtotal e valor de produção se as funções existirem
            if (typeof calcularSubtotal === 'function') {
                calcularSubtotal();
            }
            
            if (typeof calcularValorProducao === 'function') {
                calcularValorProducao();
            }
        })
        .catch(error => {
            console.error('Erro ao obter valores do tipo de bolso:', error);
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
            // Se já tiver um valor selecionado, atualizar o valor unitário e o custo de produção
            atualizarValorECusto(tipoBolsoSelect.value);
        }
        
        // Adicionar evento onchange para atualizar o valor unitário e o custo de produção quando o tipo de bolso mudar
        tipoBolsoSelect.addEventListener('change', function() {
            console.log("Tipo de bolso alterado para:", this.value);
            atualizarValorECusto(this.value);
        });
    } else {
        console.log("Select de tipo de bolso não encontrado");
    }
});
