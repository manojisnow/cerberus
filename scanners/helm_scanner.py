"""
Helm Scanner - Scans Helm charts for security issues
"""

import subprocess
import json
from typing import Dict, List


class HelmScanner:
    """Scans Helm charts using Kubescan, Kubeaudit, Helm lint, and Trivy"""
    
    def __init__(self, config: dict):
        """
        Initialize HelmScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('helm', {})
        self.tools = self.scanner_config.get('tools', ['kubescan', 'kubeaudit', 'helm-lint', 'trivy'])
    
    def scan(self, repo_path: str, artifacts: Dict) -> Dict:
        """
        Scan Helm charts
        
        Args:
            repo_path: Path to repository
            artifacts: Detected artifacts including helm_charts
        
        Returns:
            Dictionary containing scan results
        """
        results = {
            'kubescan': [],
            'kubeaudit': [],
            'helm_lint': [],
            'trivy': []
        }
        
        helm_charts = artifacts.get('helm_charts', [])
        
        for chart_path in helm_charts:
            if 'kubescan' in self.tools:
                results['kubescan'].append(self._run_kubescan(chart_path))
            
            if 'kubeaudit' in self.tools:
                results['kubeaudit'].append(self._run_kubeaudit(chart_path))
            
            if 'helm-lint' in self.tools:
                results['helm_lint'].append(self._run_helm_lint(chart_path))
            
            if 'trivy' in self.tools:
                results['trivy'].append(self._run_trivy_helm(chart_path))
        
        return results
    
    def _run_kubescan(self, chart_path: str) -> Dict:
        """Run Kubescape scan on Helm chart"""
        try:
            # Kubescape is the current name for kubescan
            cmd = [
                'kubescape',
                'scan',
                'framework', 'nsa',
                '--format', 'json',
                chart_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode in [0, 1]:
                try:
                    return {
                        'chart': chart_path,
                        'results': json.loads(result.stdout),
                        'status': 'completed'
                    }
                except:
                    return {'chart': chart_path, 'findings': [], 'status': 'completed'}
            else:
                return {'chart': chart_path, 'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'chart': chart_path, 'error': 'Kubescape scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'chart': chart_path, 'error': 'Kubescape not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'chart': chart_path, 'error': str(e), 'status': 'error'}
    
    def _run_kubeaudit(self, chart_path: str) -> Dict:
        """Run Kubeaudit on Helm chart"""
        try:
            # First template the chart, then audit
            template_cmd = ['helm', 'template', chart_path]
            template_result = subprocess.run(
                template_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if template_result.returncode != 0:
                return {'chart': chart_path, 'error': 'Failed to template chart', 'status': 'failed'}
            
            # Audit the templated output
            audit_cmd = ['kubeaudit', 'all', '-f', '-']
            audit_result = subprocess.run(
                audit_cmd,
                input=template_result.stdout,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'chart': chart_path,
                'output': audit_result.stdout,
                'status': 'completed'
            }
                
        except subprocess.TimeoutExpired:
            return {'chart': chart_path, 'error': 'Kubeaudit timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'chart': chart_path, 'error': 'Kubeaudit or Helm not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'chart': chart_path, 'error': str(e), 'status': 'error'}
    
    def _run_helm_lint(self, chart_path: str) -> Dict:
        """Run Helm lint"""
        try:
            cmd = ['helm', 'lint', chart_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'chart': chart_path,
                'output': result.stdout,
                'errors': result.stderr,
                'status': 'completed' if result.returncode == 0 else 'issues_found'
            }
                
        except subprocess.TimeoutExpired:
            return {'chart': chart_path, 'error': 'Helm lint timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'chart': chart_path, 'error': 'Helm not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'chart': chart_path, 'error': str(e), 'status': 'error'}
    
    def _run_trivy_helm(self, chart_path: str) -> Dict:
        """Run Trivy config scan on Helm chart"""
        try:
            cmd = [
                'trivy',
                'config',
                '--format', 'json',
                chart_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                try:
                    return {
                        'chart': chart_path,
                        'results': json.loads(result.stdout),
                        'status': 'completed'
                    }
                except:
                    return {'chart': chart_path, 'findings': [], 'status': 'completed'}
            else:
                return {'chart': chart_path, 'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'chart': chart_path, 'error': 'Trivy scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'chart': chart_path, 'error': 'Trivy not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'chart': chart_path, 'error': str(e), 'status': 'error'}
