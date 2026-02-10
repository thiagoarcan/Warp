"""
Unit tests for XLSX to CSV converter
"""

import pytest
from pathlib import Path
import pandas as pd
from platform_base.utils.xlsx_to_csv import XlsxToCsvConverter


@pytest.fixture
def temp_xlsx_file(tmp_path):
    """Create a temporary XLSX file for testing"""
    filepath = tmp_path / "test_data.xlsx"
    
    # Create sample data
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1s'),
        'value1': range(100),
        'value2': [x * 2 for x in range(100)],
    })
    
    df.to_excel(filepath, index=False, engine='openpyxl')
    return filepath


@pytest.fixture
def temp_xlsx_multi_sheet(tmp_path):
    """Create a temporary XLSX file with multiple sheets"""
    filepath = tmp_path / "test_multi_sheet.xlsx"
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df1 = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        df2 = pd.DataFrame({'col3': [7, 8, 9], 'col4': [10, 11, 12]})
        df3 = pd.DataFrame({'col5': [13, 14, 15], 'col6': [16, 17, 18]})
        
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)
        df3.to_excel(writer, sheet_name='Sheet3', index=False)
    
    return filepath


class TestXlsxToCsvConverter:
    """Tests for XlsxToCsvConverter"""
    
    def test_init(self):
        """Test converter initialization"""
        converter = XlsxToCsvConverter()
        assert converter is not None
    
    def test_convert_single_sheet(self, temp_xlsx_file, tmp_path):
        """Test converting a single sheet XLSX to CSV"""
        converter = XlsxToCsvConverter()
        csv_path = tmp_path / "output.csv"
        
        result = converter.convert(temp_xlsx_file, csv_path)
        
        assert result is True
        assert csv_path.exists()
        
        # Verify CSV content
        df = pd.read_csv(csv_path)
        assert len(df) == 100
        assert 'value1' in df.columns
        assert 'value2' in df.columns
    
    def test_convert_auto_path(self, temp_xlsx_file):
        """Test conversion with auto-generated CSV path"""
        converter = XlsxToCsvConverter()
        
        result = converter.convert(temp_xlsx_file)
        
        assert result is True
        
        # Check if CSV was created in same directory
        expected_csv = temp_xlsx_file.with_suffix('.csv')
        assert expected_csv.exists()
    
    def test_convert_with_custom_delimiter(self, temp_xlsx_file, tmp_path):
        """Test conversion with custom delimiter"""
        converter = XlsxToCsvConverter()
        csv_path = tmp_path / "output_semicolon.csv"
        
        result = converter.convert(
            temp_xlsx_file,
            csv_path,
            delimiter=';'
        )
        
        assert result is True
        
        # Verify delimiter
        with open(csv_path, 'r') as f:
            first_line = f.readline()
            assert ';' in first_line
    
    def test_convert_with_custom_encoding(self, temp_xlsx_file, tmp_path):
        """Test conversion with custom encoding"""
        converter = XlsxToCsvConverter()
        csv_path = tmp_path / "output_latin1.csv"
        
        result = converter.convert(
            temp_xlsx_file,
            csv_path,
            encoding='latin-1'
        )
        
        assert result is True
        assert csv_path.exists()
    
    def test_convert_nonexistent_file(self, tmp_path):
        """Test conversion of nonexistent file"""
        converter = XlsxToCsvConverter()
        fake_path = tmp_path / "nonexistent.xlsx"
        
        result = converter.convert(fake_path)
        
        assert result is False
    
    def test_convert_all_sheets(self, temp_xlsx_multi_sheet, tmp_path):
        """Test converting all sheets to separate CSVs"""
        converter = XlsxToCsvConverter()
        
        result = converter.convert_all_sheets(
            temp_xlsx_multi_sheet,
            output_dir=tmp_path
        )
        
        assert len(result) == 3  # 3 sheets
        
        # Verify all CSV files were created
        for csv_path in result:
            assert Path(csv_path).exists()
    
    def test_get_sheet_names(self, temp_xlsx_multi_sheet):
        """Test getting sheet names from XLSX"""
        sheet_names = XlsxToCsvConverter.get_sheet_names(temp_xlsx_multi_sheet)
        
        assert len(sheet_names) == 3
        assert 'Sheet1' in sheet_names
        assert 'Sheet2' in sheet_names
        assert 'Sheet3' in sheet_names
    
    def test_preview_sheet(self, temp_xlsx_file):
        """Test previewing XLSX sheet"""
        df = XlsxToCsvConverter.preview_sheet(temp_xlsx_file, nrows=10)
        
        assert df is not None
        assert len(df) == 10
        assert 'value1' in df.columns
    
    def test_signals_emitted(self, temp_xlsx_file, tmp_path, qtbot):
        """Test that signals are emitted during conversion"""
        from PyQt6.QtCore import QSignalSpy
        
        converter = XlsxToCsvConverter()
        csv_path = tmp_path / "output.csv"
        
        progress_spy = QSignalSpy(converter.progress_updated)
        completed_spy = QSignalSpy(converter.conversion_completed)
        
        result = converter.convert(temp_xlsx_file, csv_path)
        
        assert result is True
        assert len(progress_spy) > 0  # At least one progress update
        assert len(completed_spy) == 1  # Completion signal
    
    def test_failed_signal(self, tmp_path, qtbot):
        """Test that failed signal is emitted on error"""
        from PyQt6.QtCore import QSignalSpy
        
        converter = XlsxToCsvConverter()
        failed_spy = QSignalSpy(converter.conversion_failed)
        
        fake_path = tmp_path / "nonexistent.xlsx"
        result = converter.convert(fake_path)
        
        assert result is False
        assert len(failed_spy) == 1


@pytest.mark.integration
class TestXlsxConverterIntegration:
    """Integration tests for XLSX converter"""
    
    def test_convert_and_reload(self, temp_xlsx_file, tmp_path):
        """Test converting XLSX and reloading as CSV"""
        converter = XlsxToCsvConverter()
        csv_path = tmp_path / "output.csv"
        
        # Convert
        converter.convert(temp_xlsx_file, csv_path)
        
        # Load original XLSX
        df_xlsx = pd.read_excel(temp_xlsx_file)
        
        # Load converted CSV
        df_csv = pd.read_csv(csv_path)
        
        # Compare
        assert len(df_xlsx) == len(df_csv)
        assert list(df_xlsx.columns) == list(df_csv.columns)
    
    def test_large_file_conversion(self, tmp_path):
        """Test conversion of a large XLSX file"""
        # Create large XLSX
        large_xlsx = tmp_path / "large_data.xlsx"
        large_data = pd.DataFrame({
            'time': range(10000),
            'value': [x * 1.5 for x in range(10000)],
        })
        large_data.to_excel(large_xlsx, index=False, engine='openpyxl')
        
        # Convert
        converter = XlsxToCsvConverter()
        csv_path = tmp_path / "large_output.csv"
        result = converter.convert(large_xlsx, csv_path)
        
        assert result is True
        assert csv_path.exists()
        
        # Verify size
        df = pd.read_csv(csv_path)
        assert len(df) == 10000


@pytest.mark.smoke
class TestXlsxConverterSmoke:
    """Smoke tests for XLSX converter"""
    
    def test_converter_can_be_created(self):
        """Test that converter can be instantiated"""
        converter = XlsxToCsvConverter()
        assert converter is not None
    
    def test_static_methods(self):
        """Test that static methods can be called"""
        # These should not raise exceptions even with invalid paths
        sheets = XlsxToCsvConverter.get_sheet_names(Path("fake.xlsx"))
        assert sheets == []
        
        df = XlsxToCsvConverter.preview_sheet(Path("fake.xlsx"))
        assert df is None
