"""
Script para exportar resultados em diferentes formatos
Útil para análises adicionais ou integração com outras ferramentas
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class ResultsExporter:
    """Exportador de resultados em múltiplos formatos"""
    
    def __init__(self, arquivo_consolidado: str):
        """
        Inicializa o exportador
        
        Args:
            arquivo_consolidado: Caminho para o arquivo Excel consolidado
        """
        self.df = pd.read_excel(arquivo_consolidado)
        self.arquivo = Path(arquivo_consolidado)
    
    def exportar_json(self, output_path: Path):
        """Exporta para JSON estruturado"""
        # Converter DataFrame para dict
        dados = self.df.to_dict(orient='records')
        
        # Estruturar por LLM e benchmark
        estruturado = {}
        
        for registro in dados:
            llm = registro['llm']
            benchmark = registro['benchmark']
            
            if llm not in estruturado:
                estruturado[llm] = {}
            
            if benchmark not in estruturado[llm]:
                estruturado[llm][benchmark] = []
            
            estruturado[llm][benchmark].append(registro)
        
        # Salvar
        output_file = output_path / f'analise_completa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(estruturado, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON exportado: {output_file.name}")
        return output_file
    
    def exportar_csv(self, output_path: Path):
        """Exporta para CSV"""
        output_file = output_path / f'analise_completa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ CSV exportado: {output_file.name}")
        return output_file
    
    def exportar_estatisticas_json(self, output_path: Path):
        """Exporta apenas estatísticas resumidas em JSON"""
        stats = {
            "meta": {
                "data_exportacao": datetime.now().isoformat(),
                "total_analises": len(self.df),
                "arquivo_origem": self.arquivo.name
            },
            "por_llm": {},
            "por_persona": {},
            "por_benchmark": {}
        }
        
        # Estatísticas por LLM
        for llm in self.df['llm'].unique():
            df_llm = self.df[self.df['llm'] == llm]
            
            vies_counts = df_llm['vies_identificado'].value_counts().to_dict()
            
            stats["por_llm"][llm] = {
                "total_respostas": len(df_llm),
                "vies_identificado": vies_counts.get('sim', 0),
                "vies_parcial": vies_counts.get('parcial', 0),
                "sem_vies": vies_counts.get('não', 0),
                "percentual_vies": round(vies_counts.get('sim', 0) / len(df_llm) * 100, 2)
            }
        
        # Estatísticas por persona
        for persona in self.df['persona'].unique():
            df_persona = self.df[self.df['persona'] == persona]
            
            vies_counts = df_persona['vies_identificado'].value_counts().to_dict()
            
            stats["por_persona"][persona] = {
                "total_respostas": len(df_persona),
                "vies_identificado": vies_counts.get('sim', 0),
                "percentual_vies": round(vies_counts.get('sim', 0) / len(df_persona) * 100, 2)
            }
        
        # Estatísticas por benchmark
        for benchmark in self.df['benchmark'].unique():
            df_bench = self.df[self.df['benchmark'] == benchmark]
            
            vies_counts = df_bench['vies_identificado'].value_counts().to_dict()
            
            stats["por_benchmark"][benchmark] = {
                "total_respostas": len(df_bench),
                "vies_identificado": vies_counts.get('sim', 0),
                "percentual_vies": round(vies_counts.get('sim', 0) / len(df_bench) * 100, 2)
            }
        
        # Salvar
        output_file = output_path / f'estatisticas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Estatísticas JSON exportadas: {output_file.name}")
        return output_file
    
    def exportar_respostas_problematicas(self, output_path: Path, limite_nota: float = 2.5):
        """
        Exporta apenas respostas problemáticas (com notas baixas ou viés identificado)
        
        Args:
            output_path: Diretório de saída
            limite_nota: Nota abaixo da qual a resposta é considerada problemática
        """
        # Filtrar respostas problemáticas
        df_problematicas = self.df[
            (self.df['vies_identificado'] == 'sim') |
            (self.df['vies_identificado'] == 'parcial')
        ].copy()
        
        # Salvar
        output_file = output_path / f'respostas_problematicas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        df_problematicas.to_excel(output_file, index=False)
        
        print(f"✓ Respostas problemáticas exportadas: {output_file.name}")
        print(f"  Total: {len(df_problematicas)} de {len(self.df)} ({len(df_problematicas)/len(self.df)*100:.1f}%)")
        return output_file
    
    def exportar_comparacao_personas(self, output_path: Path):
        """Exporta comparação direta entre personas para mesmas perguntas"""
        comparacoes = []
        
        # Agrupar por LLM, benchmark e número da pergunta
        grupos = self.df.groupby(['llm', 'benchmark', 'numero_pergunta', 'pergunta'])
        
        for (llm, benchmark, num, pergunta), grupo in grupos:
            if len(grupo) > 1:  # Só se houver múltiplas personas
                comparacao = {
                    'llm': llm,
                    'benchmark': benchmark,
                    'numero_pergunta': num,
                    'pergunta': pergunta,
                    'respostas_por_persona': {}
                }
                
                for _, row in grupo.iterrows():
                    persona = row['persona']
                    comparacao['respostas_por_persona'][persona] = {
                        'resposta': row['resposta'],
                        'vies_identificado': row.get('vies_identificado', 'N/A'),
                        'tipo_vies': row.get('tipo_vies', 'N/A'),
                        'observacoes': row.get('observacoes_gerais', 'N/A')
                    }
                
                comparacoes.append(comparacao)
        
        # Salvar JSON
        output_file = output_path / f'comparacao_personas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparacoes, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Comparação entre personas exportada: {output_file.name}")
        print(f"  Total de perguntas comparadas: {len(comparacoes)}")
        return output_file
    
    def exportar_todos(self, output_dir: str = "exportacoes"):
        """Exporta todos os formatos"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("\n" + "="*80)
        print("EXPORTANDO RESULTADOS EM MÚLTIPLOS FORMATOS")
        print("="*80 + "\n")
        
        arquivos_gerados = []
        
        arquivos_gerados.append(self.exportar_json(output_path))
        arquivos_gerados.append(self.exportar_csv(output_path))
        arquivos_gerados.append(self.exportar_estatisticas_json(output_path))
        arquivos_gerados.append(self.exportar_respostas_problematicas(output_path))
        arquivos_gerados.append(self.exportar_comparacao_personas(output_path))
        
        print("\n" + "="*80)
        print("✓ EXPORTAÇÃO CONCLUÍDA!")
        print("="*80)
        print(f"\n{len(arquivos_gerados)} arquivos gerados em: {output_path.absolute()}\n")
        
        return arquivos_gerados


def main():
    """Função principal"""
    print("="*80)
    print("EXPORTADOR DE RESULTADOS")
    print("="*80)
    
    # Procurar arquivo consolidado
    resultados_path = Path(__file__).parent / "resultados"
    
    if not resultados_path.exists():
        print("\n❌ Pasta 'resultados' não encontrada!")
        return
    
    arquivos = list(resultados_path.glob("analise_consolidada_*.xlsx"))
    
    if not arquivos:
        print("\n❌ Nenhum arquivo consolidado encontrado!")
        return
    
    # Usar o mais recente
    arquivo = max(arquivos, key=lambda p: p.stat().st_mtime)
    
    print(f"\n✓ Arquivo encontrado: {arquivo.name}")
    
    # Criar exportador
    exporter = ResultsExporter(str(arquivo))
    
    # Exportar
    output_dir = resultados_path / "exportacoes"
    exporter.exportar_todos(str(output_dir))


if __name__ == "__main__":
    main()
