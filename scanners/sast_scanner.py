"""
SAST Scanner - Static Application Security Testing for Java
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List


class SASTScanner:
    """Performs static analysis using Semgrep and SpotBugs/FindSecBugs"""
    
    def __init__(self, config: dict):
        """
        Initialize SASTScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('sast', {})
        self.tools = self.scanner_config.get('tools', ['semgrep', 'spotbugs'])
    
    def scan(self, repo_path: str, artifacts: Dict) -> Dict:
        """
        Perform SAST scanning
        
        Args:
            repo_path: Path to repository
            artifacts: Detected artifacts
        
        Returns:
            Dictionary containing scan results
        """
        results = {
            'semgrep': None,
            'spotbugs': None
        }
        
        if 'semgrep' in self.tools:
            results['semgrep'] = self._run_semgrep(repo_path)
        
        if 'spotbugs' in self.tools and artifacts.get('jar_files'):
            results['spotbugs'] = self._run_spotbugs(artifacts['jar_files'])
        
        return results
    
    def _run_semgrep(self, repo_path: str) -> Dict:
        """Run Semgrep with security rules"""
        try:
            cmd = [
                'semgrep',
                'scan',
                '--config', 'auto',  # Auto-detect rules
                '--json',
                repo_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode in [0, 1]:  # 0 = no findings, 1 = findings
                try:
                    return json.loads(result.stdout)
                except:
                    return {'findings': [], 'status': 'completed'}
            else:
                return {'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Semgrep scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'error': 'Semgrep not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def _run_spotbugs(self, jar_files: List[str]) -> Dict:
        """Run SpotBugs with FindSecBugs plugin"""
        all_findings = []
        
        for jar_file in jar_files:
            try:
                cmd = [
                    'spotbugs',
                    '-textui',
                    '-xml:withMessages',
                    '-output', '/tmp/spotbugs-report.xml',
                    jar_file
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                # SpotBugs returns 0 even with findings
                if result.returncode == 0:
                    # Parse XML output (simplified - would need proper XML parsing)
                    all_findings.append({
                        'jar': jar_file,
                        'status': 'completed',
                        'output': result.stdout
                    })
                else:
                    all_findings.append({
                        'jar': jar_file,
                        'error': result.stderr,
                        'status': 'failed'
                    })
                    
            except subprocess.TimeoutExpired:
                all_findings.append({
                    'jar': jar_file,
                    'error': 'SpotBugs scan timed out',
                    'status': 'timeout'
                })
            except FileNotFoundError:
                return {'error': 'SpotBugs not installed', 'status': 'not_installed'}
            except Exception as e:
                all_findings.append({
                    'jar': jar_file,
                    'error': str(e),
                    'status': 'error'
                })
        
        return {'findings': all_findings, 'status': 'completed'}
