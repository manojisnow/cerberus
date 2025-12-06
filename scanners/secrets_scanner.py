"""
Secrets Scanner - Detects hardcoded secrets and credentials
"""

import subprocess
import json
from typing import Dict


class SecretsScanner:
    """Scans for secrets using Gitleaks"""
    
    def __init__(self, config: dict):
        """
        Initialize SecretsScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('secrets', {})
        self.tools = self.scanner_config.get('tools', ['gitleaks'])
        self.timeout = config.get('performance', {}).get('scanner_timeout', 1800)
    
    def scan(self, repo_path: str) -> Dict:
        """
        Scan repository for secrets
        
        Args:
            repo_path: Path to repository
        
        Returns:
            Dictionary containing scan results
        """
        results = {'gitleaks': None}
        
        if 'gitleaks' in self.tools:
            results['gitleaks'] = self._run_gitleaks(repo_path)
        
        return results
    
    def _run_gitleaks(self, repo_path: str) -> Dict:
        """Run Gitleaks to detect secrets"""
        try:
            cmd = [
                'gitleaks',
                'detect',
                '--source', repo_path,
                '--report-format', 'json',
                '--report-path', '/tmp/gitleaks-report.json',
                '--no-git'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Gitleaks returns exit code 1 if secrets are found
            # Read the report file
            try:
                with open('/tmp/gitleaks-report.json', 'r') as f:
                    findings = json.load(f)
                    return findings if findings else []
            except FileNotFoundError:
                # No report file means no secrets found
                return []
            except json.JSONDecodeError:
                return []
                
        except subprocess.TimeoutExpired:
            return {'error': 'Gitleaks scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'error': 'Gitleaks not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
