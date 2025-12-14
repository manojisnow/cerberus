"""
IaC Scanner - Infrastructure-as-Code security scanning
"""

import subprocess
import json
from typing import Dict


class IaCScanner:
    """Scans IaC files for misconfigurations using Trivy and Checkov"""
    
    def __init__(self, config: dict):
        """
        Initialize IaCScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('iac', {})
        self.tools = self.scanner_config.get('tools', ['trivy', 'checkov'])
    
    def scan(self, repo_path: str, artifacts: Dict) -> Dict:
        """
        Scan IaC files for security issues
        
        Args:
            repo_path: Path to repository
            artifacts: Detected artifacts
        
        Returns:
            Dictionary containing scan results
        """
        results = {
            'trivy': None,
            'checkov': None
        }
        
        if 'trivy' in self.tools:
            results['trivy'] = self._run_trivy_config(repo_path)
        
        if 'checkov' in self.tools:
            results['checkov'] = self._run_checkov(repo_path)
        
        return results
    
    def _run_trivy_config(self, repo_path: str) -> Dict:
        """Run Trivy config scan"""
        try:
            cmd = [
                'trivy',
                'config',
                '--format', 'json',
                repo_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except:
                    return {'findings': [], 'status': 'completed'}
            else:
                return {'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Trivy config scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'error': 'Trivy not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _run_checkov(self, repo_path: str) -> Dict:
        """Run Checkov scan"""
        try:
            cmd = [
                'checkov',
                '--directory', repo_path,
                '--output', 'json',
                '--quiet',
                '--skip-path', 'reports'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Checkov returns non-zero if issues found
            if result.returncode in [0, 1]:
                try:
                    return json.loads(result.stdout)
                except:
                    return {'findings': [], 'status': 'completed'}
            else:
                return {'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Checkov scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'error': 'Checkov not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
