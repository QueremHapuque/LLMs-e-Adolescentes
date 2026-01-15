# 🚀 Guia Rápido de Instalação - Análise Quantitativa

## Passo 1: Navegar para a pasta

```powershell
cd "D:\Querem 2.0\Estudos\Faculdade\TCC\LLMs-e-Adolescentes\analise\quanti"
```

## Passo 2: Instalar dependências

```powershell
pip install -r requirements.txt
```

**Dependências principais:**
- `sentence-transformers` - Para cálculo de embeddings e similaridade
- `pandas` e `openpyxl` - Para manipulação de planilhas
- `matplotlib` e `seaborn` - Para visualizações
- `scipy` - Para estatísticas (IC 95%)
- `torch` - Backend para SentenceTransformers

**Nota**: Na primeira execução, o modelo `all-MiniLM-L6-v2` (~80MB) será baixado automaticamente.

## Passo 3: Executar o menu

```powershell
python menu_quanti.py
```

## Opções do Menu

```
1. Analisar uma planilha (calcular similaridade)
   └─ Selecione qual LLM e benchmark analisar (1-6)
   └─ Aguarde o processamento (2-5 minutos por planilha)
   └─ Resultados salvos em resultados/

2. Gerar visualizações (consolidar e plotar gráficos)
   └─ Consolida todas as análises já feitas
   └─ Gera 9 gráficos PNG em resultados/visualizacoes/

3. Ver resultados (abrir pasta)
   └─ Abre o explorador de arquivos na pasta resultados/

0. Sair
```

## Fluxo de Trabalho Típico

### Primeira Execução
```
1. Instalar dependências (uma vez)
2. Executar menu
3. Escolher opção 1 → Analisar primeira planilha
4. Aguardar conclusão
```

### Análises Subsequentes
```
1. Executar menu
2. Escolher opção 1 → Analisar outra planilha
3. Repetir para todas as 6 planilhas
4. Escolher opção 2 → Gerar visualizações consolidadas
5. Escolher opção 3 → Ver resultados
```

## Estrutura de Saída

```
resultados/
├── similaridade_ChatGPT_INTIMA_20250115_143022.xlsx
├── similaridade_Grok_INTIMA_20250115_143530.xlsx
├── similaridade_Gemini_INTIMA_20250115_144015.xlsx
├── similaridade_ChatGPT_Safe_Child_LLM_20250115_144520.xlsx
├── similaridade_Grok_Safe_Child_LLM_20250115_145040.xlsx
├── similaridade_Gemini_Safe_Child_LLM_20250115_145550.xlsx
├── relatorio_quantitativo_20250115_150000.txt
└── visualizacoes/
    ├── resumo_geral_similaridade.png
    ├── comparacao_llms_INTIMA.png
    ├── comparacao_llms_Safe_Child_LLM.png
    ├── distribuicao_similaridade_INTIMA.png
    ├── distribuicao_similaridade_Safe_Child_LLM.png
    ├── perguntas_criticas_INTIMA.png
    ├── perguntas_criticas_Safe_Child_LLM.png
    ├── evolucao_perguntas_INTIMA.png
    └── evolucao_perguntas_Safe_Child_LLM.png
```

## Tempos Estimados

| Ação | Tempo |
|------|-------|
| Instalação de dependências | 2-3 minutos |
| Download do modelo (primeira vez) | 1-2 minutos |
| Análise de 1 planilha (50 perguntas) | 2-5 minutos |
| Geração de todas as visualizações | 30-60 segundos |

**Total para análise completa** (6 planilhas + visualizações): ~20-30 minutos

## Resolução de Problemas

### "ModuleNotFoundError: No module named 'sentence_transformers'"
```powershell
pip install sentence-transformers
```

### "torch is not available"
```powershell
pip install torch
```

### "Memory Error"
- Feche outros programas
- Analise uma planilha por vez
- O modelo usa ~500MB de RAM

### Processo muito lento
- Normal na primeira execução (download do modelo)
- CPU é suficiente, mas GPU acelera (opcional)

## Menu Principal Unificado

Para acessar tanto análise quali quanto quanti:

```powershell
cd "D:\Querem 2.0\Estudos\Faculdade\TCC\LLMs-e-Adolescentes\analise"
python menu_principal.py
```

```
1. Análise Qualitativa (quali/) - Avaliação com DeepSeek
2. Análise Quantitativa (quanti/) - Similaridade de Cosseno
0. Sair
```

## Dúvidas?

Consulte o [README.md](README.md) para detalhes sobre metodologia e interpretação dos resultados.
