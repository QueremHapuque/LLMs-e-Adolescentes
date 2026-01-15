"""
Menu Principal - Análise Quantitativa
Sistema de análise de viés de gênero por similaridade de cosseno
"""

import sys
import subprocess
from pathlib import Path


def executar_script(script_nome: str):
    """
    Executa um script Python usando o interpretador correto do venv
    
    Args:
        script_nome: Nome do arquivo .py a executar
    """
    script_path = Path(__file__).parent / script_nome
    
    if not script_path.exists():
        print(f"\n⚠️  Script não encontrado: {script_path}")
        return
    
    try:
        # Usar sys.executable para garantir que usa o Python do venv
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️  Erro ao executar {script_nome}: {e}")
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")


def mostrar_menu():
    """Exibe o menu principal"""
    print("\n" + "="*80)
    print("ANÁLISE QUANTITATIVA - VIÉS DE GÊNERO POR SIMILARIDADE DE COSSENO")
    print("="*80)
    print("\nO que você deseja fazer?\n")
    print("1. Analisar uma planilha (calcular similaridade)")
    print("2. Gerar visualizações (consolidar e plotar gráficos)")
    print("3. Ver resultados (abrir pasta)")
    print("0. Sair")
    print()


def abrir_pasta_resultados():
    """Abre a pasta de resultados no explorador de arquivos"""
    resultados_path = Path(__file__).parent / "resultados"
    
    if not resultados_path.exists():
        print("\n⚠️  Pasta de resultados não existe ainda.")
        print("Execute primeiro uma análise (opção 1).")
        return
    
    try:
        import os
        if sys.platform == 'win32':
            os.startfile(resultados_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', resultados_path])
        else:  # linux
            subprocess.run(['xdg-open', resultados_path])
        
        print(f"\n✓ Pasta aberta: {resultados_path}")
    except Exception as e:
        print(f"\n⚠️  Erro ao abrir pasta: {e}")
        print(f"Caminho: {resultados_path}")


def main():
    """Função principal do menu"""
    while True:
        try:
            mostrar_menu()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                print("\n" + "="*80)
                executar_script("quantitativa.py")
                input("\nPressione ENTER para voltar ao menu...")
                
            elif opcao == "2":
                print("\n" + "="*80)
                executar_script("visualizar_quanti.py")
                input("\nPressione ENTER para voltar ao menu...")
                
            elif opcao == "3":
                abrir_pasta_resultados()
                input("\nPressione ENTER para voltar ao menu...")
                
            elif opcao == "0":
                print("\nSaindo...")
                break
                
            else:
                print("\n⚠️  Opção inválida! Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"\n⚠️  Erro inesperado: {e}")
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
