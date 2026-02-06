"""
XLSX to CSV Converter Utility

Converte arquivos Excel (.xlsx) para CSV com opções de configuração
"""

from pathlib import Path
from typing import Optional

import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal


class XlsxToCsvConverter(QObject):
    """
    Conversor de XLSX para CSV.
    
    Features:
    - Suporte para múltiplas sheets
    - Configuração de delimitador
    - Configuração de encoding
    - Progress tracking
    """
    
    progress_updated = pyqtSignal(int, str)  # (progress%, message)
    conversion_completed = pyqtSignal(str)  # filepath
    conversion_failed = pyqtSignal(str)  # error message
    
    def __init__(self):
        super().__init__()
    
    def convert(
        self,
        xlsx_path: str | Path,
        csv_path: str | Path | None = None,
        sheet_name: str | int | None = 0,
        delimiter: str = ",",
        encoding: str = "utf-8",
        include_index: bool = False,
    ) -> bool:
        """
        Converte arquivo XLSX para CSV.
        
        Args:
            xlsx_path: Caminho do arquivo XLSX de entrada
            csv_path: Caminho do arquivo CSV de saída (None = auto)
            sheet_name: Nome ou índice da sheet (None = primeira sheet)
            delimiter: Delimitador do CSV (padrão: ',')
            encoding: Encoding do arquivo CSV (padrão: 'utf-8')
            include_index: Se deve incluir o índice no CSV
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            xlsx_path = Path(xlsx_path)
            
            # Verifica se arquivo existe
            if not xlsx_path.exists():
                self.conversion_failed.emit(f"Arquivo não encontrado: {xlsx_path}")
                return False
            
            self.progress_updated.emit(10, "Lendo arquivo XLSX...")
            
            # Lê o arquivo XLSX
            df = pd.read_excel(xlsx_path, sheet_name=sheet_name, engine='openpyxl')
            
            self.progress_updated.emit(50, f"Lidas {len(df):,} linhas")
            
            # Determina caminho de saída
            if csv_path is None:
                csv_path = xlsx_path.with_suffix('.csv')
            else:
                csv_path = Path(csv_path)
            
            self.progress_updated.emit(70, f"Salvando para {csv_path.name}...")
            
            # Salva como CSV
            df.to_csv(
                csv_path,
                sep=delimiter,
                encoding=encoding,
                index=include_index,
            )
            
            self.progress_updated.emit(100, "Conversão concluída")
            self.conversion_completed.emit(str(csv_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Erro na conversão: {str(e)}"
            self.conversion_failed.emit(error_msg)
            return False
    
    def convert_all_sheets(
        self,
        xlsx_path: str | Path,
        output_dir: str | Path | None = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        include_index: bool = False,
    ) -> list[str]:
        """
        Converte todas as sheets de um XLSX para CSVs separados.
        
        Args:
            xlsx_path: Caminho do arquivo XLSX de entrada
            output_dir: Diretório de saída (None = mesmo dir do XLSX)
            delimiter: Delimitador do CSV
            encoding: Encoding dos arquivos CSV
            include_index: Se deve incluir o índice
        
        Returns:
            Lista de caminhos dos arquivos CSV criados
        """
        try:
            xlsx_path = Path(xlsx_path)
            
            if not xlsx_path.exists():
                self.conversion_failed.emit(f"Arquivo não encontrado: {xlsx_path}")
                return []
            
            # Determina diretório de saída
            if output_dir is None:
                output_dir = xlsx_path.parent
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            self.progress_updated.emit(5, "Lendo arquivo XLSX...")
            
            # Lê todas as sheets
            excel_file = pd.ExcelFile(xlsx_path, engine='openpyxl')
            sheet_names = excel_file.sheet_names
            
            total_sheets = len(sheet_names)
            converted_files = []
            
            for idx, sheet_name in enumerate(sheet_names):
                progress = int(10 + (idx / total_sheets) * 80)
                self.progress_updated.emit(
                    progress,
                    f"Convertendo sheet '{sheet_name}' ({idx+1}/{total_sheets})..."
                )
                
                # Lê sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Nome do arquivo CSV
                safe_sheet_name = "".join(
                    c if c.isalnum() or c in (' ', '_', '-') else '_'
                    for c in sheet_name
                )
                csv_filename = f"{xlsx_path.stem}_{safe_sheet_name}.csv"
                csv_path = output_dir / csv_filename
                
                # Salva como CSV
                df.to_csv(
                    csv_path,
                    sep=delimiter,
                    encoding=encoding,
                    index=include_index,
                )
                
                converted_files.append(str(csv_path))
            
            self.progress_updated.emit(100, f"Convertidas {total_sheets} sheets")
            self.conversion_completed.emit(f"{total_sheets} arquivos criados")
            
            return converted_files
            
        except Exception as e:
            error_msg = f"Erro na conversão: {str(e)}"
            self.conversion_failed.emit(error_msg)
            return []
    
    @staticmethod
    def get_sheet_names(xlsx_path: str | Path) -> list[str]:
        """Retorna lista de nomes de sheets em um arquivo XLSX"""
        try:
            excel_file = pd.ExcelFile(xlsx_path, engine='openpyxl')
            return excel_file.sheet_names
        except Exception:
            return []
    
    @staticmethod
    def preview_sheet(
        xlsx_path: str | Path,
        sheet_name: str | int | None = 0,
        nrows: int = 10
    ) -> Optional[pd.DataFrame]:
        """
        Preview de uma sheet do XLSX.
        
        Args:
            xlsx_path: Caminho do arquivo XLSX
            sheet_name: Nome ou índice da sheet
            nrows: Número de linhas para preview
        
        Returns:
            DataFrame com preview ou None se erro
        """
        try:
            df = pd.read_excel(
                xlsx_path,
                sheet_name=sheet_name,
                nrows=nrows,
                engine='openpyxl'
            )
            return df
        except Exception:
            return None
