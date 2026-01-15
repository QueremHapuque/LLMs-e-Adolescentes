"""
Teste rápido do sistema de análise quantitativa
Verifica se todas as dependências estão instaladas
"""

import sys
from pathlib import Path


def verificar_modulo(nome_modulo, nome_display=None):
    """Verifica se um módulo está instalado"""
    if nome_display is None:
        nome_display = nome_modulo
    
    try:
        __import__(nome_modulo)
        print(f"  ✓ {nome_display}")
        return True
    except ImportError:
        print(f"  ✗ {nome_display} (não instalado)")
        return False


def verificar_arquivos():
    """Verifica se os arquivos necessários existem"""
    arquivos = [
        "quantitativa.py",
        "visualizar_quanti.py",
        "menu_quanti.py",
        "requirements.txt"
    ]
    
    print("\n2. Verificando arquivos do projeto:")
    base_path = Path(__file__).parent
    todos_ok = True
    
    for arquivo in arquivos:
        caminho = base_path / arquivo
        if caminho.exists():
            print(f"  ✓ {arquivo}")
        else:
            print(f"  ✗ {arquivo} (não encontrado)")
            todos_ok = False
    
    return todos_ok


def verificar_planilhas():
    """Verifica se as planilhas existem"""
    base_path = Path(__file__).parent.parent.parent
    
    planilhas = [
        ("INTIMA", "Chat GPT - INTIMA.xlsx"),
        ("INTIMA", "Grok - INTIMA.xlsx"),
        ("INTIMA", "Gemini - INTIMA.xlsx"),
        ("Safe Child LLM", "Chat GPT - Safe Child LLM.xlsx"),
        ("Safe Child LLM", "Grok - Safe Child LLM.xlsx"),
        ("Safe Child LLM", "Gemini - Safe Child LLM.xlsx"),
    ]
    
    print("\n3. Verificando planilhas de dados:")
    total = 0
    encontradas = 0
    
    for pasta, arquivo in planilhas:
        total += 1
        caminho = base_path / pasta / arquivo
        if caminho.exists():
            print(f"  ✓ {pasta}/{arquivo}")
            encontradas += 1
        else:
            print(f"  ✗ {pasta}/{arquivo} (não encontrado)")
    
    print(f"\n  Total: {encontradas}/{total} planilhas encontradas")
    return encontradas > 0


def teste_rapido():
    """Executa um teste rápido de cálculo de similaridade"""
    print("\n4. Teste rápido de funcionalidade:")
    
    try:
        from sentence_transformers import SentenceTransformer, util
        
        print("  • Carregando modelo...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("  • Calculando embeddings...")
        respostas = [
            "Você pode solicitar a retificação de nome em cartório com autorização dos pais.",
            "É possível mudar o nome civilmente aos 16 anos com consentimento dos responsáveis."
        ]
        embeddings = model.encode(respostas)
        
        print("  • Calculando similaridade...")
        sim = util.cos_sim(embeddings[0], embeddings[1]).item()
        
        print(f"  ✓ Similaridade calculada: {sim:.4f}")
        
        if sim > 0.5:
            print("  ✓ Sistema funcionando corretamente!")
        else:
            print("  ⚠️  Similaridade baixa (esperado > 0.5)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erro no teste: {e}")
        return False


def main():
    print("="*80)
    print("TESTE RÁPIDO - ANÁLISE QUANTITATIVA")
    print("="*80)
    
    # 1. Verificar dependências
    print("\n1. Verificando dependências Python:")
    dependencias = [
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("tqdm", "tqdm"),
        ("sentence_transformers", "sentence-transformers"),
        ("torch", "torch")
    ]
    
    todas_instaladas = True
    faltando = []
    
    for modulo, display in dependencias:
        if not verificar_modulo(modulo, display):
            todas_instaladas = False
            faltando.append(display)
    
    # 2. Verificar arquivos
    arquivos_ok = verificar_arquivos()
    
    # 3. Verificar planilhas
    planilhas_ok = verificar_planilhas()
    
    # 4. Teste funcional
    if todas_instaladas:
        teste_ok = teste_rapido()
    else:
        print("\n4. Teste rápido de funcionalidade:")
        print("  ⚠️  Pulado (instale as dependências primeiro)")
        teste_ok = False
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    
    if todas_instaladas:
        print("\n✓ Todas as dependências estão instaladas")
    else:
        print(f"\n✗ Faltam {len(faltando)} dependências:")
        for dep in faltando:
            print(f"  • {dep}")
        print("\nPara instalar:")
        print("  pip install -r requirements.txt")
    
    if arquivos_ok:
        print("✓ Todos os arquivos do projeto estão presentes")
    else:
        print("✗ Alguns arquivos do projeto estão faltando")
    
    if planilhas_ok:
        print("✓ Planilhas de dados encontradas")
    else:
        print("✗ Nenhuma planilha encontrada (verifique as pastas INTIMA e Safe Child LLM)")
    
    if teste_ok:
        print("✓ Teste funcional passou")
        print("\n" + "="*80)
        print("🎉 SISTEMA PRONTO PARA USO!")
        print("="*80)
        print("\nExecute: python menu_quanti.py")
    else:
        print("✗ Teste funcional falhou")
        print("\n" + "="*80)
        print("⚠️  SISTEMA NÃO ESTÁ PRONTO")
        print("="*80)
        print("\nResolva os problemas acima antes de usar.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido.")
    except Exception as e:
        print(f"\n⚠️  Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
