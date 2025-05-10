/**
 * Script para gerenciar o formulário de transações financeiras
 */
document.addEventListener('DOMContentLoaded', function() {
    const tipoField = document.getElementById('id_tipo');
    const categoriaField = document.getElementById('id_categoria');
    
    if (tipoField && categoriaField) {
        console.log("Campos de tipo e categoria encontrados");
        
        // Definir as categorias disponíveis para cada tipo
        const categorias = {
            'receita': [
                ['ordem_servico', 'Ordem de Serviço'],
                ['outros', 'Outros']
            ],
            'despesa': [
                ['materiais', 'Materiais'],
                ['salarios', 'Salários'],
                ['aluguel', 'Aluguel'],
                ['agua_luz', 'Água/Luz'],
                ['equipamentos', 'Equipamentos'],
                ['outros', 'Outros']
            ]
        };
        
        // Função para atualizar as opções de categoria
        function atualizarCategorias() {
            const tipo = tipoField.value;
            console.log("Tipo selecionado:", tipo);
            
            // Salvar a categoria selecionada atual, se houver
            const categoriaAtual = categoriaField.value;
            console.log("Categoria atual:", categoriaAtual);
            
            // Limpar as opções atuais
            categoriaField.innerHTML = '';
            
            // Adicionar as novas opções com base no tipo
            if (tipo && categorias[tipo]) {
                categorias[tipo].forEach(function(categoria) {
                    const option = document.createElement('option');
                    option.value = categoria[0];
                    option.textContent = categoria[1];
                    categoriaField.appendChild(option);
                });
                
                // Tentar restaurar a categoria selecionada, se ainda for válida
                if (categoriaAtual) {
                    const opcaoExistente = Array.from(categoriaField.options).find(option => option.value === categoriaAtual);
                    if (opcaoExistente) {
                        categoriaField.value = categoriaAtual;
                    }
                }
            }
        }
        
        // Atualizar as categorias quando o tipo mudar
        tipoField.addEventListener('change', atualizarCategorias);
        
        // Atualizar as categorias na inicialização
        atualizarCategorias();
    } else {
        console.log("Campos de tipo ou categoria não encontrados");
    }
});
