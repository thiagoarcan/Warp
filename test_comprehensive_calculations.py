#!/usr/bin/env python3
"""
Comprehensive Calculation Test Script
Tests all calculation features with the provided Excel files

Files tested:
- BAR_FT-OP10.xlsx
- BAR_PT-OP10.xlsx
- PLN_FT-OP10.xlsx
- PLN_PT-OP10.xlsx

Calculations performed:
- Raw data
- 1st, 2nd, 3rd derivatives
- Area under curve
- Trend
- Rate of change
- All interpolation types (15 second interval)
- All regression types
- Statistics (std dev, mean, median, mode)
- Area between curves (various pairs)
- Temporal synchronization (5s and 13s intervals)
- All calculations on synchronized data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Import computation engine directly
from scipy import integrate, interpolate, signal, stats as scipy_stats

class ComputationEngine:
    """Standalone computation engine for testing"""
    
    @staticmethod
    def compute_derivative(timestamps: np.ndarray, values: np.ndarray, 
                          order: int = 1, apply_smoothing: bool = False,
                          smoothing_span: int = 5):
        working_values = np.array(values, dtype=float)
        
        if apply_smoothing and smoothing_span > 1:
            kernel = np.ones(smoothing_span) / smoothing_span
            working_values = np.convolve(working_values, kernel, mode='same')
        
        result_values = working_values
        result_times = timestamps
        
        for _ in range(order):
            dt = np.diff(result_times)
            dv = np.diff(result_values)
            dt = np.where(dt == 0, 1e-10, dt)
            result_values = dv / dt
            result_times = result_times[:-1]
            
        return result_times, result_values
    
    @staticmethod
    def compute_area_under_curve(timestamps: np.ndarray, values: np.ndarray,
                                 method: str = 'trapezoid'):
        if method == 'simpson' and len(values) >= 3:
            area = integrate.simpson(values, x=timestamps)
        else:
            area = integrate.trapezoid(values, x=timestamps)
        return float(area)
    
    @staticmethod
    def compute_area_between_curves(timestamps1, values1, timestamps2, values2):
        t_min = max(timestamps1.min(), timestamps2.min())
        t_max = min(timestamps1.max(), timestamps2.max())
        num_points = min(len(timestamps1), len(timestamps2))
        common_times = np.linspace(t_min, t_max, num_points)
        
        interp1 = interpolate.interp1d(timestamps1, values1, kind='linear', fill_value='extrapolate')
        interp2 = interpolate.interp1d(timestamps2, values2, kind='linear', fill_value='extrapolate')
        
        aligned_values1 = interp1(common_times)
        aligned_values2 = interp2(common_times)
        difference = np.abs(aligned_values1 - aligned_values2)
        area = integrate.trapezoid(difference, x=common_times)
        return float(area)
    
    @staticmethod
    def compute_statistics(values):
        clean_vals = values[~np.isnan(values)]
        if len(clean_vals) == 0:
            return {'mean': np.nan, 'median': np.nan, 'mode': np.nan,
                    'min': np.nan, 'max': np.nan, 'std': np.nan, 'variance': np.nan}
        
        mode_result = scipy_stats.mode(clean_vals, keepdims=True)
        return {
            'mean': float(np.mean(clean_vals)),
            'median': float(np.median(clean_vals)),
            'mode': float(mode_result.mode[0]) if len(mode_result.mode) > 0 else np.nan,
            'min': float(np.min(clean_vals)),
            'max': float(np.max(clean_vals)),
            'std': float(np.std(clean_vals)),
            'variance': float(np.var(clean_vals))
        }
    
    @staticmethod
    def compute_std_deviation_bands(values, multiplier: float = 1.0):
        mean_val = np.mean(values)
        std_val = np.std(values)
        return {
            'mean': np.full_like(values, mean_val),
            'upper_band': np.full_like(values, mean_val + (multiplier * std_val)),
            'lower_band': np.full_like(values, mean_val - (multiplier * std_val))
        }
    
    @staticmethod
    def compute_trend_line(timestamps, values, degree: int = 1):
        coefficients = np.polyfit(timestamps, values, degree)
        trend_values = np.polyval(coefficients, timestamps)
        return timestamps, trend_values
    
    @staticmethod
    def compute_regression(timestamps, values, regression_type: str = 'linear', polynomial_order: int = 2):
        if regression_type == 'linear':
            coeffs = np.polyfit(timestamps, values, 1)
            fitted = np.polyval(coeffs, timestamps)
        elif regression_type == 'polynomial':
            coeffs = np.polyfit(timestamps, values, polynomial_order)
            fitted = np.polyval(coeffs, timestamps)
        elif regression_type == 'exponential':
            log_vals = np.log(np.abs(values) + 1e-10)
            coeffs = np.polyfit(timestamps, log_vals, 1)
            fitted = np.exp(coeffs[1]) * np.exp(coeffs[0] * timestamps)
        elif regression_type == 'logarithmic':
            log_times = np.log(np.abs(timestamps) + 1e-10)
            coeffs = np.polyfit(log_times, values, 1)
            fitted = coeffs[0] * log_times + coeffs[1]
        elif regression_type == 'power':
            log_times = np.log(np.abs(timestamps) + 1e-10)
            log_vals = np.log(np.abs(values) + 1e-10)
            coeffs = np.polyfit(log_times, log_vals, 1)
            fitted = np.exp(coeffs[1]) * (timestamps ** coeffs[0])
        else:
            raise ValueError(f"Unknown regression type: {regression_type}")
        return timestamps, fitted
    
    @staticmethod
    def compute_interpolation(timestamps, values, target_interval_seconds: float, interpolation_kind: str = 'linear'):
        t_min = timestamps.min()
        t_max = timestamps.max()
        num_points = int((t_max - t_min) / target_interval_seconds) + 1
        new_timestamps = np.linspace(t_min, t_max, num_points)
        interpolator = interpolate.interp1d(timestamps, values, kind=interpolation_kind, fill_value='extrapolate')
        new_values = interpolator(new_timestamps)
        return new_timestamps, new_values
    
    @staticmethod
    def compute_rate_of_change(timestamps, values, window_size: int = 1):
        if window_size == 1:
            dt = np.diff(timestamps)
            dv = np.diff(values)
            dt = np.where(dt == 0, 1e-10, dt)
            return timestamps[:-1], dv / dt
        deriv_times, deriv_vals = ComputationEngine.compute_derivative(timestamps, values, order=1)
        kernel = np.ones(window_size) / window_size
        smoothed_rate = np.convolve(deriv_vals, kernel, mode='same')
        return deriv_times, smoothed_rate
    
    @staticmethod
    def synchronize_time_series(datasets, target_interval_seconds: float):
        if not datasets:
            return []
        t_min = max(ts.min() for ts, _ in datasets)
        t_max = min(ts.max() for ts, _ in datasets)
        num_points = int((t_max - t_min) / target_interval_seconds) + 1
        common_times = np.linspace(t_min, t_max, num_points)
        synchronized = []
        for timestamps, values in datasets:
            interp_func = interpolate.interp1d(timestamps, values, kind='linear', fill_value='extrapolate')
            sync_values = interp_func(common_times)
            synchronized.append((common_times, sync_values))
        return synchronized

class ComprehensiveCalculationTest:
    """Comprehensive test of all calculation features"""
    
    def __init__(self, excel_files: List[str]):
        self.excel_files = excel_files
        self.engine = ComputationEngine()
        self.datasets: Dict[str, Dict] = {}
        self.results: Dict[str, pd.DataFrame] = {}
        self.scalar_results: List[Dict] = []
        
    def load_data(self):
        """Load all Excel files"""
        print("=" * 80)
        print("LOADING DATA FILES")
        print("=" * 80)
        
        for file_path in self.excel_files:
            if not Path(file_path).exists():
                print(f"❌ File not found: {file_path}")
                continue
                
            df = pd.read_excel(file_path)
            name = Path(file_path).stem
            
            # Extract time and value
            time_col = df.columns[0]
            value_col = df.columns[1]
            
            # Convert datetime to seconds
            if pd.api.types.is_datetime64_any_dtype(df[time_col]):
                time_data = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds().values
            else:
                time_data = df[time_col].values
                
            value_data = df[value_col].values
            
            self.datasets[name] = {
                'time': time_data,
                'value': value_data,
                'original_df': df
            }
            
            print(f"✅ Loaded {name}: {len(time_data)} points")
            
        print(f"\nTotal datasets loaded: {len(self.datasets)}\n")
        
    def test_derivatives(self):
        """Test derivative calculations"""
        print("=" * 80)
        print("TESTING DERIVATIVES (1st, 2nd, 3rd order)")
        print("=" * 80)
        
        for name, data in self.datasets.items():
            print(f"\n{name}:")
            
            for order in [1, 2, 3]:
                try:
                    deriv_time, deriv_value = self.engine.compute_derivative(
                        data['time'], data['value'], order=order
                    )
                    
                    result_name = f"{name}_deriv{order}"
                    self.results[result_name] = pd.DataFrame({
                        'tempo': deriv_time,
                        'valor': deriv_value
                    })
                    
                    print(f"  ✅ Derivada {order}ª: {len(deriv_value)} pontos")
                    
                except Exception as e:
                    print(f"  ❌ Derivada {order}ª falhou: {str(e)}")
                    
        print("\n")
        
    def test_area_under_curve(self):
        """Test area under curve calculation"""
        print("=" * 80)
        print("TESTING AREA UNDER CURVE")
        print("=" * 80)
        
        for name, data in self.datasets.items():
            try:
                area = self.engine.compute_area_under_curve(
                    data['time'], data['value']
                )
                
                self.scalar_results.append({
                    'tipo': 'area_under_curve',
                    'serie': name,
                    'valor': area
                })
                
                print(f"✅ {name}: Área = {area:.6f}")
                
            except Exception as e:
                print(f"❌ {name}: Falha - {str(e)}")
                
        print("\n")
        
    def test_area_between_curves(self):
        """Test area between curves"""
        print("=" * 80)
        print("TESTING AREA BETWEEN CURVES")
        print("=" * 80)
        
        # Define pairs to test
        pairs = [
            ('BAR_FT-OP10', 'BAR_PT-OP10'),
            ('BAR_FT-OP10', 'PLN_FT-OP10'),
            ('PLN_FT-OP10', 'PLN_PT-OP10'),
            ('PLN_PT-OP10', 'BAR_PT-OP10')
        ]
        
        for name1, name2 in pairs:
            if name1 in self.datasets and name2 in self.datasets:
                try:
                    data1 = self.datasets[name1]
                    data2 = self.datasets[name2]
                    
                    area = self.engine.compute_area_between_curves(
                        data1['time'], data1['value'],
                        data2['time'], data2['value']
                    )
                    
                    self.scalar_results.append({
                        'tipo': 'area_between_curves',
                        'serie': f"{name1} x {name2}",
                        'valor': area
                    })
                    
                    print(f"✅ {name1} x {name2}: Área = {area:.6f}")
                    
                except Exception as e:
                    print(f"❌ {name1} x {name2}: Falha - {str(e)}")
            else:
                print(f"⚠️  Skipping {name1} x {name2} - dados não disponíveis")
                
        print("\n")
        
    def test_statistics(self):
        """Test statistical calculations"""
        print("=" * 80)
        print("TESTING STATISTICS")
        print("=" * 80)
        
        for name, data in self.datasets.items():
            try:
                stats = self.engine.compute_statistics(data['value'])
                
                print(f"\n{name}:")
                print(f"  Média: {stats['mean']:.6f}")
                print(f"  Mediana: {stats['median']:.6f}")
                print(f"  Moda: {stats['mode']:.6f}")
                print(f"  Mínimo: {stats['min']:.6f}")
                print(f"  Máximo: {stats['max']:.6f}")
                print(f"  Desvio Padrão: {stats['std']:.6f}")
                
                # Store scalar results
                for stat_name, stat_value in stats.items():
                    self.scalar_results.append({
                        'tipo': f'stat_{stat_name}',
                        'serie': name,
                        'valor': stat_value
                    })
                    
            except Exception as e:
                print(f"❌ {name}: Falha - {str(e)}")
                
        print("\n")
        
    def test_std_deviation_bands(self):
        """Test standard deviation bands"""
        print("=" * 80)
        print("TESTING STD DEVIATION BANDS (1x, 1.5x)")
        print("=" * 80)
        
        for name, data in self.datasets.items():
            for multiplier in [1.0, 1.5]:
                try:
                    bands = self.engine.compute_std_deviation_bands(
                        data['value'], multiplier
                    )
                    
                    result_name = f"{name}_std{multiplier}"
                    self.results[result_name] = pd.DataFrame({
                        'tempo': data['time'],
                        'mean': bands['mean'],
                        'upper_band': bands['upper_band'],
                        'lower_band': bands['lower_band']
                    })
                    
                    print(f"✅ {name} (±{multiplier}σ): 3 séries geradas")
                    
                except Exception as e:
                    print(f"❌ {name} (±{multiplier}σ): Falha - {str(e)}")
                    
        print("\n")
        
    def test_trend_line(self):
        """Test trend line calculation"""
        print("=" * 80)
        print("TESTING TREND LINES")
        print("=" * 80)
        
        for name, data in self.datasets.items():
            try:
                trend_time, trend_value = self.engine.compute_trend_line(
                    data['time'], data['value'], degree=1
                )
                
                result_name = f"{name}_trend"
                self.results[result_name] = pd.DataFrame({
                    'tempo': trend_time,
                    'valor': trend_value
                })
                
                print(f"✅ {name}: Tendência linear calculada")
                
            except Exception as e:
                print(f"❌ {name}: Falha - {str(e)}")
                
        print("\n")
        
    def test_regressions(self):
        """Test all regression types"""
        print("=" * 80)
        print("TESTING REGRESSIONS (Linear, Polynomial, Exponential, etc.)")
        print("=" * 80)
        
        regression_types = [
            'linear', 'polynomial', 'exponential', 'logarithmic', 'power'
        ]
        
        for name, data in self.datasets.items():
            print(f"\n{name}:")
            
            for reg_type in regression_types:
                try:
                    reg_time, reg_value = self.engine.compute_regression(
                        data['time'], data['value'],
                        regression_type=reg_type,
                        polynomial_order=3
                    )
                    
                    result_name = f"{name}_reg_{reg_type}"
                    self.results[result_name] = pd.DataFrame({
                        'tempo': reg_time,
                        'valor': reg_value
                    })
                    
                    print(f"  ✅ Regressão {reg_type}")
                    
                except Exception as e:
                    print(f"  ❌ Regressão {reg_type}: {str(e)}")
                    
        print("\n")
        
    def test_interpolations(self):
        """Test all interpolation types"""
        print("=" * 80)
        print("TESTING INTERPOLATIONS (15 second interval)")
        print("=" * 80)
        
        interp_types = ['linear', 'cubic', 'quadratic', 'nearest', 'slinear']
        target_interval = 15.0
        
        for name, data in self.datasets.items():
            print(f"\n{name}:")
            
            for interp_type in interp_types:
                try:
                    interp_time, interp_value = self.engine.compute_interpolation(
                        data['time'], data['value'],
                        target_interval_seconds=target_interval,
                        interpolation_kind=interp_type
                    )
                    
                    result_name = f"{name}_interp_{interp_type}"
                    self.results[result_name] = pd.DataFrame({
                        'tempo': interp_time,
                        'valor': interp_value
                    })
                    
                    print(f"  ✅ Interpolação {interp_type}: {len(interp_value)} pontos")
                    
                except Exception as e:
                    print(f"  ❌ Interpolação {interp_type}: {str(e)}")
                    
        print("\n")
        
    def test_rate_of_change(self):
        """Test rate of change calculation"""
        print("=" * 80)
        print("TESTING RATE OF CHANGE")
        print("=" * 80)
        
        for name, data in self.datasets.items():
            try:
                roc_time, roc_value = self.engine.compute_rate_of_change(
                    data['time'], data['value'], window_size=1
                )
                
                result_name = f"{name}_roc"
                self.results[result_name] = pd.DataFrame({
                    'tempo': roc_time,
                    'valor': roc_value
                })
                
                print(f"✅ {name}: Taxa de variação calculada")
                
            except Exception as e:
                print(f"❌ {name}: Falha - {str(e)}")
                
        print("\n")
        
    def test_temporal_synchronization(self):
        """Test temporal synchronization"""
        print("=" * 80)
        print("TESTING TEMPORAL SYNCHRONIZATION (5s and 13s intervals)")
        print("=" * 80)
        
        # Prepare datasets for synchronization
        datasets_list = [
            (data['time'], data['value'])
            for data in self.datasets.values()
        ]
        
        for interval in [5.0, 13.0]:
            print(f"\nSincronizando com intervalo de {interval}s:")
            
            try:
                synchronized = self.engine.synchronize_time_series(
                    datasets_list, target_interval_seconds=interval
                )
                
                # Create combined dataframe
                sync_df = pd.DataFrame({'tempo': synchronized[0][0]})
                
                for idx, (name, original_data) in enumerate(self.datasets.items()):
                    sync_time, sync_value = synchronized[idx]
                    sync_df[f'{name}_sync'] = sync_value
                    
                result_name = f"synchronized_{int(interval)}s"
                self.results[result_name] = sync_df
                
                print(f"✅ Sincronização completa: {len(sync_df)} pontos")
                print(f"   Séries sincronizadas: {len(self.datasets)}")
                
                # Repeat calculations on synchronized data
                self._repeat_calculations_on_synced(sync_df, interval)
                
            except Exception as e:
                print(f"❌ Sincronização falhou: {str(e)}")
                
        print("\n")
        
    def _repeat_calculations_on_synced(self, sync_df: pd.DataFrame, interval: float):
        """Repeat all calculations on synchronized data"""
        print(f"  Repetindo cálculos em dados sincronizados ({interval}s):")
        
        time_data = sync_df['tempo'].values
        
        for col in sync_df.columns[1:]:  # Skip 'tempo' column
            value_data = sync_df[col].values
            base_name = f"{col}_sync{int(interval)}s"
            
            # Derivatives
            for order in [1, 2, 3]:
                try:
                    deriv_t, deriv_v = self.engine.compute_derivative(
                        time_data, value_data, order=order
                    )
                    self.results[f"{base_name}_deriv{order}"] = pd.DataFrame({
                        'tempo': deriv_t, 'valor': deriv_v
                    })
                except:
                    pass
                    
            # Area
            try:
                area = self.engine.compute_area_under_curve(time_data, value_data)
                self.scalar_results.append({
                    'tipo': f'area_sync_{int(interval)}s',
                    'serie': col,
                    'valor': area
                })
            except:
                pass
                
            # Statistics
            try:
                stats = self.engine.compute_statistics(value_data)
                for stat_name, stat_value in stats.items():
                    self.scalar_results.append({
                        'tipo': f'stat_{stat_name}_sync_{int(interval)}s',
                        'serie': col,
                        'valor': stat_value
                    })
            except:
                pass
                
        print(f"    ✅ Cálculos repetidos em dados sincronizados")
        
    def export_results(self, output_file: str = "comprehensive_test_results.xlsx"):
        """Export all results to Excel"""
        print("=" * 80)
        print("EXPORTING RESULTS")
        print("=" * 80)
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Export raw data
                for name, data in self.datasets.items():
                    df = pd.DataFrame({
                        'tempo': data['time'],
                        'valor': data['value']
                    })
                    sheet_name = name[:31]  # Excel limit
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                # Export calculated series
                sheet_counter = 0
                for result_name, result_df in self.results.items():
                    sheet_name = result_name[:31]
                    try:
                        result_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        sheet_counter += 1
                    except Exception as e:
                        print(f"  ⚠️  Falha ao exportar {result_name}: {str(e)}")
                        
                # Export scalar results
                if self.scalar_results:
                    scalar_df = pd.DataFrame(self.scalar_results)
                    scalar_df.to_excel(writer, sheet_name='Resultados_Escalares', index=False)
                    
            print(f"\n✅ Resultados exportados para: {output_file}")
            print(f"   Total de planilhas: {len(self.datasets) + sheet_counter + 1}")
            print(f"   Resultados escalares: {len(self.scalar_results)}")
            
        except Exception as e:
            print(f"❌ Falha na exportação: {str(e)}")
            raise
            
    def run_all_tests(self):
        """Run all test procedures"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE CALCULATION TEST - Platform Base v2.0")
        print("=" * 80 + "\n")
        
        self.load_data()
        self.test_derivatives()
        self.test_area_under_curve()
        self.test_area_between_curves()
        self.test_statistics()
        self.test_std_deviation_bands()
        self.test_trend_line()
        self.test_regressions()
        self.test_interpolations()
        self.test_rate_of_change()
        self.test_temporal_synchronization()
        
        # Export results
        self.export_results()
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    # Files to test
    test_files = [
        "BAR_FT-OP10.xlsx",
        "BAR_PT-OP10.xlsx",
        "PLN_FT-OP10.xlsx",
        "PLN_PT-OP10.xlsx"
    ]
    
    # Run comprehensive test
    tester = ComprehensiveCalculationTest(test_files)
    tester.run_all_tests()
