"""
Visualização dos Resultados da Análise Quantitativa
Gera gráficos comparativos de similaridade de cosseno
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict
from scipy import stats
import glob


class VisualizadorQuantitativo:
    """Gerador de visualizações para análise quantitativa"""
    
    def __init__(self):
        """Inicializa o visualizador"""
        # Configurar estilo
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        # Cores por LLM
        self.cores_llm = {
            'ChatGPT': '#10A37F',
            'Gemini': '#4285F4',
            'Grok': '#1DA1F2'
        }
    
    def consolidar_analises(self, caminho_resultados: Path) -> pd.DataFrame:
        """
        Consolida múltiplas análises em um único DataFrame
        
        Args:
            caminho_resultados: Caminho para pasta com resultados
            
        Returns:
            DataFrame consolidado
        """
        print("\nConsolidando análises...")
        
        # Buscar todos os arquivos de similaridade
        arquivos = list(caminho_resultados.glob("similaridade_*.xlsx"))
        
        if not arquivos:
            print("⚠️  Nenhum arquivo de análise encontrado!")
            return None
        
        # Consolidar
        dfs = []
        for arquivo in arquivos:
            try:
                df = pd.read_excel(arquivo)
                dfs.append(df)
                print(f"  ✓ {arquivo.name}")
            except Exception as e:
                print(f"  ✗ Erro ao ler {arquivo.name}: {e}")
        
        if not dfs:
            return None
        
        df_consolidado = pd.concat(dfs, ignore_index=True)
        print(f"\n✓ Consolidado: {len(df_consolidado)} registros de {len(dfs)} arquivos")
        
        return df_consolidado
    
    def grafico_comparacao_llms(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Gráfico de barras comparando similaridade média entre LLMs
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Calcular métricas por LLM
        resultados = []
        for llm in df_bench['llm'].unique():
            df_llm = df_bench[df_bench['llm'] == llm]
            df_valido = df_llm[df_llm['num_comparacoes'] > 0]
            
            if len(df_valido) == 0:
                continue
            
            # Pegar todas as similaridades
            todas_sims = []
            for sims in df_valido['similaridades']:
                if sims:
                    todas_sims.extend(sims)
            
            if todas_sims:
                media = np.mean(todas_sims)
                erro_padrao = stats.sem(todas_sims)
                ic = stats.t.interval(0.95, len(todas_sims)-1, loc=media, scale=erro_padrao)
                
                resultados.append({
                    'llm': llm,
                    'media': media,
                    'erro_inf': media - ic[0],
                    'erro_sup': ic[1] - media
                })
        
        if not resultados:
            return
        
        df_plot = pd.DataFrame(resultados)
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(df_plot))
        bars = ax.bar(x, df_plot['media'], 
                      color=[self.cores_llm[llm] for llm in df_plot['llm']],
                      alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Adicionar barras de erro (IC 95%)
        ax.errorbar(x, df_plot['media'], 
                   yerr=[df_plot['erro_inf'], df_plot['erro_sup']],
                   fmt='none', ecolor='black', capsize=5, capthick=2)
        
        # Adicionar valores nas barras
        for i, (idx, row) in enumerate(df_plot.iterrows()):
            ax.text(i, row['media'] + 0.02, f"{row['media']:.3f}", 
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Linha de referência
        ax.axhline(y=0.85, color='green', linestyle='--', alpha=0.5, label='Excelente (≥0.85)')
        ax.axhline(y=0.75, color='orange', linestyle='--', alpha=0.5, label='Bom (≥0.75)')
        ax.axhline(y=0.65, color='red', linestyle='--', alpha=0.5, label='Moderado (≥0.65)')
        
        ax.set_xlabel('LLM', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno (média)', fontsize=12, fontweight='bold')
        ax.set_title(f'Comparação de Viés de Gênero - {benchmark}\n(Maior similaridade = menor viés)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(df_plot['llm'], fontsize=11)
        ax.set_ylim(0, 1.0)
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"comparacao_llms_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def grafico_distribuicao_similaridade(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Gráfico de distribuição (violin plot) das similaridades
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Preparar dados
        dados_plot = []
        for _, row in df_bench.iterrows():
            if row['similaridades'] and row['num_comparacoes'] > 0:
                for sim in row['similaridades']:
                    dados_plot.append({
                        'llm': row['llm'],
                        'similaridade': sim
                    })
        
        if not dados_plot:
            return
        
        df_plot = pd.DataFrame(dados_plot)
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Violin plot
        parts = ax.violinplot(
            [df_plot[df_plot['llm'] == llm]['similaridade'].values 
             for llm in sorted(df_plot['llm'].unique())],
            positions=range(len(df_plot['llm'].unique())),
            widths=0.7,
            showmeans=True,
            showmedians=True
        )
        
        # Colorir violinos
        for i, llm in enumerate(sorted(df_plot['llm'].unique())):
            parts['bodies'][i].set_facecolor(self.cores_llm[llm])
            parts['bodies'][i].set_alpha(0.7)
        
        # Box plot sobreposto
        bp = ax.boxplot(
            [df_plot[df_plot['llm'] == llm]['similaridade'].values 
             for llm in sorted(df_plot['llm'].unique())],
            positions=range(len(df_plot['llm'].unique())),
            widths=0.3,
            patch_artist=False,
            showfliers=False,
            medianprops=dict(color='red', linewidth=2),
            boxprops=dict(color='black', linewidth=1.5),
            whiskerprops=dict(color='black', linewidth=1.5),
            capprops=dict(color='black', linewidth=1.5)
        )
        
        ax.set_xlabel('LLM', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno', fontsize=12, fontweight='bold')
        ax.set_title(f'Distribuição da Similaridade entre Respostas - {benchmark}\n(Violin Plot + Box Plot)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(range(len(df_plot['llm'].unique())))
        ax.set_xticklabels(sorted(df_plot['llm'].unique()), fontsize=11)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"distribuicao_similaridade_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def grafico_perguntas_criticas(self, df: pd.DataFrame, output_path: Path, benchmark: str, top_n: int = 10):
        """
        Heatmap das N perguntas com menor similaridade (maior viés)
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
            top_n: Número de perguntas a mostrar
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Pegar as perguntas com menor similaridade média
        df_valido = df_bench[df_bench['num_comparacoes'] > 0].copy()
        
        if len(df_valido) < top_n:
            top_n = len(df_valido)
        
        if top_n == 0:
            return
        
        # Ordenar por similaridade média (crescente)
        df_sorted = df_valido.sort_values('media').head(top_n)
        
        # Preparar matriz para heatmap
        matriz_dados = []
        labels_perguntas = []
        
        for idx, row in df_sorted.iterrows():
            matriz_dados.append([row['media']])
            # Truncar pergunta
            pergunta_curta = row['pergunta'][:60] + "..." if len(row['pergunta']) > 60 else row['pergunta']
            labels_perguntas.append(f"P{row['numero_pergunta']}: {pergunta_curta}")
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(10, max(8, top_n * 0.5)))
        
        # Heatmap
        im = ax.imshow(matriz_dados, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Adicionar valores
        for i in range(len(matriz_dados)):
            text = ax.text(0, i, f"{matriz_dados[i][0]:.3f}",
                          ha="center", va="center", color="black", fontweight='bold')
        
        # Configurar eixos
        ax.set_xticks([0])
        ax.set_xticklabels([f'{benchmark}\nSimilaridade Média'], fontsize=11)
        ax.set_yticks(range(len(labels_perguntas)))
        ax.set_yticklabels(labels_perguntas, fontsize=9)
        ax.set_title(f'Top {top_n} Perguntas com MAIOR Viés de Gênero - {benchmark}\n(Menor similaridade)', 
                    fontsize=13, fontweight='bold', pad=20)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Similaridade', rotation=270, labelpad=20, fontsize=11)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"perguntas_criticas_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def grafico_evolucao_perguntas(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Gráfico de linha mostrando evolução da similaridade ao longo das perguntas
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for llm in sorted(df_bench['llm'].unique()):
            df_llm = df_bench[df_bench['llm'] == llm].copy()
            df_llm = df_llm[df_llm['num_comparacoes'] > 0].sort_values('numero_pergunta')
            
            if len(df_llm) == 0:
                continue
            
            ax.plot(df_llm['numero_pergunta'], df_llm['media'], 
                   marker='o', label=llm, color=self.cores_llm[llm],
                   linewidth=2, markersize=4, alpha=0.7)
        
        # Linhas de referência
        ax.axhline(y=0.85, color='green', linestyle='--', alpha=0.3, label='Excelente')
        ax.axhline(y=0.75, color='orange', linestyle='--', alpha=0.3, label='Bom')
        ax.axhline(y=0.65, color='red', linestyle='--', alpha=0.3, label='Moderado')
        
        ax.set_xlabel('Número da Pergunta', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno (média)', fontsize=12, fontweight='bold')
        ax.set_title(f'Evolução da Similaridade ao Longo das Perguntas - {benchmark}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 1.0)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"evolucao_perguntas_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def grafico_resumo_geral(self, df: pd.DataFrame, output_path: Path):
        """
        Gráfico resumo comparando todos os benchmarks e LLMs
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
        """
        # Calcular métricas por LLM e benchmark
        resultados = []
        for llm in df['llm'].unique():
            for benchmark in df['benchmark'].unique():
                df_subset = df[(df['llm'] == llm) & (df['benchmark'] == benchmark)]
                df_valido = df_subset[df_subset['num_comparacoes'] > 0]
                
                if len(df_valido) == 0:
                    continue
                
                todas_sims = []
                for sims in df_valido['similaridades']:
                    if sims:
                        todas_sims.extend(sims)
                
                if todas_sims:
                    media = np.mean(todas_sims)
                    resultados.append({
                        'llm': llm,
                        'benchmark': benchmark,
                        'media': media
                    })
        
        if not resultados:
            return
        
        df_plot = pd.DataFrame(resultados)
        
        # Criar gráfico de barras agrupadas
        fig, ax = plt.subplots(figsize=(12, 7))
        
        benchmarks = sorted(df_plot['benchmark'].unique())
        llms = sorted(df_plot['llm'].unique())
        x = np.arange(len(benchmarks))
        width = 0.25
        
        for i, llm in enumerate(llms):
            df_llm = df_plot[df_plot['llm'] == llm]
            valores = [df_llm[df_llm['benchmark'] == b]['media'].values[0] 
                      if len(df_llm[df_llm['benchmark'] == b]) > 0 else 0 
                      for b in benchmarks]
            
            offset = width * (i - len(llms)/2 + 0.5)
            bars = ax.bar(x + offset, valores, width, label=llm, 
                         color=self.cores_llm[llm], alpha=0.8, edgecolor='black')
            
            # Adicionar valores
            for j, v in enumerate(valores):
                if v > 0:
                    ax.text(j + offset, v + 0.01, f'{v:.3f}', 
                           ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Benchmark', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno (média)', fontsize=12, fontweight='bold')
        ax.set_title('Comparação Geral: Viés de Gênero por LLM e Benchmark\n(Maior similaridade = menor viés)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(benchmarks, fontsize=11)
        ax.set_ylim(0, 1.0)
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / "resumo_geral_similaridade.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def gerar_todos_graficos(self, df: pd.DataFrame, output_path: Path):
        """
        Gera todos os gráficos
        
        Args:
            df: DataFrame consolidado
            output_path: Diretório de saída
        """
        if df is None or len(df) == 0:
            print("⚠️  Nenhum dado para visualizar!")
            return
        
        print("\n" + "="*80)
        print("GERANDO VISUALIZAÇÕES")
        print("="*80)
        
        # Criar diretório de saída
        output_path.mkdir(exist_ok=True)
        
        # Gráfico resumo geral
        print("\nGráfico Resumo Geral:")
        self.grafico_resumo_geral(df, output_path)
        
        # Gráficos por benchmark
        for benchmark in df['benchmark'].unique():
            print(f"\nGráficos para {benchmark}:")
            self.grafico_comparacao_llms(df, output_path, benchmark)
            self.grafico_distribuicao_similaridade(df, output_path, benchmark)
            self.grafico_perguntas_criticas(df, output_path, benchmark)
            self.grafico_evolucao_perguntas(df, output_path, benchmark)
        
        print("\n" + "="*80)
        print("✓ TODAS AS VISUALIZAÇÕES FORAM GERADAS!")
        print("="*80)


def main():
    """Função principal"""
    print("="*80)
    print("VISUALIZAÇÃO - ANÁLISE QUANTITATIVA")
    print("="*80)
    
    # Diretórios
    base_path = Path(__file__).parent
    resultados_path = base_path / "resultados"
    visualizacoes_path = resultados_path / "visualizacoes"
    
    if not resultados_path.exists():
        print(f"\n⚠️  Diretório de resultados não encontrado: {resultados_path}")
        print("Execute primeiro a análise quantitativa (quantitativa.py)")
        return
    
    # Criar visualizador
    visualizador = VisualizadorQuantitativo()
    
    # Consolidar análises
    df = visualizador.consolidar_analises(resultados_path)
    
    if df is None:
        print("\n⚠️  Não foi possível consolidar as análises.")
        return
    
    # Gerar gráficos
    visualizador.gerar_todos_graficos(df, visualizacoes_path)
    
    print(f"\n✓ Gráficos salvos em: {visualizacoes_path}")


if __name__ == "__main__":
    main()
