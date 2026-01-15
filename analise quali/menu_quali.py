"""
Menu principal - Análise de Viés de Gênero
"""
import os
import sys
import subprocess
from pathlib import Path


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def verificar_api_key():
    """Verifica se a API key está configurada"""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return False
    with open(env_file) as f:
        conteudo = f.read()
        return "DEEPSEEK_API_KEY=" in conteudo and "sua_chave_api_aqui" not in conteudo


def mostrar_menu():
    limpar_tela()
    print("="*60)
    print("ANÁLISE DE VIÉS DE GÊNERO EM LLMs")
    print("="*60)
    print()
    
    tem_api = verificar_api_key()
    if not tem_api:
        print("⚠️  API key não configurada (edite o arquivo .env)")
        print()
    
    print("1. Teste Rápido")
    print("2. Análise Completa" + (" (configure API key primeiro!)" if not tem_api else ""))
    print("3. Gerar Gráficos")
    print("4. Gerar Relatórios")
    print("0. Sair")
    print()
    
    return input("Escolha: ").strip()


def executar_script(script):
    """Executa um script Python"""
    base_path = Path(__file__).parent
    try:
        subprocess.run([sys.executable, script], cwd=str(base_path))
    except KeyboardInterrupt:
        print("\n\nInterrompido")
    except Exception as e:
        print(f"\nErro: {e}")
    
    input("\nEnter para continuar...")


def main():
    while True:
        opcao = mostrar_menu()
        
        if opcao == "0":
            limpar_tela()
            print("Até logo!\n")
            break
        
        elif opcao == "1":
            executar_script("teste_rapido.py")
        
        elif opcao == "2":
            if not verificar_api_key():
                print("\nConfigure a API key no arquivo .env primeiro!")
                input("\nEnter para continuar...")
            else:
                executar_script("analyzer.py")
        
        elif opcao == "3":
            executar_script("visualizar.py")
        
        elif opcao == "4":
            executar_script("relatorios.py")
        
        else:
            print("\nOpção inválida!")
            input("\nEnter para continuar...")


if __name__ == "__main__":
    main()
