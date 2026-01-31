"""
Geração de relatórios de profiling conforme PRD

HTML reports and statistics generation
"""

import json
from datetime import datetime
from typing import Any

from .profiler import ProfilingResult


class ProfilingReport:
    """Gerador de relatórios de profiling"""

    def __init__(self, results: list[ProfilingResult]):
        self.results = results

    def generate_summary_html(self) -> str:
        """Gera relatório HTML resumido"""

        # Agrupa resultados por função
        by_function = {}
        for result in self.results:
            fname = result.function_name
            if fname not in by_function:
                by_function[fname] = []
            by_function[fname].append(result)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Platform Base - Profiling Report</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: -20px -20px 30px -20px;
        }}
        .metric {{
            display: inline-block;
            background: #f8f9fa;
            padding: 15px;
            margin: 10px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .metric-title {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .status-ok {{ color: #28a745; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .status-error {{ color: #dc3545; font-weight: bold; }}
        .function-name {{ font-family: monospace; color: #6f42c1; }}
        .duration {{ color: #007bff; }}
        .memory {{ color: #20c997; }}
        .section {{ margin: 30px 0; }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Platform Base v2.0 - Profiling Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="section">
            <div class="section-title">Summary</div>
            <div class="metric">
                <div class="metric-title">Total Functions</div>
                <div class="metric-value">{len(by_function)}</div>
            </div>
            <div class="metric">
                <div class="metric-title">Total Calls</div>
                <div class="metric-value">{len(self.results)}</div>
            </div>
            <div class="metric">
                <div class="metric-title">Avg Duration</div>
                <div class="metric-value">{sum(r.duration_seconds for r in self.results) / len(self.results) if self.results else 0:.3f}s</div>
            </div>
            <div class="metric">
                <div class="metric-title">Targets Met</div>
                <div class="metric-value">{sum(1 for r in self.results if r.performance_target_met)}/{len(self.results)}</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Function Performance</div>
            <table>
                <thead>
                    <tr>
                        <th>Function</th>
                        <th>Calls</th>
                        <th>Avg Duration</th>
                        <th>Max Duration</th>
                        <th>Avg Memory</th>
                        <th>Max Memory</th>
                        <th>Targets Met</th>
                    </tr>
                </thead>
                <tbody>
        """

        for fname, results in by_function.items():
            durations = [r.duration_seconds for r in results]
            memory_peaks = [r.memory_peak_mb for r in results]
            targets_met = sum(1 for r in results if r.performance_target_met)

            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            avg_memory = sum(memory_peaks) / len(memory_peaks) if memory_peaks else 0
            max_memory = max(memory_peaks) if memory_peaks else 0

            target_status = "ok" if targets_met == len(results) else ("warning" if targets_met > 0 else "error")

            html += f"""
                    <tr>
                        <td class="function-name">{fname.split('.')[-1]}</td>
                        <td>{len(results)}</td>
                        <td class="duration">{avg_duration:.3f}s</td>
                        <td class="duration">{max_duration:.3f}s</td>
                        <td class="memory">{avg_memory:.1f}MB</td>
                        <td class="memory">{max_memory:.1f}MB</td>
                        <td class="status-{target_status}">{targets_met}/{len(results)}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <div class="section-title">Recent Calls</div>
            <table>
                <thead>
                    <tr>
                        <th>Function</th>
                        <th>Duration</th>
                        <th>Memory Peak</th>
                        <th>CPU Stats</th>
                        <th>Target Met</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Mostra últimas 20 calls
        recent_results = self.results[-20:]
        for result in reversed(recent_results):
            status = "ok" if result.performance_target_met else "error"

            html += f"""
                    <tr>
                        <td class="function-name">{result.function_name.split('.')[-1]}</td>
                        <td class="duration">{result.duration_seconds:.3f}s</td>
                        <td class="memory">{result.memory_peak_mb:.1f}MB</td>
                        <td>{result.cpu_stats.get('function_count', 0)} funcs</td>
                        <td class="status-{status}">{'✓' if result.performance_target_met else '✗'}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """

        return html

    def generate_json_summary(self) -> dict[str, Any]:
        """Gera resumo em JSON para APIs"""
        by_function = {}
        for result in self.results:
            fname = result.function_name
            if fname not in by_function:
                by_function[fname] = []
            by_function[fname].append(result)

        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_functions": len(by_function),
            "total_calls": len(self.results),
            "functions": {},
        }

        for fname, results in by_function.items():
            durations = [r.duration_seconds for r in results]
            memory_peaks = [r.memory_peak_mb for r in results]
            targets_met = sum(1 for r in results if r.performance_target_met)

            summary["functions"][fname] = {
                "call_count": len(results),
                "duration": {
                    "min": min(durations),
                    "max": max(durations),
                    "avg": sum(durations) / len(durations),
                    "total": sum(durations),
                },
                "memory": {
                    "avg_peak": sum(memory_peaks) / len(memory_peaks) if memory_peaks else 0,
                    "max_peak": max(memory_peaks) if memory_peaks else 0,
                },
                "targets": {
                    "met": targets_met,
                    "total": len(results),
                    "success_rate": targets_met / len(results) if results else 0,
                },
            }

        return summary


def generate_html_report(results: list[ProfilingResult], output_file: str):
    """Gera e salva relatório HTML"""
    report = ProfilingReport(results)
    html = report.generate_summary_html()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)


def generate_json_report(results: list[ProfilingResult], output_file: str):
    """Gera e salva relatório JSON"""
    report = ProfilingReport(results)
    data = report.generate_json_summary()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
