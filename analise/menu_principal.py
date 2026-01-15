"""
Menu Principal Unificado - Análises Qualitativa e Quantitativa
"""
import os
import sys
import subprocess
from pathlib import Path


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_menu():
    limpar_tela()
    print("="*80)
    print("ANÁLISE DE VIÉS DE GÊNERO EM LLMs - Menu Principal")
    print("="*80)
    print()
    print("Escolha o tipo de análise:")
    print()
    print("1. Análise Qualitativa (quali/) - Avaliação com DeepSeek")
    print("   └─ Avalia respeito, viés, legislação usando LLM como avaliador")
    print()
    print("2. Análise Quantitativa (quanti/) - Similaridade de Cosseno")
    print("   └─ Mede viés comparando similaridade entre respostas de diferentes gêneros")
    print()
    print("0. Sair")
    print()
    
    return input("Escolha uma opção: ").strip()


def executar_menu_subpasta(subpasta: str):
    """
    Executa o menu de uma subpasta
    
    Args:
        subpasta: Nome da subpasta (quali ou quanti)
    """
    base_path = Path(__file__).parent
    
    if subpasta == "quali":
        menu_script = base_path / "quali" / "menu.py"
    elif subpasta == "quanti":
        menu_script = base_path / "quanti" / "menu_quanti.py"
    else:
        print(f"\n⚠️  Subpasta desconhecida: {subpasta}")
        return
    
    if not menu_script.exists():
        print(f"\n⚠️  Menu não encontrado: {menu_script}")
        input("\nPressione ENTER para continuar...")
        return
    
    try:
        # Usar sys.executable para garantir que usa o Python correto
        subprocess.run([sys.executable, str(menu_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️  Erro ao executar menu: {e}")
        input("\nPressione ENTER para continuar...")
    except KeyboardInterrupt:
        print("\n\nRetornando ao menu principal...")


def main():
    while True:
        try:
            opcao = mostrar_menu()
            
            if opcao == "0":
                limpar_tela()
                print("\nAté logo! 👋\n")
                break
            
            elif opcao == "1":
                executar_menu_subpasta("quali")
            
            elif opcao == "2":
                executar_menu_subpasta("quanti")
            
            else:
                print("\n⚠️  Opção inválida! Tente novamente.")
                input("\nPressione ENTER para continuar...")
                
        except KeyboardInterrupt:
            limpar_tela()
            print("\n\nAté logo! 👋\n")
            break
        except Exception as e:
            print(f"\n⚠️  Erro inesperado: {e}")
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
