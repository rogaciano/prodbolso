-- Script para adicionar a coluna cor_linha à tabela ordens_servico_itemordemservico no banco de produção
-- Este script é compatível com PostgreSQL

-- Verificar se a coluna já existe antes de tentar adicioná-la
DO $$
BEGIN
    -- Verificar se a coluna já existe
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'ordens_servico_itemordemservico' 
        AND column_name = 'cor_linha'
    ) THEN
        -- Adicionar a coluna cor_linha se ela não existir
        ALTER TABLE ordens_servico_itemordemservico 
        ADD COLUMN cor_linha VARCHAR(100) DEFAULT '' NOT NULL;
        
        -- Registrar a alteração no log
        RAISE NOTICE 'Coluna cor_linha adicionada com sucesso à tabela ordens_servico_itemordemservico';
    ELSE
        -- Informar que a coluna já existe
        RAISE NOTICE 'A coluna cor_linha já existe na tabela ordens_servico_itemordemservico';
    END IF;
END $$;

-- Verificar se a coluna foi adicionada corretamente
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'ordens_servico_itemordemservico' 
AND column_name = 'cor_linha';

-- Para SQLite (caso o banco de produção seja SQLite):
-- 
-- PRAGMA foreign_keys=off;
-- 
-- BEGIN TRANSACTION;
-- 
-- -- Verificar se a coluna já existe (SQLite não tem information_schema)
-- -- Adicionar a coluna cor_linha
-- ALTER TABLE ordens_servico_itemordemservico ADD COLUMN cor_linha TEXT DEFAULT '' NOT NULL;
-- 
-- COMMIT;
-- 
-- PRAGMA foreign_keys=on;
