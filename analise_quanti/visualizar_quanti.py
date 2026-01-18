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
            'Gemini': '#9370DB',
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
        import ast
        
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
                # Converter colunas de string para estruturas Python usando ast.literal_eval
                if 'similaridades' in df.columns:
                    df['similaridades'] = df['similaridades'].apply(
                        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                    )
                if 'comparacoes_detalhadas' in df.columns:
                    df['comparacoes_detalhadas'] = df['comparacoes_detalhadas'].apply(
                        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                    )
                dfs.append(df)
                print(f"  ✓ {arquivo.name}")
            except Exception as e:
                print(f"  ✗ Erro ao ler {arquivo.name}: {e}")
        
        if not dfs:
            return None
        
        df_consolidado = pd.concat(dfs, ignore_index=True)
        print(f"\n✓ Consolidado: {len(df_consolidado)} registros de {len(dfs)} arquivos")
        
        return df_consolidado
    
    def grafico_intervalo_confianca(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Gráfico de Intervalo de Confiança (95%) comparando LLMs
        Mostra média com barras de erro do IC95%
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Calcular média e IC95% para cada LLM
        llms_ordem = ['ChatGPT', 'Gemini', 'Grok']
        medias = []
        ic_inferiores = []
        ic_superiores = []
        llms_presentes = []
        
        for llm in llms_ordem:
            df_llm = df_bench[df_bench['llm'] == llm]
            
            if len(df_llm) == 0:
                continue
            
            # Coletar todas as similaridades
            todas_sims = []
            for _, row in df_llm.iterrows():
                if row['similaridades'] and row['num_comparacoes'] > 0:
                    todas_sims.extend(row['similaridades'])
            
            if len(todas_sims) < 2:
                continue
            
            # Calcular média e IC95%
            media = np.mean(todas_sims)
            sem = stats.sem(todas_sims)
            n = len(todas_sims)
            confianca = 0.95
            graus_liberdade = n - 1
            intervalo = stats.t.interval(confianca, graus_liberdade, loc=media, scale=sem)
            
            medias.append(media)
            ic_inferiores.append(intervalo[0])
            ic_superiores.append(intervalo[1])
            llms_presentes.append(llm)
        
        if not medias:
            return
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(10, 7))
        
        positions = range(len(llms_presentes))
        
        # Calcular erros para errorbar (distância da média até os limites do IC)
        erro_inferior = [media - ic_inf for media, ic_inf in zip(medias, ic_inferiores)]
        erro_superior = [ic_sup - media for media, ic_sup in zip(medias, ic_superiores)]
        erros = [erro_inferior, erro_superior]
        
        # Plot com barras de erro
        ax.errorbar(
            positions, 
            medias, 
            yerr=erros,
            fmt='o',  # Pontos circulares
            markersize=10,
            capsize=15,  # Tamanho das "tampas" da barra de erro
            capthick=2,
            linewidth=2,
            color='#2E86AB',  # Azul
            ecolor='#2E86AB',  # Cor da barra de erro
            markerfacecolor='#2E86AB',
            markeredgecolor='black',
            markeredgewidth=1.5
        )
        
        # Adicionar valores com média e intervalo
        for i, (pos, ic_inf, ic_sup) in enumerate(zip(positions, ic_inferiores, ic_superiores)):
            offset = 0.005
            label = f'[{ic_inf:.3f}; {ic_sup:.3f}]'
            ax.text(pos, ic_sup + offset, label, 
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Configurar eixos
        ax.set_xticks(positions)
        ax.set_xticklabels(llms_presentes, fontsize=12, fontweight='bold')
        ax.set_xlabel('LLM', fontsize=13, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno (Média)', fontsize=13, fontweight='bold')
        ax.set_title(f'Gráfico de Intervalos de Confiança (IC 95%)\n{benchmark}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid horizontal
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Ajustar limites do Y
        y_min = min(ic_inferiores) - 0.05
        y_max = max(ic_superiores) + 0.08
        ax.set_ylim(y_min, y_max)
        
        # Adicionar nota explicativa
        ax.text(0.02, 0.98, 'As barras indicam o intervalo de confiança de 95%', 
               transform=ax.transAxes, fontsize=9, va='top', style='italic',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"intervalo_confianca_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
        
        # Salvar tabela Excel com dados do IC95%
        tabela_dados = []
        for llm, media, ic_inf, ic_sup in zip(llms_presentes, medias, ic_inferiores, ic_superiores):
            margem_erro = ic_sup - media
            tabela_dados.append({
                'LLM': llm,
                'Média': media,
                'IC 95% Inferior': ic_inf,
                'IC 95% Superior': ic_sup,
                'Margem de Erro': margem_erro,
                'Amplitude IC': ic_sup - ic_inf
            })
        
        df_tabela = pd.DataFrame(tabela_dados)
        arquivo_excel = output_path / f"tabela_intervalo_confianca_{benchmark.replace(' ', '_')}.xlsx"
        df_tabela.to_excel(arquivo_excel, index=False)
        print(f"  ✓ {arquivo_excel.name} [TABELA]")
    
    def grafico_intervalo_confianca_por_persona(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Gráfico de Intervalo de Confiança (95%) por PERSONA comparando os 3 LLMs
        Similar ao violin plot por persona, mas com IC ao invés de distribuição completa
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Verificar se temos comparacoes_detalhadas
        if 'comparacoes_detalhadas' not in df_bench.columns:
            print("  ⚠️  Coluna 'comparacoes_detalhadas' não encontrada.")
            return
        
        # Mapear nomes para perfis completos
        perfis_personas = {
            'Ana': 'Ana\n(garota cis, 15a)',
            'Felipe': 'Felipe\n(garoto cis, 16a)',
            'Geovana': 'Geovana\n(garota trans, 14a)',
            'Italo': 'Ítalo\n(garoto trans, 15a)',
            'Ariel': 'Ariel\n(não-binário, 16a)'
        }
        
        personas_ordem = ['Ana', 'Felipe', 'Geovana', 'Italo', 'Ariel']
        llms_ordem = ['ChatGPT', 'Gemini', 'Grok']
        
        # Coletar similaridades por persona E LLM
        dados_plot = []
        
        for llm in df_bench['llm'].unique():
            df_llm = df_bench[df_bench['llm'] == llm]
            
            for _, row in df_llm.iterrows():
                if row['comparacoes_detalhadas']:
                    for comp in row['comparacoes_detalhadas']:
                        p1 = comp['persona1']
                        p2 = comp['persona2']
                        sim = comp['similaridade']
                        
                        dados_plot.append({'llm': llm, 'persona': p1, 'similaridade': sim})
                        dados_plot.append({'llm': llm, 'persona': p2, 'similaridade': sim})
        
        if not dados_plot:
            print("  ⚠️  Nenhum dado detalhado encontrado.")
            return
        
        df_plot = pd.DataFrame(dados_plot)
        
        # Criar gráfico único
        fig, ax = plt.subplots(figsize=(18, 8))
        
        # Preparar dados
        positions = []
        medias = []
        ic_inferiores = []
        ic_superiores = []
        colors_list = []
        labels_x = []
        
        pos_counter = 0
        gap_between_personas = 2.0
        gap_between_llms = 0.5
        
        for persona in personas_ordem:
            if persona not in df_plot['persona'].unique():
                continue
            
            for llm in llms_ordem:
                df_subset = df_plot[(df_plot['persona'] == persona) & (df_plot['llm'] == llm)]
                
                if len(df_subset) > 1:
                    valores = df_subset['similaridade'].values
                    
                    # Calcular média e IC95%
                    media = np.mean(valores)
                    sem = stats.sem(valores)
                    n = len(valores)
                    confianca = 0.95
                    graus_liberdade = n - 1
                    intervalo = stats.t.interval(confianca, graus_liberdade, loc=media, scale=sem)
                    
                    positions.append(pos_counter)
                    medias.append(media)
                    ic_inferiores.append(intervalo[0])
                    ic_superiores.append(intervalo[1])
                    colors_list.append(self.cores_llm[llm])
                    
                    pos_counter += gap_between_llms
            
            pos_counter += gap_between_personas
        
        # Calcular erros
        erro_inferior = [media - ic_inf for media, ic_inf in zip(medias, ic_inferiores)]
        erro_superior = [ic_sup - media for media, ic_sup in zip(medias, ic_superiores)]
        erros = [erro_inferior, erro_superior]
        
        # Plot com barras de erro (um por um para colorir individualmente)
        for i, (pos, media, erro_inf, erro_sup, color) in enumerate(zip(positions, medias, erro_inferior, erro_superior, colors_list)):
            ax.errorbar(
                pos, 
                media, 
                yerr=[[erro_inf], [erro_sup]],
                fmt='o',
                markersize=8,
                capsize=10,
                capthick=2,
                linewidth=2,
                color=color,
                ecolor=color,
                markerfacecolor=color,
                markeredgecolor='black',
                markeredgewidth=1.2
            )
        
        # Adicionar valores com média e intervalo
        for pos, ic_inf, ic_sup in zip(positions, ic_inferiores, ic_superiores):
            offset = 0.005
            label = f'[{ic_inf:.2f}; {ic_sup:.2f}]'
            ax.text(pos, ic_sup + offset, label, 
                   ha='center', va='bottom', fontsize=7, fontweight='bold')
        
        # Configurar eixo X com personas
        persona_positions = []
        persona_labels = []
        
        pos_counter = 0
        for persona in personas_ordem:
            if persona not in df_plot['persona'].unique():
                continue
            
            # Posição central dos 3 LLMs
            centro = pos_counter + gap_between_llms
            persona_positions.append(centro)
            persona_labels.append(perfis_personas[persona])
            
            pos_counter += (gap_between_llms * len(llms_ordem)) + gap_between_personas
        
        ax.set_xticks(persona_positions)
        ax.set_xticklabels(persona_labels, fontsize=10, fontweight='bold')
        
        # Labels e título
        ax.set_xlabel('Persona', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno (Média)', fontsize=12, fontweight='bold')
        ax.set_title(f'{benchmark}: Intervalos de Confiança (IC 95%) por Persona\n(Cada persona mostra ChatGPT | Gemini | Grok lado a lado)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Ajustar limites
        if ic_inferiores and ic_superiores:
            y_min = min(ic_inferiores) - 0.05
            y_max = max(ic_superiores) + 0.08
            ax.set_ylim(y_min, y_max)
        
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Legenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.cores_llm['ChatGPT'], edgecolor='black', label='ChatGPT'),
            Patch(facecolor=self.cores_llm['Gemini'], edgecolor='black', label='Gemini'),
            Patch(facecolor=self.cores_llm['Grok'], edgecolor='black', label='Grok')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=11, framealpha=0.9)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"intervalo_confianca_por_persona_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def grafico_violino_por_persona(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Violin plot agrupado por PERSONA comparando os 3 LLMs lado a lado
        Objetivo: ver como cada LLM trata cada persona diferentemente
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída  
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Verificar se temos comparacoes_detalhadas
        if 'comparacoes_detalhadas' not in df_bench.columns:
            print("  ⚠️  Coluna 'comparacoes_detalhadas' não encontrada. Execute a análise quantitativa novamente.")
            return
        
        # Mapear nomes para perfis completos
        perfis_personas = {
            'Ana': 'Ana\n(garota cis, 15a)',
            'Felipe': 'Felipe\n(garoto cis, 16a)',
            'Geovana': 'Geovana\n(garota trans, 14a)',
            'Italo': 'Ítalo\n(garoto trans, 15a)',
            'Ariel': 'Ariel\n(não-binário, 16a)'
        }
        
        personas_ordem = ['Ana', 'Felipe', 'Geovana', 'Italo', 'Ariel']
        llms_ordem = ['ChatGPT', 'Gemini', 'Grok']
        
        # Coletar similaridades por persona E LLM
        dados_plot = []
        
        for llm in df_bench['llm'].unique():
            df_llm = df_bench[df_bench['llm'] == llm]
            
            for _, row in df_llm.iterrows():
                if row['comparacoes_detalhadas']:
                    for comp in row['comparacoes_detalhadas']:
                        p1 = comp['persona1']
                        p2 = comp['persona2']
                        sim = comp['similaridade']
                        
                        # Adicionar para ambas personas
                        dados_plot.append({'llm': llm, 'persona': p1, 'similaridade': sim})
                        dados_plot.append({'llm': llm, 'persona': p2, 'similaridade': sim})
        
        if not dados_plot:
            print("  ⚠️  Nenhum dado detalhado encontrado.")
            return
        
        df_plot = pd.DataFrame(dados_plot)
        
        # Criar gráfico único com todas as personas e LLMs
        fig, ax = plt.subplots(figsize=(18, 8))
        
        # Preparar dados para violin plot agrupado
        positions = []
        data_to_plot = []
        colors_list = []
        
        pos_counter = 0
        gap_between_personas = 2.0
        gap_between_llms = 0.5
        
        for persona in personas_ordem:
            if persona not in df_plot['persona'].unique():
                continue
                
            for llm in llms_ordem:
                df_subset = df_plot[(df_plot['persona'] == persona) & (df_plot['llm'] == llm)]
                
                if len(df_subset) > 0:
                    data_to_plot.append(df_subset['similaridade'].values)
                    positions.append(pos_counter)
                    colors_list.append(self.cores_llm[llm])
                    
                    pos_counter += gap_between_llms
            
            # Adicionar gap maior entre personas
            pos_counter += gap_between_personas
        
        # Criar violin plots individuais para cada grupo
        for i, (data, pos, color) in enumerate(zip(data_to_plot, positions, colors_list)):
            parts = ax.violinplot(
                [data],
                positions=[pos],
                widths=0.4,
                showmeans=False,
                showmedians=False,
                showextrema=False
            )
            
            # Colorir violino
            for pc in parts['bodies']:
                pc.set_facecolor(color)
                pc.set_alpha(0.4)
                pc.set_edgecolor('black')
                pc.set_linewidth(1.2)
        
        # Adicionar boxplot fino sobreposto para mostrar quartis
        bp = ax.boxplot(
            data_to_plot,
            positions=positions,
            widths=0.15,
            patch_artist=False,
            showfliers=False,
            medianprops=dict(color='red', linewidth=2),
            boxprops=dict(color='black', linewidth=1.2),
            whiskerprops=dict(color='black', linewidth=1.2),
            capprops=dict(color='black', linewidth=1.2)
        )
        
        # Adicionar valores mínimos (pior caso)
        pos_idx = 0
        for persona in personas_ordem:
            if persona not in df_plot['persona'].unique():
                continue
                
            for llm in llms_ordem:
                df_subset = df_plot[(df_plot['persona'] == persona) & (df_plot['llm'] == llm)]
                
                if len(df_subset) > 0:
                    valores = df_subset['similaridade'].values
                    minimo = np.min(valores)
                    
                    # Pior caso - ajuste de posição dinâmico
                    offset = 0.02  # Mais próximo do violino
                    ax.text(positions[pos_idx], minimo - offset, f'{minimo:.2f}', 
                           ha='center', va='top', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.8,
                                   edgecolor='orange', linewidth=1))
                    
                    pos_idx += 1
        
        # Configurar eixo X com personas
        persona_positions = []
        persona_labels = []
        
        pos_counter = 0
        for persona in personas_ordem:
            if persona not in df_plot['persona'].unique():
                continue
            
            # Posição central dos 3 LLMs
            centro = pos_counter + gap_between_llms
            persona_positions.append(centro)
            persona_labels.append(perfis_personas[persona])
            
            pos_counter += (gap_between_llms * len(llms_ordem)) + gap_between_personas
        
        ax.set_xticks(persona_positions)
        ax.set_xticklabels(persona_labels, fontsize=10, fontweight='bold')
        
        # Labels e título
        ax.set_xlabel('Persona', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similaridade de Cosseno\n(comparações envolvendo esta persona)', 
                     fontsize=12, fontweight='bold')
        ax.set_title(f'{benchmark}: Comparação de Viés por Persona entre LLMs\n' +
                    f'(Cada persona mostra ChatGPT | Gemini | Grok lado a lado)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.set_ylim(-0.05, 1.05)
        ax.grid(axis='y', alpha=0.3)
        
        # Legenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.cores_llm['ChatGPT'], alpha=0.7, label='ChatGPT'),
            Patch(facecolor=self.cores_llm['Gemini'], alpha=0.7, label='Gemini'),
            Patch(facecolor=self.cores_llm['Grok'], alpha=0.7, label='Grok')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=11, framealpha=0.9)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"comparacao_llms_por_persona_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name}")
    
    def grafico_heatmap_persona_llm(self, df: pd.DataFrame, output_path: Path, benchmark: str):
        """
        Heatmap mostrando PIOR CASO de viés por Persona x LLM
        (Métrica adicional interessante: identifica qual LLM tem mais viés contra qual persona)
        
        Args:
            df: DataFrame com análises
            output_path: Diretório de saída
            benchmark: Tipo de benchmark
        """
        # Filtrar benchmark
        df_bench = df[df['benchmark'] == benchmark].copy()
        
        if len(df_bench) == 0:
            return
        
        # Calcular pior caso por LLM
        llms = sorted(df_bench['llm'].unique())
        
        # Criar matriz: LLMs x Estatísticas
        matriz_dados = []
        estatisticas = ['Pior Caso\n(min)', 'Q1\n(25%)', 'Mediana\n(50%)', 'Q3\n(75%)', 'Melhor\n(max)']
        
        for llm in llms:
            df_llm = df_bench[df_bench['llm'] == llm]
            todas_sims = []
            for sims in df_llm['similaridades']:
                if sims:
                    todas_sims.extend(sims)
            
            if todas_sims:
                linha = [
                    np.min(todas_sims),      # Pior caso
                    np.percentile(todas_sims, 25),  # Q1
                    np.median(todas_sims),   # Mediana
                    np.percentile(todas_sims, 75),  # Q3
                    np.max(todas_sims)       # Melhor caso
                ]
                matriz_dados.append(linha)
        
        if not matriz_dados:
            return
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Heatmap
        im = ax.imshow(matriz_dados, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Adicionar valores e destacar pior caso
        for i in range(len(llms)):
            for j in range(len(estatisticas)):
                valor = matriz_dados[i][j]
                # Destacar pior caso (primeira coluna)
                if j == 0:
                    text = ax.text(j, i, f'{valor:.3f}',
                                  ha="center", va="center", color="white",
                                  fontweight='bold', fontsize=12,
                                  bbox=dict(boxstyle='round,pad=0.5', 
                                           facecolor='darkred', alpha=0.8))
                else:
                    text = ax.text(j, i, f'{valor:.3f}',
                                  ha="center", va="center", color="black",
                                  fontweight='bold', fontsize=10)
        
        # Configurar eixos
        ax.set_xticks(range(len(estatisticas)))
        ax.set_xticklabels(estatisticas, fontsize=11)
        ax.set_yticks(range(len(llms)))
        ax.set_yticklabels(llms, fontsize=12, fontweight='bold')
        ax.set_title(f'Análise Estatística de Viés - {benchmark}\n(Destaque: PIOR CASO = maior viés detectado)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Similaridade\n(0=viés máximo, 1=sem viés)', 
                      rotation=270, labelpad=25, fontsize=11)
        
        plt.tight_layout()
        
        # Salvar
        arquivo = output_path / f"heatmap_estatisticas_{benchmark.replace(' ', '_')}.png"
        plt.savefig(arquivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ {arquivo.name} [NOVA MÉTRICA: Estatísticas por LLM com destaque no pior caso]")
    

    

    

    
    def gerar_todos_graficos(self, df: pd.DataFrame, output_path: Path):
        """
        Gera todos os gráficos (apenas violinos conforme orientação)
        
        Args:
            df: DataFrame consolidado
            output_path: Diretório de saída
        """
        if df is None or len(df) == 0:
            print("⚠️  Nenhum dado para visualizar!")
            return
        
        print("\n" + "="*80)
        print("GERANDO VISUALIZAÇÕES (FOCO: PIOR CASO)")
        print("="*80)
        
        # Criar diretório de saída
        output_path.mkdir(exist_ok=True)
        
        # Gráficos por benchmark
        for benchmark in df['benchmark'].unique():
            print(f"\n📊 Gráficos para {benchmark}:")
            print("-" * 60)
            self.grafico_intervalo_confianca(df, output_path, benchmark)
            self.grafico_intervalo_confianca_por_persona(df, output_path, benchmark)
            self.grafico_violino_por_persona(df, output_path, benchmark)
        
        print("\n" + "="*80)
        print("✓ VISUALIZAÇÕES CONCLUÍDAS!")
        print("="*80)
        print("\n📈 Gráficos gerados:")
        print("  • Intervalo de Confiança (IC 95%) GERAL: média com barras de erro por LLM")
        print("  • Intervalo de Confiança (IC 95%) POR PERSONA: comparação entre LLMs para cada persona")
        print("  • Violin plot por PERSONA: distribuição completa para cada persona")
        print("\n💡 Interpretação:")
        print("  • Valores BAIXOS = MAIOR viés de gênero")
        print("  • IC 95%: se os intervalos NÃO se sobrepõem, há diferença estatística")
        print("  • Gráfico por persona: identifica QUAL persona sofre mais viés")
        print("  • Min destacado no violin = PIOR CASO (maior viés detectado)")


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
