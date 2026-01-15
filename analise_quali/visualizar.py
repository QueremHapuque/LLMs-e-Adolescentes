"""
Script para visualização e comparação dos resultados da análise
Gera gráficos e estatísticas comparativas entre LLMs e personas
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class ResultsVisualizer:
    """Visualizador de resultados da análise de viés"""
    
    def __init__(self, arquivo_consolidado: str):
        """
        Inicializa o visualizador
        
        Args:
            arquivo_consolidado: Caminho para o arquivo consolidado
        """
        self.df = pd.read_excel(arquivo_consolidado)
        
        # Critérios Safe Child LLM
        self.criterios_safe_child = [
            "respeito_identidade",
            "acuracia_legislacao",
            "estereotipos_genero",
            "linguagem_inclusiva",
            "contexto_adolescencia"
        ]
        
        # Critérios INTIMA
        self.criterios_intima = [
            "limites_terapeuticos",
            "incentivo_amizade",
            "limites_romanticos",
            "autonomia_adolescente",
            "encaminhamento_adequado"
        ]
        
        # Labels para exibição
        self.labels_safe_child = [
            'Respeito à\nIdentidade',
            'Acurácia\nLegislação',
            'Ausência de\nEstereótipos',
            'Linguagem\nInclusiva',
            'Contexto\nAdolescência'
        ]
        
        self.labels_intima = [
            'Limites\nTerapêuticos',
            'Limites sobre\nAmizade',
            'Limites\nRomânticos',
            'Promoção de\nAutonomia',
            'Encaminhamento\nAdequado'
        ]
        
    def extrair_notas(self):
        """Extrai notas dos campos JSON"""
        import json
        
        # Extrair notas de todos os critérios possíveis
        todos_criterios = set(self.criterios_safe_child + self.criterios_intima)
        
        for criterio in todos_criterios:
            if criterio in self.df.columns:
                def extrair_nota(x):
                    if pd.isna(x):
                        return np.nan
                    
                    # Se já for dict, usar diretamente
                    if isinstance(x, dict):
                        return x.get('nota', np.nan)
                    
                    # Se for string, tentar parsear JSON
                    if isinstance(x, str):
                        try:
                            dados = json.loads(x.replace("'", '"'))
                            return dados.get('nota', np.nan)
                        except:
                            return np.nan
                    
                    return np.nan
                
                self.df[f'{criterio}_nota'] = self.df[criterio].apply(extrair_nota)
    
    def grafico_comparacao_llms(self, output_path: Path):
        """Gera gráficos comparando médias por LLM (separado por benchmark)"""
        
        # Separar por benchmark
        df_safe_child = self.df[self.df['benchmark'] == 'Safe Child LLM']
        df_intima = self.df[self.df['benchmark'] == 'INTIMA']
        
        # Gráfico Safe Child LLM
        if len(df_safe_child) > 0:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            medias = {}
            for llm in df_safe_child['llm'].unique():
                df_llm = df_safe_child[df_safe_child['llm'] == llm]
                medias[llm] = [df_llm[f'{c}_nota'].mean() for c in self.criterios_safe_child]
            
            x = np.arange(len(self.criterios_safe_child))
            width = 0.25
            cores = {'ChatGPT': '#10a37f', 'Grok': '#1DA1F2', 'Gemini': '#4285f4'}
            
            for i, (llm, notas) in enumerate(medias.items()):
                offset = width * (i - 1)
                ax.bar(x + offset, notas, width, label=llm, 
                       color=cores.get(llm, f'C{i}'), alpha=0.8)
            
            ax.set_ylabel('Nota Média (1-5)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Critérios', fontsize=12, fontweight='bold')
            ax.set_title('Safe Child LLM: Ética e Segurança por LLM', 
                         fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(self.labels_safe_child, rotation=0, ha='center')
            ax.legend(title='LLM', fontsize=11)
            ax.set_ylim(0, 5.5)
            ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, linewidth=1)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / 'comparacao_llms_safe_child.png', dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: comparacao_llms_safe_child.png")
            plt.close()
        
        # Gráfico INTIMA
        if len(df_intima) > 0:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            medias = {}
            for llm in df_intima['llm'].unique():
                df_llm = df_intima[df_intima['llm'] == llm]
                medias[llm] = [df_llm[f'{c}_nota'].mean() for c in self.criterios_intima]
            
            x = np.arange(len(self.criterios_intima))
            width = 0.25
            cores = {'ChatGPT': '#10a37f', 'Grok': '#1DA1F2', 'Gemini': '#4285f4'}
            
            for i, (llm, notas) in enumerate(medias.items()):
                offset = width * (i - 1)
                ax.bar(x + offset, notas, width, label=llm, 
                       color=cores.get(llm, f'C{i}'), alpha=0.8)
            
            ax.set_ylabel('Nota Média (1-5)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Critérios', fontsize=12, fontweight='bold')
            ax.set_title('INTIMA: Limites no Companheirismo de IA por LLM', 
                         fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(self.labels_intima, rotation=0, ha='center')
            ax.legend(title='LLM', fontsize=11)
            ax.set_ylim(0, 5.5)
            ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, linewidth=1)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / 'comparacao_llms_intima.png', dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: comparacao_llms_intima.png")
            plt.close()
    
    def grafico_comparacao_personas(self, output_path: Path):
        """Gera gráficos comparando médias por persona (separado por benchmark)"""
        
        # Função para normalizar nomes de personas
        def normalizar_persona(nome):
            nome_lower = nome.lower()
            if 'ana' in nome_lower and 'cis' in nome_lower:
                return "Ana\n(menina cis)"
            elif 'felipe' in nome_lower and 'cis' in nome_lower:
                return "Felipe\n(menino cis)"
            elif 'geovana' in nome_lower and 'trans' in nome_lower:
                return "Geovana\n(menina trans)"
            elif 'italo' in nome_lower or 'ítalo' in nome_lower:
                return "Italo\n(menino trans)"
            elif 'ariel' in nome_lower:
                return "Ariel\n(não-binário)"
            else:
                return nome.split(',')[0].strip()
        
        # Separar por benchmark
        df_safe_child = self.df[self.df['benchmark'] == 'Safe Child LLM']
        df_intima = self.df[self.df['benchmark'] == 'INTIMA']
        
        cores = ['#FF69B4', '#4169E1', '#FF1493', '#1E90FF', '#9370DB']
        
        # Gráfico Safe Child LLM
        if len(df_safe_child) > 0:
            fig, ax = plt.subplots(figsize=(14, 8))
            medias = {}
            
            for persona in df_safe_child['persona'].unique():
                df_persona = df_safe_child[df_safe_child['persona'] == persona]
                label = normalizar_persona(persona)
                medias[label] = [df_persona[f'{c}_nota'].mean() for c in self.criterios_safe_child]
            
            x = np.arange(len(self.criterios_safe_child))
            width = 0.15
            
            for i, (persona, notas) in enumerate(medias.items()):
                offset = width * (i - 2)
                ax.bar(x + offset, notas, width, label=persona, color=cores[i], alpha=0.8)
            
            ax.set_ylabel('Nota Média (1-5)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Critérios', fontsize=12, fontweight='bold')
            ax.set_title('Safe Child LLM: Ética e Segurança por Persona', 
                         fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(self.labels_safe_child, rotation=0, ha='center')
            ax.legend(title='Persona', fontsize=10, ncol=2)
            ax.set_ylim(0, 5.5)
            ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, linewidth=1)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / 'comparacao_personas_safe_child.png', dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: comparacao_personas_safe_child.png")
            plt.close()
        
        # Gráfico INTIMA
        if len(df_intima) > 0:
            fig, ax = plt.subplots(figsize=(14, 8))
            medias = {}
            
            for persona in df_intima['persona'].unique():
                df_persona = df_intima[df_intima['persona'] == persona]
                label = normalizar_persona(persona)
                medias[label] = [df_persona[f'{c}_nota'].mean() for c in self.criterios_intima]
            
            x = np.arange(len(self.criterios_intima))
            width = 0.15
            
            for i, (persona, notas) in enumerate(medias.items()):
                offset = width * (i - 2)
                ax.bar(x + offset, notas, width, label=persona, color=cores[i], alpha=0.8)
            
            ax.set_ylabel('Nota Média (1-5)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Critérios', fontsize=12, fontweight='bold')
            ax.set_title('INTIMA: Limites no Companheirismo por Persona', 
                         fontsize=14, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(self.labels_intima, rotation=0, ha='center')
            ax.legend(title='Persona', fontsize=10, ncol=2)
            ax.set_ylim(0, 5.5)
            ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, linewidth=1)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path / 'comparacao_personas_intima.png', dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: comparacao_personas_intima.png")
            plt.close()
    
    def grafico_vies_por_llm(self, output_path: Path):
        """Gera gráfico de pizza mostrando viés por LLM"""
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        llms = self.df['llm'].unique()
        cores = ['#ef4444', '#fbbf24', '#10b981']  # vermelho, amarelo, verde
        
        for i, llm in enumerate(llms):
            df_llm = self.df[self.df['llm'] == llm]
            
            # Contar viés
            vies_counts = df_llm['vies_identificado'].value_counts()
            
            # Criar pizza
            labels = []
            sizes = []
            colors = []
            
            if 'sim' in vies_counts:
                labels.append(f'Viés\nIdentificado\n({vies_counts["sim"]})')
                sizes.append(vies_counts['sim'])
                colors.append(cores[0])
            
            if 'parcial' in vies_counts:
                labels.append(f'Viés\nParcial\n({vies_counts["parcial"]})')
                sizes.append(vies_counts['parcial'])
                colors.append(cores[1])
            
            if 'não' in vies_counts:
                labels.append(f'Sem\nViés\n({vies_counts["não"]})')
                sizes.append(vies_counts['não'])
                colors.append(cores[2])
            
            axes[i].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                       startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
            axes[i].set_title(llm, fontsize=13, fontweight='bold', pad=15)
        
        plt.suptitle('Identificação de Viés por LLM', 
                     fontsize=15, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(output_path / 'vies_por_llm.png', dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico salvo: vies_por_llm.png")
        plt.close()
    
    def heatmap_criterios(self, output_path: Path):
        """Gera heatmaps de critérios por LLM (separado por benchmark)"""
        
        # Separar por benchmark
        df_safe_child = self.df[self.df['benchmark'] == 'Safe Child LLM']
        df_intima = self.df[self.df['benchmark'] == 'INTIMA']
        
        # Heatmap Safe Child LLM
        if len(df_safe_child) > 0:
            pivot_data = []
            for llm in df_safe_child['llm'].unique():
                df_llm = df_safe_child[df_safe_child['llm'] == llm]
                row = [df_llm[f'{c}_nota'].mean() for c in self.criterios_safe_child]
                pivot_data.append(row)
            
            df_pivot = pd.DataFrame(
                pivot_data,
                index=df_safe_child['llm'].unique(),
                columns=self.labels_safe_child
            )
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(df_pivot, annot=True, fmt='.2f', cmap='RdYlGn',
                       vmin=1, vmax=5, center=3, cbar_kws={'label': 'Nota (1-5)'},
                       linewidths=2, linecolor='white', ax=ax)
            
            ax.set_title('Safe Child LLM: Mapa de Calor - Ética e Segurança', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Critérios de Avaliação', fontsize=12, fontweight='bold')
            ax.set_ylabel('LLM', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(output_path / 'heatmap_safe_child.png', dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: heatmap_safe_child.png")
            plt.close()
        
        # Heatmap INTIMA
        if len(df_intima) > 0:
            pivot_data = []
            for llm in df_intima['llm'].unique():
                df_llm = df_intima[df_intima['llm'] == llm]
                row = [df_llm[f'{c}_nota'].mean() for c in self.criterios_intima]
                pivot_data.append(row)
            
            df_pivot = pd.DataFrame(
                pivot_data,
                index=df_intima['llm'].unique(),
                columns=self.labels_intima
            )
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(df_pivot, annot=True, fmt='.2f', cmap='RdYlGn',
                       vmin=1, vmax=5, center=3, cbar_kws={'label': 'Nota (1-5)'},
                       linewidths=2, linecolor='white', ax=ax)
            
            ax.set_title('INTIMA: Mapa de Calor - Limites no Companheirismo', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Critérios de Avaliação', fontsize=12, fontweight='bold')
            ax.set_ylabel('LLM', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(output_path / 'heatmap_intima.png', dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: heatmap_intima.png")
            plt.close()
    
    def gerar_todos_graficos(self, output_dir: str = "visualizacoes"):
        """Gera todos os gráficos"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("\n" + "="*80)
        print("GERANDO VISUALIZAÇÕES")
        print("="*80 + "\n")
        
        # Extrair notas
        print("Processando dados...")
        self.extrair_notas()
        
        # Gerar gráficos
        print("\nGerando gráficos:")
        self.grafico_comparacao_llms(output_path)
        self.grafico_comparacao_personas(output_path)
        self.grafico_vies_por_llm(output_path)
        self.heatmap_criterios(output_path)
        
        print("\n" + "="*80)
        print(f"✓ VISUALIZAÇÕES CONCLUÍDAS!")
        print("="*80)
        print(f"\nGráficos salvos em: {output_path.absolute()}")


def main():
    """Função principal"""
    print("="*80)
    print("VISUALIZADOR DE RESULTADOS - Análise de Viés de Gênero")
    print("="*80)
    
    # Procurar arquivo consolidado mais recente
    resultados_path = Path(__file__).parent / "resultados"
    
    if not resultados_path.exists():
        print("\n❌ Pasta 'resultados' não encontrada!")
        print("Execute primeiro o analyzer.py para gerar as análises.")
        return
    
    # Buscar arquivos de análise (consolidados ou individuais)
    arquivos_analise = list(resultados_path.glob("analise_*.xlsx"))
    
    if not arquivos_analise:
        print("\n❌ Nenhum arquivo de análise encontrado!")
        print("Execute primeiro o analyzer.py para gerar as análises.")
        return
    
    # Verificar se há arquivo consolidado
    arquivos_consolidados = [a for a in arquivos_analise if "consolidada" in a.name.lower()]
    
    if arquivos_consolidados:
        # Usar consolidado se existir
        arquivo_selecionado = max(arquivos_consolidados, key=lambda p: p.stat().st_mtime)
        print(f"\n✓ Usando arquivo consolidado: {arquivo_selecionado.name}")
    else:
        # Consolidar automaticamente
        print(f"\n📊 Encontradas {len(arquivos_analise)} análises individuais")
        print("Consolidando todas as análises...")
        
        df_consolidado = pd.concat([pd.read_excel(f) for f in arquivos_analise], ignore_index=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_selecionado = resultados_path / f"analise_consolidada_{timestamp}.xlsx"
        df_consolidado.to_excel(arquivo_selecionado, index=False)
        
        print(f"✓ Consolidado salvo: {arquivo_selecionado.name}")
    
    print(f"Total de registros: {len(pd.read_excel(arquivo_selecionado))}")
    
    # Criar visualizador
    visualizer = ResultsVisualizer(str(arquivo_selecionado))
    
    # Gerar gráficos
    output_dir = resultados_path / "visualizacoes"
    visualizer.gerar_todos_graficos(str(output_dir))
    
    print(f"\nAbra a pasta para visualizar os gráficos:")
    print(f"📊 {output_dir.absolute()}")


if __name__ == "__main__":
    main()
