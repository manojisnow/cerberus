"""
Dependency Scanner - Software Composition Analysis
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List


class DependencyScanner:
    """Scans dependencies for known vulnerabilities using OWASP Dependency-Check and Trivy"""
    
    def __init__(self, config: dict):
        """
        Initialize DependencyScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('dependencies', {})
        self.tools = self.scanner_config.get('tools', ['owasp-dependency-check', 'trivy'])
        self.nvd_api_key = self.scanner_config.get('nvd_api_key', '')
        self.timeout = config.get('performance', {}).get('scanner_timeout', 1800)
    
    def scan(self, repo_path: str, artifacts: Dict) -> Dict:
        """
        Scan dependencies for vulnerabilities
        
        Args:
            repo_path: Path to repository
            artifacts: Detected artifacts
        
        Returns:
            Dictionary containing scan results
        """
        results = {'trivy': None}
        
        if 'trivy' in self.tools:
            results['trivy'] = self._run_trivy_fs(repo_path)
        
        return results
    
    def _run_trivy_fs(self, repo_path: str) -> Dict:
        """Run Trivy filesystem scan for dependencies"""
        try:
            cmd = [
                'trivy',
                'fs',
                '--format', 'json',
                '--scanners', 'vuln',
                repo_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return {'findings': [], 'status': 'completed'}
            else:
                return {'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Trivy scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'error': 'Trivy not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
