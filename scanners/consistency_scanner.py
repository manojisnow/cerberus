"""
Consistency Scanner - Detects dependency version conflicts using SBOM analysis
"""

import subprocess
import json
import tempfile
import os
import shutil
from typing import Dict, List, Any

class ConsistencyScanner:
    """
    Analyzes software dependencies to find 'Diamond Dependency' conflicts
    (multiple versions of the same package).
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('scanners', {}).get('consistency', {}).get('enabled', True)
        
    def scan(self, repo_path: str, artifacts: Dict = None) -> Dict[str, Any]:
        """
        Generate SBOM via Syft and analyze for conflicts.
        """
        if not self.enabled:
            return {}

        if not shutil.which('syft'):
            return {'error': 'Syft binary not found', 'status': 'not_installed'}

        try:
            # Generate SBOM (CycloneDX JSON)
            # Use tempfile to avoid messy output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
                sbom_path = tmp_file.name

            # Run Syft
            # dir:. tells syft to scan the directory
            cmd = ['syft', 'packages', f'dir:{repo_path}', '-o', 'json']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                # Log stderr if failed
                return {'error': result.stderr, 'status': 'failed'}
            
            try:
                sbom_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                 return {'error': 'Failed to parse Syft output', 'status': 'failed'}

            # Analyze for duplicates
            findings = self._find_conflicts(sbom_data)
            
            return {
                'findings': findings,
                'status': 'completed',
                'tool': 'syft'
            }

        except subprocess.TimeoutExpired:
            return {'error': 'Syft analysis timed out', 'status': 'timeout'}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
        finally:
            if 'sbom_path' in locals() and os.path.exists(sbom_path):
                os.unlink(sbom_path)

    def _find_conflicts(self, sbom_data: Dict) -> List[Dict]:
        """
        Group packages by name and type, identifying those with >1 version.
        """
        packages = sbom_data.get('artifacts', [])
        registry = {} # Key: (name, type), Value: set(versions)

        for pkg in packages:
            name = pkg.get('name')
            ver = pkg.get('version')
            p_type = pkg.get('type')
            
            key = (name, p_type)
            if key not in registry:
                registry[key] = set()
            registry[key].add(ver)

        conflicts = []
        for (name, p_type), versions in registry.items():
            if len(versions) > 1:
                # Conflict found!
                sorted_versions = sorted(list(versions))
                
                remediation = self._generate_remediation(name, p_type, sorted_versions[-1])
                
                conflicts.append({
                    'package': name,
                    'type': p_type,
                    'versions': sorted_versions,
                    'severity': 'MEDIUM',
                    'description': f"Multiple versions of '{name}' detected: {', '.join(sorted_versions)}. This can lead to runtime errors or unpredictable behavior.",
                    'remediation': remediation
                })
        
        return conflicts

    def _generate_remediation(self, name: str, pkg_type: str, latest_version: str) -> str:
        """
        Generate ecosystem-specific advice to fix the conflict.
        """
        if 'maven' in pkg_type or 'java' in pkg_type:
            return (
                f"Identify the root cause using `mvn dependency:tree -Dverbose -Dincludes={name}`. "
                f"Then, force convergence by adding `{name}:{latest_version}` to the `<dependencyManagement>` section of your root pom.xml."
            )
        elif 'python' in pkg_type or 'pip' in pkg_type:
             return (
                 f"Check your requirements using `pipdeptree -p {name}`. "
                 f"Pin `{name}=={latest_version}` in your requirements.txt or use a lockfile manager like Poetry/Pipenv."
             )
        elif 'npm' in pkg_type or 'node' in pkg_type:
            return (
                f"Run `npm list {name}` to see the tree. "
                f"Consider using `npm dedupe` or adding an 'overrides' section in package.json for `{name}`."
            )
        else:
            return f"Investigate build configuration to ensure only version {latest_version} of {name} is used."
