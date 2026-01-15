"""
Script para análise rápida de uma única planilha
Útil para testar o sistema antes de processar todas as planilhas
"""

import os
from pathlib import Path
from analyzer import LLMBiasAnalyzer
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    print("="*80)
    print("TESTE RÁPIDO - Análise de Viés de Gênero")
    print("="*80)
    
    # Verificar API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("\n❌ ERRO: Configure a variável DEEPSEEK_API_KEY no arquivo .env")
        print("Copie .env.example para .env e adicione sua chave")
        return
    
    print("\n✓ API Key configurada")
    
    # Selecionar planilha para teste
    print("\nSelecione a planilha para testar:")
    print("1. ChatGPT - INTIMA")
    print("2. ChatGPT - Safe Child LLM")
    print("3. Grok - INTIMA")
    print("4. Grok - Safe Child LLM")
    print("5. Gemini - INTIMA")
    print("6. Gemini - Safe Child LLM")
    
    escolha = input("\nDigite o número (1-6): ").strip()
    
    planilhas = {
        "1": ("INTIMA/Chat GPT - INTIMA.xlsx", "ChatGPT", "INTIMA"),
        "2": ("Safe Child LLM/Chat GPT - Safe Child LLM.xlsx", "ChatGPT", "Safe Child LLM"),
        "3": ("INTIMA/Grok - INTIMA.xlsx", "Grok", "INTIMA"),
        "4": ("Safe Child LLM/Grok - Safe Child LLM.xlsx", "Grok", "Safe Child LLM"),
        "5": ("INTIMA/Gemini - INTIMA.xlsx", "Gemini", "INTIMA"),
        "6": ("Safe Child LLM/Gemini - Safe Child LLM.xlsx", "Gemini", "Safe Child LLM"),
    }
    
    if escolha not in planilhas:
        print("❌ Opção inválida!")
        return
    
    caminho_rel, llm, benchmark = planilhas[escolha]
    
    # Construir caminho completo
    base_path = Path(__file__).parent.parent
    caminho_completo = base_path / caminho_rel
    
    if not caminho_completo.exists():
        print(f"\n❌ Arquivo não encontrado: {caminho_completo}")
        return
    
    print(f"\n✓ Planilha selecionada: {llm} - {benchmark}")
    print(f"Caminho: {caminho_completo}")
    
    # Perguntar quantas perguntas analisar
    print("\nQuantas perguntas você quer analisar? (padrão: 5)")
    num_perguntas = input("Digite o número ou Enter para 5: ").strip()
    
    try:
        num_perguntas = int(num_perguntas) if num_perguntas else 5
    except ValueError:
        num_perguntas = 5
    
    print(f"\n✓ Analisando primeiras {num_perguntas} perguntas")
    
    # Confirmar antes de começar
    print("\n⚠️  Isso consumirá créditos da API DeepSeek")
    print(f"Estimativa: {num_perguntas * 5} análises (5 personas por pergunta)")
    confirma = input("\nDeseja continuar? (s/N): ").strip().lower()
    
    if confirma != 's':
        print("Cancelado pelo usuário.")
        return
    
    # Criar analisador
    print("\n" + "="*80)
    print("INICIANDO ANÁLISE...")
    print("="*80 + "\n")
    
    analyzer = LLMBiasAnalyzer(api_key)
    
    # Processar planilha (limitado)
    import pandas as pd
    df = pd.read_excel(str(caminho_completo))
    
    # DEBUG: Mostrar informações da planilha
    print("\n📋 Informações da planilha:")
    print(f"Colunas encontradas: {list(df.columns)}")
    print(f"Total de linhas: {len(df)}")
    print("\nPrimeiras linhas:")
    print(df.head(2))
    print("\n" + "="*80)
    
    df_limitado = df.head(num_perguntas)
    
    # Salvar temporariamente
    temp_file = Path(__file__).parent / "temp_test.xlsx"
    df_limitado.to_excel(temp_file, index=False)
    
    # Processar
    resultado = analyzer.processar_planilha(str(temp_file), llm, benchmark)
    
    # Remover arquivo temporário
    temp_file.unlink()
    
    # Salvar resultado
    output_path = Path(__file__).parent / "resultados"
    output_path.mkdir(exist_ok=True)
    
    output_file = output_path / f"teste_{llm}_{benchmark.replace(' ', '_')}.xlsx"
    resultado.to_excel(output_file, index=False)
    
    print("\n" + "="*80)
    print("✓ TESTE CONCLUÍDO!")
    print("="*80)
    print(f"\nResultado salvo em: {output_file}")
    print(f"Total de análises: {len(resultado)}")
    
    # Mostrar resumo rápido
    if 'vies_identificado' in resultado.columns:
        vies_sim = len(resultado[resultado['vies_identificado'] == 'sim'])
        vies_parcial = len(resultado[resultado['vies_identificado'] == 'parcial'])
        vies_nao = len(resultado[resultado['vies_identificado'] == 'não'])
        
        print(f"\nResumo:")
        print(f"  - Viés identificado: {vies_sim} ({vies_sim/len(resultado)*100:.1f}%)")
        print(f"  - Viés parcial: {vies_parcial} ({vies_parcial/len(resultado)*100:.1f}%)")
        print(f"  - Sem viés: {vies_nao} ({vies_nao/len(resultado)*100:.1f}%)")
    
    print(f"\nAbra o arquivo Excel para ver os detalhes completos.")

if __name__ == "__main__":
    main()
