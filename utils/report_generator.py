"""
Report Generator - Creates unified security reports in multiple formats
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from jinja2 import Template


class ReportGenerator:
    """Generates security scan reports in multiple formats"""
    
    def __init__(self, config: dict):
        """
        Initialize ReportGenerator
        
        Args:
            config: Reporting configuration from main config
        """
        self.config = config.get('reporting', {})
        self.output_dir = Path(self.config.get('output_dir', './reports'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, results: Dict[str, Any], metadata: Dict[str, Any], format: str):
        """
        Generate report in specified format
        
        Args:
            results: Scan results from all scanners
            metadata: Scan metadata (timestamps, repo info, etc.)
            format: Output format (json, html, markdown)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            self._generate_json(results, metadata, timestamp)
        elif format == 'html':
            self._generate_html(results, metadata, timestamp)
        elif format == 'markdown':
            self._generate_markdown(results, metadata, timestamp)
    
    def _generate_json(self, results: Dict, metadata: Dict, timestamp: str):
        """Generate JSON report"""
        output_file = self.output_dir / f'cerberus_report_{timestamp}.json'
        
        report = {
            'metadata': {
                'scan_time': metadata['start_time'].isoformat(),
                'duration_seconds': metadata['duration'],
                'repository': metadata['repo_path'],
                'cerberus_version': '1.0.0'
            },
            'summary': self._generate_summary(results),
            'results': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"   ✓ JSON report: {output_file}")
    
    def _generate_markdown(self, results: Dict, metadata: Dict, timestamp: str):
        """Generate Markdown report"""
        from utils.report_formatter import ReportFormatter
        
        output_file = self.output_dir / f'cerberus_report_{timestamp}.md'
        
        summary = self._generate_summary(results)
        
        md_content = f"""# Cerberus Security Scan Report

**Repository:** `{metadata['repo_path']}`  
**Scan Date:** {metadata['start_time'].strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {metadata['duration']:.2f} seconds  

---

## Executive Summary

| Category | Critical | High | Medium | Low | Info |
|----------|----------|------|--------|-----|------|
| **Secrets** | {summary.get('secrets', {}).get('critical', 0)} | {summary.get('secrets', {}).get('high', 0)} | {summary.get('secrets', {}).get('medium', 0)} | {summary.get('secrets', {}).get('low', 0)} | {summary.get('secrets', {}).get('info', 0)} |
| **SAST** | {summary.get('sast', {}).get('critical', 0)} | {summary.get('sast', {}).get('high', 0)} | {summary.get('sast', {}).get('medium', 0)} | {summary.get('sast', {}).get('low', 0)} | {summary.get('sast', {}).get('info', 0)} |
| **Dependencies** | {summary.get('dependencies', {}).get('critical', 0)} | {summary.get('dependencies', {}).get('high', 0)} | {summary.get('dependencies', {}).get('medium', 0)} | {summary.get('dependencies', {}).get('low', 0)} | {summary.get('dependencies', {}).get('info', 0)} |
| **IaC** | {summary.get('iac', {}).get('critical', 0)} | {summary.get('iac', {}).get('high', 0)} | {summary.get('iac', {}).get('medium', 0)} | {summary.get('iac', {}).get('low', 0)} | {summary.get('iac', {}).get('info', 0)} |
| **Containers** | {summary.get('containers', {}).get('critical', 0)} | {summary.get('containers', {}).get('high', 0)} | {summary.get('containers', {}).get('medium', 0)} | {summary.get('containers', {}).get('low', 0)} | {summary.get('containers', {}).get('info', 0)} |
| **Helm** | {summary.get('helm', {}).get('critical', 0)} | {summary.get('helm', {}).get('high', 0)} | {summary.get('helm', {}).get('medium', 0)} | {summary.get('helm', {}).get('low', 0)} | {summary.get('helm', {}).get('info', 0)} |
| **Linting** | {summary.get('linting', {}).get('critical', 0)} | {summary.get('linting', {}).get('high', 0)} | {summary.get('linting', {}).get('medium', 0)} | {summary.get('linting', {}).get('low', 0)} | {summary.get('linting', {}).get('info', 0)} |

---

## Detailed Findings

"""
        
        # Format specific scanners with custom formatters
        if 'secrets' in results and results['secrets']:
            md_content += "\n### SECRETS\n\n"
            if 'gitleaks' in results['secrets'] and results['secrets']['gitleaks']:
                md_content += "#### Gitleaks\n"
                md_content += ReportFormatter.format_gitleaks_results_markdown(results['secrets']['gitleaks'])
        
        if 'dependencies' in results and results['dependencies']:
            md_content += "\n### DEPENDENCIES\n\n"
            if 'trivy' in results['dependencies'] and results['dependencies']['trivy']:
                md_content += "#### Trivy\n"
                md_content += ReportFormatter.format_trivy_results_markdown(results['dependencies']['trivy'])
        
        if 'iac' in results and results['iac']:
            md_content += "\n### INFRASTRUCTURE AS CODE\n\n"
            if 'trivy' in results['iac'] and results['iac']['trivy']:
                md_content += "#### Trivy\n"
                md_content += ReportFormatter.format_trivy_results_markdown(results['iac']['trivy'])
            if 'checkov' in results['iac'] and results['iac']['checkov']:
                md_content += "\n#### Checkov\n"
                md_content += ReportFormatter.format_checkov_results_markdown(results['iac']['checkov'])
        
        # Add other scanners as JSON for now
        for scanner_name in ['sast', 'linting']:
            if scanner_name in results and results[scanner_name]:
                md_content += f"\n### {scanner_name.upper()}\n\n"
                md_content += f"```json\n{json.dumps(results[scanner_name], indent=2, default=str)}\n```\n\n"
        
        md_content += f"""
---

*Report generated by Cerberus Security Scanner v1.0.0*
"""
        
        with open(output_file, 'w') as f:
            f.write(md_content)
        
        print(f"   ✓ Markdown report: {output_file}")
    
    def _generate_html(self, results: Dict, metadata: Dict, timestamp: str):
        """Generate HTML report"""
        output_file = self.output_dir / f'cerberus_report_{timestamp}.html'
        
        summary = self._generate_summary(results)
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cerberus Security Scan Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .metadata-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metadata-item strong {
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }
        .summary-table {
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .summary-table table {
            width: 100%;
            border-collapse: collapse;
        }
        .summary-table th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }
        .summary-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        .summary-table tr:hover {
            background-color: #f8f9fa;
        }
        .severity-critical { color: #dc3545; font-weight: bold; }
        .severity-high { color: #fd7e14; font-weight: bold; }
        .severity-medium { color: #ffc107; font-weight: bold; }
        .severity-low { color: #28a745; }
        .severity-info { color: #17a2b8; }
        .section {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section h2 {
            color: #667eea;
            margin-top: 0;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .footer {
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }
        .vuln-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .vuln-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        .vuln-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        .vuln-table tr:hover {
            background-color: #f8f9fa;
        }
        .vuln-table code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐕 Cerberus Security Scan Report</h1>
        <p>Defense-in-Depth Security Analysis</p>
    </div>
    
    <div class="metadata">
        <div class="metadata-item">
            <strong>Repository</strong>
            {{ metadata.repo_path }}
        </div>
        <div class="metadata-item">
            <strong>Scan Date</strong>
            {{ metadata.start_time.strftime('%Y-%m-%d %H:%M:%S') }}
        </div>
        <div class="metadata-item">
            <strong>Duration</strong>
            {{ "%.2f"|format(metadata.duration) }} seconds
        </div>
        <div class="metadata-item">
            <strong>Cerberus Version</strong>
            1.0.0
        </div>
    </div>
    
    <div class="summary-table">
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Critical</th>
                    <th>High</th>
                    <th>Medium</th>
                    <th>Low</th>
                    <th>Info</th>
                </tr>
            </thead>
            <tbody>
                {% for category, counts in summary.items() %}
                <tr>
                    <td><strong>{{ category.upper() }}</strong></td>
                    <td class="severity-critical">{{ counts.get('critical', 0) }}</td>
                    <td class="severity-high">{{ counts.get('high', 0) }}</td>
                    <td class="severity-medium">{{ counts.get('medium', 0) }}</td>
                    <td class="severity-low">{{ counts.get('low', 0) }}</td>
                    <td class="severity-info">{{ counts.get('info', 0) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Detailed Findings</h2>
        {% if results.get('secrets') %}
            <h3>SECRETS</h3>
            {% if results['secrets'].get('gitleaks') %}
                <h4>Gitleaks</h4>
                {{ gitleaks_html | safe }}
            {% endif %}
        {% endif %}
        
        {% if results.get('dependencies') %}
            <h3>DEPENDENCIES</h3>
            {% if results['dependencies'].get('trivy') %}
                <h4>Trivy</h4>
                {{ trivy_deps_html | safe }}
            {% endif %}
        {% endif %}
        
        {% if results.get('iac') %}
            <h3>INFRASTRUCTURE AS CODE</h3>
            {% if results['iac'].get('trivy') %}
                <h4>Trivy</h4>
                {{ trivy_iac_html | safe }}
            {% endif %}
            {% if results['iac'].get('checkov') %}
                <h4>Checkov</h4>
                {{ checkov_html | safe }}
            {% endif %}
        {% endif %}
        
        {% if results.get('sast') %}
            <h3>SAST</h3>
            <pre>{{ results['sast'] | tojson(indent=2) }}</pre>
        {% endif %}
        
        {% if results.get('linting') %}
            <h3>LINTING</h3>
            <pre>{{ results['linting'] | tojson(indent=2) }}</pre>
        {% endif %}
    </div>
    
    <div class="footer">
        <p>Report generated by <strong>Cerberus Security Scanner v1.0.0</strong></p>
    </div>
</body>
</html>
"""
        
        template = Template(html_template)
        
        # Format scanner results for HTML
        from utils.report_formatter import ReportFormatter
        
        gitleaks_html = ReportFormatter.format_gitleaks_results_html(
            results.get('secrets', {}).get('gitleaks', [])
        )
        
        trivy_deps_html = ReportFormatter.format_trivy_results_html(
            results.get('dependencies', {}).get('trivy', {})
        )
        
        trivy_iac_html = ReportFormatter.format_trivy_results_html(
            results.get('iac', {}).get('trivy', {})
        )
        
        checkov_html = ReportFormatter.format_checkov_results_html(
            results.get('iac', {}).get('checkov', [])
        )
        
        html_content = template.render(
            metadata=metadata,
            summary=summary,
            results=results,
            gitleaks_html=gitleaks_html,
            trivy_deps_html=trivy_deps_html,
            trivy_iac_html=trivy_iac_html,
            checkov_html=checkov_html
        )
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"   ✓ HTML report: {output_file}")
    
    def _generate_summary(self, results: Dict) -> Dict:
        """
        Generate summary statistics from scan results
        
        Args:
            results: All scan results
        
        Returns:
            Summary dictionary with counts by severity
        """
        summary = {}
        
        for scanner_name, scanner_results in results.items():
            summary[scanner_name] = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
            
            # This is a placeholder - actual implementation would parse
            # scanner-specific result formats
            if isinstance(scanner_results, dict):
                summary[scanner_name]['info'] = len(scanner_results)
        
        return summary
