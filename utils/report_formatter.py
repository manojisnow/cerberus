"""
Report Formatting Utilities - Format scanner results for better readability
"""

from typing import Dict, List, Any


class ReportFormatter:
    """Formats scanner results into readable tables and sections"""
    
    @staticmethod
    def format_trivy_results_markdown(trivy_data: Dict) -> str:
        """Format Trivy vulnerability results as Markdown tables"""
        if not trivy_data or not isinstance(trivy_data, dict):
            return "_No vulnerabilities found_\n"
        
        results = trivy_data.get('Results', [])
        if not results:
            return "_No vulnerabilities found_\n"
        
        md = ""
        for result in results:
            target = result.get('Target', 'Unknown')
            vulns = result.get('Vulnerabilities', [])
            
            if not vulns:
                continue
            
            md += f"\n#### {target}\n\n"
            md += "| CVE ID | Severity | Package | Installed | Fixed | Title |\n"
            md += "|--------|----------|---------|-----------|-------|-------|\n"
            
            for vuln in vulns:
                cve_id = vuln.get('VulnerabilityID', 'N/A')
                severity = vuln.get('Severity', 'UNKNOWN')
                pkg_name = vuln.get('PkgName', 'N/A')
                installed = vuln.get('InstalledVersion', 'N/A')
                fixed = vuln.get('FixedVersion', 'Not available')
                title = vuln.get('Title', 'No description')[:60]
                
                md += f"| {cve_id} | **{severity}** | {pkg_name} | {installed} | {fixed} | {title} |\n"
            
            md += "\n"
        
        return md
    
    @staticmethod
    def format_trivy_results_html(trivy_data: Dict) -> str:
        """Format Trivy vulnerability results as HTML tables"""
        if not trivy_data or not isinstance(trivy_data, dict):
            return "<p><em>No vulnerabilities found</em></p>"
        
        results = trivy_data.get('Results', [])
        if not results:
            return "<p><em>No vulnerabilities found</em></p>"
        
        html = ""
        for result in results:
            target = result.get('Target', 'Unknown')
            vulns = result.get('Vulnerabilities', [])
            
            if not vulns:
                continue
            
            html += f"<h4>{target}</h4>\n"
            html += '<table class="vuln-table">\n'
            html += '<thead><tr><th>CVE ID</th><th>Severity</th><th>Package</th><th>Installed</th><th>Fixed</th><th>Title</th></tr></thead>\n'
            html += '<tbody>\n'
            
            for vuln in vulns:
                cve_id = vuln.get('VulnerabilityID', 'N/A')
                severity = vuln.get('Severity', 'UNKNOWN')
                pkg_name = vuln.get('PkgName', 'N/A')
                installed = vuln.get('InstalledVersion', 'N/A')
                fixed = vuln.get('FixedVersion', 'Not available')
                title = vuln.get('Title', 'No description')
                
                severity_class = f"severity-{severity.lower()}"
                html += f'<tr><td><code>{cve_id}</code></td>'
                html += f'<td class="{severity_class}"><strong>{severity}</strong></td>'
                html += f'<td>{pkg_name}</td><td>{installed}</td><td>{fixed}</td>'
                html += f'<td>{title}</td></tr>\n'
            
            html += '</tbody>\n</table>\n'
        
        return html
    
    @staticmethod
    def format_gitleaks_results_markdown(gitleaks_data: List) -> str:
        """Format Gitleaks secrets as Markdown table"""
        if not gitleaks_data or not isinstance(gitleaks_data, list):
            return "_No secrets found_\n"
        
        md = "\n| File | Line | Secret Type | Match |\n"
        md += "|------|------|-------------|-------|\n"
        
        for finding in gitleaks_data:
            file_path = finding.get('File', 'Unknown')
            line = finding.get('StartLine', 'N/A')
            rule_id = finding.get('RuleID', 'Unknown')
            match = finding.get('Match', '')[:50] + '...' if len(finding.get('Match', '')) > 50 else finding.get('Match', '')
            
            md += f"| `{file_path}` | {line} | {rule_id} | `{match}` |\n"
        
        return md
    
    @staticmethod
    def format_gitleaks_results_html(gitleaks_data: List) -> str:
        """Format Gitleaks secrets as HTML table"""
        if not gitleaks_data or not isinstance(gitleaks_data, list):
            return "<p><em>No secrets found</em></p>"
        
        html = '<table class="vuln-table">\n'
        html += '<thead><tr><th>File</th><th>Line</th><th>Secret Type</th><th>Match</th></tr></thead>\n'
        html += '<tbody>\n'
        
        for finding in gitleaks_data:
            file_path = finding.get('File', 'Unknown')
            line = finding.get('StartLine', 'N/A')
            rule_id = finding.get('RuleID', 'Unknown')
            match = finding.get('Match', '')
            if len(match) > 50:
                match = match[:50] + '...'
            
            html += f'<tr><td><code>{file_path}</code></td>'
            html += f'<td>{line}</td><td>{rule_id}</td>'
            html += f'<td><code>{match}</code></td></tr>\n'
        
        html += '</tbody>\n</table>\n'
        return html
    
    @staticmethod
    def format_checkov_results_html(checkov_data: List) -> str:
        """Format Checkov IaC findings as HTML"""
        if not checkov_data or not isinstance(checkov_data, list):
            return "<p><em>No issues found</em></p>"
        
        html = ""
        for item in checkov_data:
            check_type = item.get('check_type', 'Unknown')
            results = item.get('results', {})
            
            html += f"<h4>{check_type.upper()}</h4>\n"
            
            passed_checks = results.get('passed_checks', [])
            failed_checks = results.get('failed_checks', [])
            
            if passed_checks:
                html += f'<p>✅ <strong>Passed</strong>: {len(passed_checks)} checks</p>\n'
            
            if failed_checks:
                html += f'<p>❌ <strong>Failed</strong>: {len(failed_checks)} checks</p>\n'
                html += '<table class="vuln-table">\n'
                html += '<thead><tr><th>Check ID</th><th>Name</th><th>File</th></tr></thead>\n'
                html += '<tbody>\n'
                
                for check in failed_checks[:15]:  # Limit to first 15
                    check_id = check.get('check_id', 'N/A')
                    name = check.get('check_name', 'Unknown')
                    file_path = check.get('file_path', 'Unknown')
                    
                    html += f'<tr><td><code>{check_id}</code></td><td>{name}</td>'
                    html += f'<td><code>{file_path}</code></td></tr>\n'
                
                html += '</tbody>\n</table>\n'
                
                if len(failed_checks) > 15:
                    html += f'<p><em>...and {len(failed_checks) - 15} more</em></p>\n'
        
        return html
    
    @staticmethod
    def format_checkov_results_markdown(checkov_data: List) -> str:
        """Format Checkov IaC findings as Markdown"""
        if not checkov_data or not isinstance(checkov_data, list):
            return "_No issues found_\n"
        
        md = ""
        for item in checkov_data:
            check_type = item.get('check_type', 'Unknown')
            results = item.get('results', {})
            
            md += f"\n#### {check_type.upper()}\n\n"
            
            passed_checks = results.get('passed_checks', [])
            failed_checks = results.get('failed_checks', [])
            
            if passed_checks:
                md += f"✅ **Passed**: {len(passed_checks)} checks\n\n"
            
            if failed_checks:
                md += f"❌ **Failed**: {len(failed_checks)} checks\n\n"
                md += "| Check ID | Name | File |\n"
                md += "|----------|------|------|\n"
                
                for check in failed_checks[:15]:  # Limit to first 15
                    check_id = check.get('check_id', 'N/A')
                    name = check.get('check_name', 'Unknown')
                    file_path = check.get('file_path', 'Unknown')
                    md += f"| {check_id} | {name} | `{file_path}` |\n"
                
                if len(failed_checks) > 15:
                    md += f"\n_...and {len(failed_checks) - 15} more_\n"
        
        return md
