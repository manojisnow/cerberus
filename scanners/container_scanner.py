"""
Container Scanner - Scans container images for vulnerabilities
"""

import subprocess
import json
from typing import Dict, List


class ContainerScanner:
    """Scans container images using Trivy and Grype"""
    
    def __init__(self, config: dict):
        """
        Initialize ContainerScanner
        
        Args:
            config: Main configuration dictionary
        """
        self.config = config
        self.scanner_config = config.get('scanners', {}).get('containers', {})
        self.tools = self.scanner_config.get('tools', ['trivy', 'grype'])
    
    def scan(self, repo_path: str, artifacts: Dict) -> Dict:
        """
        Scan container images
        
        Args:
            repo_path: Path to repository
            artifacts: Detected artifacts including docker_images
        
        Returns:
            Dictionary containing scan results
        """
        results = {
            'trivy': [],
            'grype': []
        }
        
        # Scan Dockerfiles to identify image names
        docker_images = self._identify_images(artifacts.get('dockerfiles', []))
        
        for image in docker_images:
            if 'trivy' in self.tools:
                results['trivy'].append(self._run_trivy_image(image))
            
            if 'grype' in self.tools:
                results['grype'].append(self._run_grype_image(image))
        
        return results
    
    def _identify_images(self, dockerfiles: List[str]) -> List[str]:
        """
        Extract image names from Dockerfiles or use built images
        
        Args:
            dockerfiles: List of Dockerfile paths
        
        Returns:
            List of image names/tags
        """
        # This is a simplified version - in production, you'd parse Dockerfiles
        # or use docker images command to list built images
        images = []
        
        # Try to list locally built images
        try:
            result = subprocess.run(
                ['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and '<none>' not in line:
                        images.append(line)
        except:
            pass
        
        return images if images else ['alpine:latest']  # Fallback for demo
    
    def _run_trivy_image(self, image: str) -> Dict:
        """Run Trivy image scan"""
        try:
            cmd = [
                'trivy',
                'image',
                '--format', 'json',
                '--scanners', 'vuln',
                image
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                try:
                    return {
                        'image': image,
                        'results': json.loads(result.stdout),
                        'status': 'completed'
                    }
                except:
                    return {'image': image, 'findings': [], 'status': 'completed'}
            else:
                return {'image': image, 'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'image': image, 'error': 'Trivy scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'image': image, 'error': 'Trivy not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'image': image, 'error': str(e), 'status': 'error'}
    
    def _run_grype_image(self, image: str) -> Dict:
        """Run Grype image scan"""
        try:
            cmd = [
                'grype',
                image,
                '--output', 'json'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                try:
                    return {
                        'image': image,
                        'results': json.loads(result.stdout),
                        'status': 'completed'
                    }
                except:
                    return {'image': image, 'findings': [], 'status': 'completed'}
            else:
                return {'image': image, 'error': result.stderr, 'status': 'failed'}
                
        except subprocess.TimeoutExpired:
            return {'image': image, 'error': 'Grype scan timed out', 'status': 'timeout'}
        except FileNotFoundError:
            return {'image': image, 'error': 'Grype not installed', 'status': 'not_installed'}
        except Exception as e:
            return {'image': image, 'error': str(e), 'status': 'error'}
