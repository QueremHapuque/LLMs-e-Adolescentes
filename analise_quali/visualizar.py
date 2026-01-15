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
        import ast
        
        # Extrair notas de todos os critérios possíveis
        todos_criterios = set(self.criterios_safe_child + self.criterios_intima)
        
        for criterio in todos_criterios:
            if criterio in self.df.columns:
                def extrair_nota(x):
                    if pd.isna(x):
                        return np.nan
                    
                    # Se já for um número direto
                    if isinstance(x, (int, float)):
                        return x
                    
                    # Se já for dict, usar diretamente
                    if isinstance(x, dict):
                        return x.get('nota', np.nan)
                    
                    # Se for string, tentar parsear como dict Python primeiro
                    if isinstance(x, str):
                        try:
                            # Tentar ast.literal_eval para formato Python {'nota': 2}
                            dados = ast.literal_eval(x)
                            return dados.get('nota', np.nan)
                        except:
                            try:
                                # Se falhar, tentar JSON
                                dados = json.loads(x.replace("'", '"'))
                                return dados.get('nota', np.nan)
                            except:
                                return np.nan
                    
                    return np.nan
                
                self.df[f'{criterio}_nota'] = self.df[criterio].apply(extrair_nota)
        
        # Debug: mostrar resumo da extração para INTIMA
        print("\n📊 Resumo da extração - INTIMA:")
        for criterio in self.criterios_intima:
            if f'{criterio}_nota' in self.df.columns:
                total = self.df[f'{criterio}_nota'].notna().sum()
                print(f"   {criterio}: {total} valores extraídos")
                if criterio == 'incentivo_amizade':
                    df_intima = self.df[self.df['benchmark'] == 'INTIMA']
                    for llm in ['Gemini', 'Grok']:
                        df_llm = df_intima[df_intima['llm'] == llm]
                        for persona in df_llm['persona'].unique():
                            df_p = df_llm[df_llm['persona'] == persona]
                            n = df_p[f'{criterio}_nota'].notna().sum()
                            print(f"      {llm} - {persona[:20]}: {n} valores")
    
    def grafico_comparacao_llms(self, output_path: Path):
        """Gera gráficos de barras empilhadas comparando distribuição de respostas por LLM"""
        
        # Separar por benchmark
        df_safe_child = self.df[self.df['benchmark'] == 'Safe Child LLM']
        df_intima = self.df[self.df['benchmark'] == 'INTIMA']
        
        # Cores do Likert (vermelho escuro -> verde escuro)
        cores_likert = ['#d32f2f', '#f57c00', '#fdd835', '#7cb342', '#388e3c']
        labels_likert = ['1 (Muito inadequado)', '2 (Inadequado)', '3 (Neutro)', 
                        '4 (Adequado)', '5 (Muito adequado)']
        
        # Gráfico Safe Child LLM
        if len(df_safe_child) > 0:
            self._criar_grafico_stacked_llm(
                df_safe_child, 
                self.criterios_safe_child, 
                self.labels_safe_child,
                'Safe Child LLM: Distribuição de Respostas por Critério',
                cores_likert,
                labels_likert,
                output_path / 'comparacao_llms_safe_child.png'
            )
        
        # Gráfico INTIMA
        if len(df_intima) > 0:
            self._criar_grafico_stacked_llm(
                df_intima, 
                self.criterios_intima, 
                self.labels_intima,
                'INTIMA: Distribuição de Respostas por Critério',
                cores_likert,
                labels_likert,
                output_path / 'comparacao_llms_intima.png'
            )
    
    def _criar_grafico_stacked_llm(self, df, criterios, labels, titulo, cores, labels_likert, output_file):
        """Cria gráfico de barras empilhadas horizontal para LLMs - um gráfico por critério"""
        llms = sorted(df['llm'].unique())
        n_llms = len(llms)
        n_criterios = len(criterios)
        
        # Criar subplots: um por critério
        fig, axes = plt.subplots(n_criterios, 1, figsize=(12, n_criterios * 2))
        
        # Se só tem 1 critério, axes não é array
        if n_criterios == 1:
            axes = [axes]
        
        for idx_crit, (criterio, label) in enumerate(zip(criterios, labels)):
            ax = axes[idx_crit]
            
            # Preparar dados para este critério
            y_positions = []
            y_labels = []
            
            for idx_llm, llm in enumerate(llms):
                df_llm = df[df['llm'] == llm]
                y_positions.append(idx_llm)
                y_labels.append(llm)
                
                # Calcular frequências
                if f'{criterio}_nota' in df_llm.columns:
                    notas = df_llm[f'{criterio}_nota'].dropna()
                    total = len(notas)
                    
                    if total > 0:
                        freq_pct = [(notas == i).sum() / total * 100 for i in range(1, 6)]
                    else:
                        freq_pct = [0, 0, 0, 0, 0]
                else:
                    freq_pct = [0, 0, 0, 0, 0]
                
                # Criar barra empilhada para este LLM
                left = 0
                for i in range(5):
                    if freq_pct[i] > 0:
                        ax.barh(idx_llm, freq_pct[i], left=left, color=cores[i], 
                               edgecolor='white', linewidth=2, height=0.7)
                        
                        # Adicionar label de percentual (apenas se >= 7%)
                        if freq_pct[i] >= 7:
                            ax.text(left + freq_pct[i]/2, idx_llm, f'{freq_pct[i]:.0f}%', 
                                   ha='center', va='center', fontsize=10, 
                                   fontweight='bold', color='white')
                        
                        left += freq_pct[i]
            
            # Configurar eixos
            ax.set_yticks(y_positions)
            ax.set_yticklabels(y_labels, fontsize=11)
            ax.set_xlim(0, 100)
            ax.set_xlabel('Frequência (%)', fontsize=10)
            ax.set_title(label, fontsize=12, fontweight='bold', pad=10, loc='left')
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        # Legenda compartilhada no topo
        handles = [plt.Rectangle((0,0),1,1, color=cores[i], edgecolor='white', linewidth=1) 
                  for i in range(5)]
        labels_curtos = ['1\n(Muito\ninadequado)', '2\n(Inadequado)', '3\n(Neutro)', 
                        '4\n(Adequado)', '5\n(Muito\nadequado)']
        fig.legend(handles, labels_curtos, loc='upper center', bbox_to_anchor=(0.5, 0.98), 
                  ncol=5, fontsize=9, frameon=False)
        
        plt.suptitle(titulo, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico salvo: {output_file.name}")
        plt.close()
    
    def grafico_comparacao_personas(self, output_path: Path):
        """Gera gráficos de barras empilhadas comparando distribuição por persona"""
        
        # Função para normalizar nomes de personas
        def normalizar_persona(nome):
            nome_lower = nome.lower()
            if 'ana' in nome_lower and 'cis' in nome_lower:
                return "Ana (menina cis)"
            elif 'felipe' in nome_lower and 'cis' in nome_lower:
                return "Felipe (menino cis)"
            elif 'geovana' in nome_lower and 'trans' in nome_lower:
                return "Geovana (menina trans)"
            elif 'italo' in nome_lower or 'ítalo' in nome_lower:
                return "Italo (menino trans)"
            elif 'ariel' in nome_lower:
                return "Ariel (não-binário)"
            else:
                return nome.split(',')[0].strip()
        
        # Separar por benchmark
        df_safe_child = self.df[self.df['benchmark'] == 'Safe Child LLM']
        df_intima = self.df[self.df['benchmark'] == 'INTIMA']
        
        # Cores do Likert
        cores_likert = ['#d32f2f', '#f57c00', '#fdd835', '#7cb342', '#388e3c']
        labels_likert = ['1 (Muito inadequado)', '2 (Inadequado)', '3 (Neutro)', 
                        '4 (Adequado)', '5 (Muito adequado)']
        
        # Gráfico Safe Child LLM
        if len(df_safe_child) > 0:
            personas_normalizadas = {p: normalizar_persona(p) for p in df_safe_child['persona'].unique()}
            self._criar_grafico_stacked_persona(
                df_safe_child,
                personas_normalizadas,
                self.criterios_safe_child,
                self.labels_safe_child,
                'Safe Child LLM: Distribuição de Respostas por Persona',
                cores_likert,
                labels_likert,
                output_path / 'comparacao_personas_safe_child.png'
            )
        
        # Gráfico INTIMA
        if len(df_intima) > 0:
            personas_normalizadas = {p: normalizar_persona(p) for p in df_intima['persona'].unique()}
            self._criar_grafico_stacked_persona(
                df_intima,
                personas_normalizadas,
                self.criterios_intima,
                self.labels_intima,
                'INTIMA: Distribuição de Respostas por Persona',
                cores_likert,
                labels_likert,
                output_path / 'comparacao_personas_intima.png'
            )
    
    def _criar_grafico_stacked_persona(self, df, personas_map, criterios, labels, titulo, cores, labels_likert, output_file):
        """Cria gráfico de barras empilhadas horizontal para personas - um gráfico por critério"""
        personas_orig = sorted(personas_map.keys())
        n_personas = len(personas_orig)
        n_criterios = len(criterios)
        
        # Criar subplots: um por critério
        fig, axes = plt.subplots(n_criterios, 1, figsize=(12, n_criterios * 2.5))
        
        # Se só tem 1 critério, axes não é array
        if n_criterios == 1:
            axes = [axes]
        
        for idx_crit, (criterio, label) in enumerate(zip(criterios, labels)):
            ax = axes[idx_crit]
            
            # Preparar dados para este critério
            y_positions = []
            y_labels = []
            
            for idx_persona, persona_orig in enumerate(personas_orig):
                df_persona = df[df['persona'] == persona_orig]
                persona_label = personas_map[persona_orig]
                
                y_positions.append(idx_persona)
                y_labels.append(persona_label)
                
                # Calcular frequências
                if f'{criterio}_nota' in df_persona.columns:
                    notas = df_persona[f'{criterio}_nota'].dropna()
                    total = len(notas)
                    
                    if total > 0:
                        freq_pct = [(notas == i).sum() / total * 100 for i in range(1, 6)]
                    else:
                        freq_pct = [0, 0, 0, 0, 0]
                else:
                    freq_pct = [0, 0, 0, 0, 0]
                
                # Criar barra empilhada para esta persona
                left = 0
                for i in range(5):
                    if freq_pct[i] > 0:
                        ax.barh(idx_persona, freq_pct[i], left=left, color=cores[i], 
                               edgecolor='white', linewidth=2, height=0.7)
                        
                        # Adicionar label de percentual (apenas se >= 7%)
                        if freq_pct[i] >= 7:
                            ax.text(left + freq_pct[i]/2, idx_persona, f'{freq_pct[i]:.0f}%', 
                                   ha='center', va='center', fontsize=9, 
                                   fontweight='bold', color='white')
                        
                        left += freq_pct[i]
            
            # Configurar eixos
            ax.set_yticks(y_positions)
            ax.set_yticklabels(y_labels, fontsize=10)
            ax.set_xlim(0, 100)
            ax.set_xlabel('Frequência (%)', fontsize=10)
            ax.set_title(label, fontsize=12, fontweight='bold', pad=10, loc='left')
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        # Legenda compartilhada no topo
        handles = [plt.Rectangle((0,0),1,1, color=cores[i], edgecolor='white', linewidth=1) 
                  for i in range(5)]
        labels_curtos = ['1\n(Muito\ninadequado)', '2\n(Inadequado)', '3\n(Neutro)', 
                        '4\n(Adequado)', '5\n(Muito\nadequado)']
        fig.legend(handles, labels_curtos, loc='upper center', bbox_to_anchor=(0.5, 0.98), 
                  ncol=5, fontsize=9, frameon=False)
        
        plt.suptitle(titulo, fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico salvo: {output_file.name}")
        plt.close()
    
    def grafico_personas_por_llm(self, output_path: Path):
        """Gera gráficos de personas separados por LLM para identificar divergências"""
        
        # Função para normalizar nomes de personas
        def normalizar_persona(nome):
            nome_lower = nome.lower()
            if 'ana' in nome_lower and 'cis' in nome_lower:
                return "Ana (menina cis)"
            elif 'felipe' in nome_lower and 'cis' in nome_lower:
                return "Felipe (menino cis)"
            elif 'geovana' in nome_lower and 'trans' in nome_lower:
                return "Geovana (menina trans)"
            elif 'italo' in nome_lower or 'ítalo' in nome_lower:
                return "Italo (menino trans)"
            elif 'ariel' in nome_lower:
                return "Ariel (não-binário)"
            else:
                return nome.split(',')[0].strip()
        
        # Separar por benchmark
        df_safe_child = self.df[self.df['benchmark'] == 'Safe Child LLM']
        df_intima = self.df[self.df['benchmark'] == 'INTIMA']
        
        # Cores do Likert
        cores_likert = ['#d32f2f', '#f57c00', '#fdd835', '#7cb342', '#388e3c']
        labels_likert = ['1 (Muito inadequado)', '2 (Inadequado)', '3 (Neutro)', 
                        '4 (Adequado)', '5 (Muito adequado)']
        
        # Gerar gráfico para cada LLM - Safe Child
        if len(df_safe_child) > 0:
            for llm in sorted(df_safe_child['llm'].unique()):
                df_llm = df_safe_child[df_safe_child['llm'] == llm]
                personas_normalizadas = {p: normalizar_persona(p) for p in df_llm['persona'].unique()}
                
                self._criar_grafico_stacked_persona(
                    df_llm,
                    personas_normalizadas,
                    self.criterios_safe_child,
                    self.labels_safe_child,
                    f'Safe Child LLM - {llm}: Distribuição por Persona',
                    cores_likert,
                    labels_likert,
                    output_path / f'personas_{llm.lower().replace(" ", "_")}_safe_child.png'
                )
        
        # Gerar gráfico para cada LLM - INTIMA
        if len(df_intima) > 0:
            for llm in sorted(df_intima['llm'].unique()):
                df_llm = df_intima[df_intima['llm'] == llm]
                personas_normalizadas = {p: normalizar_persona(p) for p in df_llm['persona'].unique()}
                
                self._criar_grafico_stacked_persona(
                    df_llm,
                    personas_normalizadas,
                    self.criterios_intima,
                    self.labels_intima,
                    f'INTIMA - {llm}: Distribuição por Persona',
                    cores_likert,
                    labels_likert,
                    output_path / f'personas_{llm.lower().replace(" ", "_")}_intima.png'
                )
    
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
        self.grafico_personas_por_llm(output_path)
        
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
