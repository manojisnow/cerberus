"""
Lint Scanner - Runs linting tools for best practices
"""

import subprocess
from typing import Dict, List


class LintScanner:
    """Runs linting tools like Hadolint for Dockerfiles"""
    
    def __init__(self, config: dict):
        """
        Initialize LintScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('linting', {})
        self.tools = self.scanner_config.get('tools', ['hadolint'])
    
    def scan(self, repo_path: str, artifacts: Dict) -> Dict:
        """
        Run linting checks
        
        Args:
            repo_path: Path to repository
            artifacts: Detected artifacts
        
        Returns:
            Dictionary containing scan results
        """
        results = {
            'hadolint': []
        }
        
        if 'hadolint' in self.tools and artifacts.get('dockerfiles'):
            for dockerfile in artifacts['dockerfiles']:
                results['hadolint'].append(self._run_hadolint(dockerfile))
        
        return results
    
    def _run_hadolint(self, dockerfile: str) -> Dict:
        """Run Hadolint on Dockerfile"""
        try:
            cmd = [
                'hadolint',
                '--format', 'json',
                dockerfile
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Hadolint returns 1 if issues found, 0 if clean
            if result.returncode == 0:
                status = 'completed'
            elif result.returncode == 1:
                status = 'issues_found'
            else:
                return {'dockerfile': dockerfile, 'error': f'Hadolint crashed with code {result.returncode}', 'status': 'error'}

            output = result.stdout
            if not output and status == 'issues_found':
                 return {'dockerfile': dockerfile, 'error': 'Hadolint returned status 1 but empty output', 'status': 'error'}

            return {
                'dockerfile': dockerfile,
                'output': output,
                'status': status
            }
                
        except subprocess.TimeoutExpired:
            return {'dockerfile': dockerfile, 'error': 'Hadolint timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'dockerfile': dockerfile, 'error': 'Hadolint not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'dockerfile': dockerfile, 'error': str(e), 'status': 'error'}
