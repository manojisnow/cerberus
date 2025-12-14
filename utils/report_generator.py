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
        
        if 'consistency' in results and results['consistency']:
            md_content += "\n### DEPENDENCY CONSISTENCY\n\n"
            findings = results['consistency'].get('findings', [])
            if findings:
                for finding in findings:
                    md_content += f"**{finding['package']}** ({finding['type']})\n"
                    md_content += f"- **Severity**: {finding['severity']}\n"
                    md_content += f"- **Versions**: {', '.join(finding['versions'])}\n"
                    md_content += f"- **Remediation**: {finding['remediation']}\n\n"
            else:
                md_content += "No consistency issues found.\n\n"
        
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
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --bg: #f5f7fa;
            --card-bg: #ffffff;
            --text: #2d3748;
            --border: #e2e8f0;
            --critical: #e53e3e;
            --high: #dd6b20;
            --medium: #d69e2e;
            --low: #38a169;
            --info: #3182ce;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { margin: 0; font-size: 2.5rem; }
        .header p { margin: 10px 0 0; opacity: 0.9; }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }
        .card-label { color: #718096; font-size: 0.875rem; display: block; margin-bottom: 5px; }
        .card-value { font-weight: 600; font-size: 1.1rem; }

        /* Dashboard Table */
        .dashboard {
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 40px;
        }
        .dashboard table {
            width: 100%;
            border-collapse: collapse;
        }
        .dashboard th {
            background: #f7fafc;
            text-align: left;
            padding: 15px 20px;
            font-weight: 600;
            color: #4a5568;
            border-bottom: 1px solid var(--border);
        }
        .dashboard td {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
        }
        .dashboard tr:last-child td { border-bottom: none; }
        .dashboard tr:hover { background: #f7fafc; }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            min-width: 30px;
            text-align: center;
        }
        .bg-critical { background: #fff5f5; color: var(--critical); }
        .bg-high { background: #fffaf0; color: var(--high); }
        .bg-medium { background: #fffff0; color: var(--medium); }
        .bg-low { background: #f0fff4; color: var(--low); }
        .bg-info { background: #ebf8ff; color: var(--info); }
        .bg-neutral { background: #edf2f7; color: #718096; }

        /* Collapsible Sections */
        .collapsible {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .collapsible-header {
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            transition: background 0.2s;
        }
        .collapsible-header:hover { background: #f7fafc; }
        .collapsible-header h2 { margin: 0; font-size: 1.25rem; color: #2d3748; }
        .toggle-icon {
            transition: transform 0.3s ease;
        }
        .collapsible.active .toggle-icon { transform: rotate(180deg); }
        
        .collapsible-content {
            padding: 0 20px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out, padding 0.3s ease;
            background: #fff;
            border-top: 1px solid transparent;
        }
        .collapsible.active .collapsible-content {
            padding: 20px;
            max-height: 5000px; /* Arbitrary large height */
            border-top: 1px solid var(--border);
            overflow: visible;
        }

        /* Scan Content Styling */
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }
        .vuln-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }
        .vuln-table th { background: #e2e8f0; padding: 10px; text-align: left; }
        .vuln-table td { border-bottom: 1px solid #edf2f7; padding: 10px; vertical-align: top; }
        
        .nav-link {
            text-decoration: none;
            color: var(--primary);
            font-weight: 600;
        }
        .nav-link:hover { text-decoration: underline; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div style="display: flex; align-items: center; gap: 20px;">
            <img src="data:{{ logo_mime }};base64,{{ logo_base64 }}" alt="Cerberus Logo" style="height: 80px; width: 80px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.3); object-fit: cover;">
            <div>
                <h1 style="margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">Cerberus Security Report</h1>
                <p style="margin: 5px 0 0; opacity: 0.9; font-size: 1.1rem;">Comprehensive Safety Analysis</p>
            </div>
        </div>
    </div>

    <div class="metadata-grid">
        <div class="card">
            <span class="card-label">Target Repository</span>
            <div class="card-value">{{ metadata.repo_path }}</div>
        </div>
        <div class="card">
            <span class="card-label">Scan Date</span>
            <div class="card-value">{{ metadata.start_time.strftime('%Y-%m-%d %H:%M') }}</div>
        </div>
        <div class="card">
            <span class="card-label">Duration</span>
            <div class="card-value">{{ "%.2f"|format(metadata.duration) }}s</div>
        </div>
    </div>

    <!-- Dashboard -->
    <div class="dashboard">
        <table>
            <thead>
                <tr>
                    <th>Scanner Category</th>
                    <th width="10%">Critical</th>
                    <th width="10%">High</th>
                    <th width="10%">Medium</th>
                    <th width="10%">Low</th>
                    <th width="10%">Info</th>
                    <th width="15%">Action</th>
                </tr>
            </thead>
            <tbody>
                {% for category, counts in summary.items() %}
                <tr>
                    <td><strong>{{ category | upper }}</strong></td>
                    <td><span class="badge {% if counts.critical %}bg-critical{% else %}bg-neutral{% endif %}">{{ counts.critical }}</span></td>
                    <td><span class="badge {% if counts.high %}bg-high{% else %}bg-neutral{% endif %}">{{ counts.high }}</span></td>
                    <td><span class="badge {% if counts.medium %}bg-medium{% else %}bg-neutral{% endif %}">{{ counts.medium }}</span></td>
                    <td><span class="badge {% if counts.low %}bg-low{% else %}bg-neutral{% endif %}">{{ counts.low }}</span></td>
                    <td><span class="badge {% if counts.info %}bg-info{% else %}bg-neutral{% endif %}">{{ counts.info }}</span></td>
                    <td><a href="#section-{{ category }}" class="nav-link" onclick="openSection('section-{{ category }}')">View Details →</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <!-- Build Status -->
        {% if results.get('build') %}
        <h3 style="margin-top: 30px; margin-bottom: 15px;">Build Status</h3>
        <table class="build-table" style="width: 100%; border-collapse: collapse; margin-bottom: 20px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background-color: #f8f9fa; border-bottom: 2px solid #e2e8f0;">
                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">Type</th>
                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">Artifact</th>
                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #4a5568;">Status</th>
                </tr>
            </thead>
            <tbody>
                {% for tool, items in results['build'].items() %}
                    {% for item in items %}
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 12px; color: #2d3748; vertical-align: top;">{{ tool|upper }}</td>
                        <td style="padding: 12px; color: #2d3748; vertical-align: top;">
                            {% if item.dir %}
                                {{ item.dir.split('/')[-1] }}
                            {% else %}
                                {{ item.image or item.file }}
                            {% endif %}
                        </td>
                        <td style="padding: 12px; vertical-align: top;">
                            <span class="badge" style="background-color: {{ '#48bb78' if item.status == 'success' else '#f56565' }}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">
                                {{ item.status|upper }}
                            </span>
                            {% if item.status != 'success' %}
                            <details style="margin-top: 10px;">
                                <summary style="cursor: pointer; color: #4299e1; font-size: 0.9em; outline: none;">View Error Log</summary>
                                <pre style="font-size: 0.8em; text-align: left; max-height: 300px; overflow: auto; background: #2d3748; color: #e2e8f0; padding: 12px; border-radius: 6px; margin-top: 8px; white-space: pre-wrap; font-family: 'Fira Code', monospace;">{{ item.log }}</pre>
                            </details>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>

    <!-- Sections -->
    <div id="sections">
        
        <!-- SECRETS -->
        {% if results.get('secrets') %}
        <div id="section-secrets" class="collapsible">
            <div class="collapsible-header" onclick="toggleSection(this.parentElement)">
                <h2>Secrets Detection (Gitleaks)</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="collapsible-content">
                {% if results['secrets'].get('gitleaks') %}
                    {{ gitleaks_html | safe }}
                {% else %}
                    <p>No secrets detected.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- DEPENDENCIES -->
        {% if results.get('dependencies') %}
        <div id="section-dependencies" class="collapsible">
            <div class="collapsible-header" onclick="toggleSection(this.parentElement)">
                <h2>Vulnerable Dependencies (Trivy)</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="collapsible-content">
                {% if results['dependencies'].get('trivy') %}
                    {{ trivy_deps_html | safe }}
                {% else %}
                    <p>No dependency vulnerabilities detected.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- IAC -->
        {% if results.get('iac') %}
        <div id="section-iac" class="collapsible">
            <div class="collapsible-header" onclick="toggleSection(this.parentElement)">
                <h2>Infrastructure as Code (Trivy/Checkov)</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="collapsible-content">
                {% if results['iac'].get('trivy') %}
                    <h4>Trivy IaC</h4>
                    {{ trivy_iac_html | safe }}
                {% endif %}
                {% if results['iac'].get('checkov') %}
                    <h4>Checkov</h4>
                    {{ checkov_html | safe }}
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- CONSISTENCY -->
        {% if results.get('consistency') %}
        <div id="section-consistency" class="collapsible">
            <div class="collapsible-header" onclick="toggleSection(this.parentElement)">
                <h2>Dependency Consistency (Diamond Dependencies)</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="collapsible-content">
                {% if results['consistency'].get('findings') %}
                    <div class="vuln-table-wrapper">
                    <table class="vuln-table">
                        <thead>
                            <tr>
                                <th>Package</th>
                                <th>Versions Detected</th>
                                <th>Severity</th>
                                <th>Remediation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for finding in results['consistency']['findings'] %}
                            <tr>
                                <td><strong>{{ finding.package }}</strong> <br><small>{{ finding.type }}</small></td>
                                <td>{{ ", ".join(finding.versions) }}</td>
                                <td><span class="badge bg-medium">{{ finding.severity }}</span></td>
                                <td>{{ finding.remediation }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    </div>
                {% else %}
                    <p>No consistency issues found. All dependencies are aligned.</p>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- SAST -->
        {% if results.get('sast') %}
        <div id="section-sast" class="collapsible">
            <div class="collapsible-header" onclick="toggleSection(this.parentElement)">
                <h2>Static Code Analysis (SAST)</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="collapsible-content">
                <p>Raw JSON Results:</p>
                <pre>{{ results['sast'] | tojson(indent=2) }}</pre>
            </div>
        </div>
        {% endif %}

        <!-- LINTING -->
        {% if results.get('linting') %}
        <div id="section-linting" class="collapsible">
            <div class="collapsible-header" onclick="toggleSection(this.parentElement)">
                <h2>Docker Linting (Hadolint)</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="collapsible-content">
                <pre>{{ results['linting'] | tojson(indent=2) }}</pre>
            </div>
        </div>
        {% endif %}

    </div>
    
    <div style="text-align: center; margin-top: 50px; color: #718096;">
        <p>Report generated by <strong>Cerberus v1.0.0</strong></p>
    </div>

</div>

<script>
    function toggleSection(element) {
        element.classList.toggle("active");
    }

    function openSection(id) {
        const el = document.getElementById(id);
        if (el) {
            el.classList.add("active");
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
</script>

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

        # Encode Logo
        import base64
        logo_base64 = ""
        mime_type = "image/jpeg" # default
        
        try:
            # Try PNG first
            logo_path = Path(__file__).parent / 'logo.png'
            if logo_path.exists():
                mime_type = "image/png"
            else:
                logo_path = Path(__file__).parent / 'logo.jpg'
                
            if logo_path.exists():
                with open(logo_path, "rb") as image_file:
                    logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"⚠️ Could not load logo: {e}")
        
        html_content = template.render(
            metadata=metadata,
            summary=summary,
            results=results,
            gitleaks_html=gitleaks_html,
            trivy_deps_html=trivy_deps_html,
            trivy_iac_html=trivy_iac_html,
            checkov_html=checkov_html,
            logo_base64=logo_base64,
            logo_mime=mime_type
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
        
        # Initialize structure for all expected scanners
        for scanner in ['secrets', 'dependencies', 'iac', 'sast', 'containers', 'helm', 'linting', 'consistency']:
            summary[scanner] = {
                'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0
            }

        # 1. Secrets (Gitleaks)
        if results.get('secrets', {}).get('gitleaks'):
            # Gitleaks findings are usually High/Critical. We'll count them as High by default if not specified
            findings = results['secrets']['gitleaks']
            summary['secrets']['high'] = len(findings)

        # 2. Dependencies (Trivy)
        if results.get('dependencies', {}).get('trivy', {}).get('Results'):
            for result in results['dependencies']['trivy']['Results']:
                if 'Vulnerabilities' in result:
                    for vuln in result['Vulnerabilities']:
                        severity = vuln.get('Severity', 'UNKNOWN').lower()
                        if severity in summary['dependencies']:
                            summary['dependencies'][severity] += 1
                        else:
                            summary['dependencies']['info'] += 1

        # 3. IaC (Trivy & Checkov)
        # Trivy IaC
        if results.get('iac', {}).get('trivy', {}).get('Results'):
             for result in results['iac']['trivy']['Results']:
                if 'Misconfigurations' in result:
                    for misconf in result['Misconfigurations']:
                        severity = misconf.get('Severity', 'UNKNOWN').lower()
                        if severity in summary['iac']:
                            summary['iac'][severity] += 1
                        else:
                            summary['iac']['info'] += 1
        # Checkov
        if results.get('iac', {}).get('checkov'):
            # Checkov format varies, assuming list of failed checks if structured simplified
            # Or if raw checkov output, we parse 'results' -> 'failed_checks'
            # For simplicity in this version, we count failures as Medium
            checkov_res = results['iac']['checkov']
            if isinstance(checkov_res, list):
                 summary['iac']['medium'] += len(checkov_res)
            elif isinstance(checkov_res, dict) and 'results' in checkov_res:
                 summary['iac']['medium'] += len(checkov_res.get('results', {}).get('failed_checks', []))

        # 4. Consistency
        if results.get('consistency', {}).get('findings'):
            for finding in results['consistency']['findings']:
                severity = finding.get('severity', 'medium').lower()
                if severity in summary['consistency']:
                    summary['consistency'][severity] += 1
                else:
                    summary['consistency']['info'] += 1

        # 5. SAST (Semgrep / SpotBugs)
        if results.get('sast'):
            # This depends on how SAST results are structured. 
            # Assuming simplified list or dict structure from scanners
            sast_res = results['sast']
            # Semgrep
            if isinstance(sast_res, dict) and 'results' in sast_res: # Standard Semgrep JSON
                for finding in sast_res['results']:
                    severity = finding.get('extra', {}).get('severity', 'medium').lower()
                    # Map semgrep severity (ERROR, WARNING, INFO) -> (High, Medium, Info)
                    if severity == 'error': summary['sast']['high'] += 1
                    elif severity == 'warning': summary['sast']['medium'] += 1
                    else: summary['sast']['info'] += 1
            # SpotBugs (simplified logic: if list of strings/dicts)
            # If our scanner returns raw text, we count as info. If dict list:
            elif isinstance(sast_res, list):
                 summary['sast']['medium'] += len(sast_res)
            elif isinstance(sast_res, dict) and 'spotbugs' in sast_res:
                 # If we structured it 'spotbugs': {'findings': []}
                 if isinstance(sast_res['spotbugs'], dict) and 'findings' in sast_res['spotbugs']:
                     summary['sast']['medium'] += len(sast_res['spotbugs']['findings'])
        
        # 6. Linting (Hadolint)
        if results.get('linting'):
            lint_res = results['linting']
            # If unified dict
            if isinstance(lint_res, dict):
                # Check for bad patterns or hadolint list
                if 'hadolint' in lint_res:
                     for file_res in lint_res['hadolint']:
                         if file_res.get('status') == 'issues_found':
                             # Parse output to count? Or just count files?
                             # Let's count total issues if possible, or just files as "Low".
                             # Parsing the JSON string in 'output' is expensive here effectively double parsing
                             # For now, count 1 per file with issues as "Low"
                             summary['linting']['low'] += 1
            elif isinstance(lint_res, list):
                summary['linting']['info'] += len(lint_res)

        return summary
