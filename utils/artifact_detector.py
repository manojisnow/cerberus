"""
Artifact Detector - Identifies build artifacts and project structure
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List


class ArtifactDetector:
    """Detects artifacts and project structure in a repository"""
    
    def __init__(self, repo_path: str, config: dict):
        """
        Initialize ArtifactDetector
        
        Args:
            repo_path: Path to repository
            config: Main configuration dictionary
        """
        self.repo_path = Path(repo_path)
        self.config = config
        self.artifacts = {
            'dockerfiles': [],
            'helm_charts': [],
            'build_files': [],
            'jar_files': [],
            'war_files': [],
            'docker_images': [],
            'kubernetes_manifests': []
        }
    
    def detect(self) -> Dict[str, List[str]]:
        """
        Detect all artifacts in the repository
        
        Returns:
            Dictionary of artifact types and their paths
        """
        self._find_dockerfiles()
        self._find_helm_charts()
        self._find_build_files()
        self._find_java_artifacts()
        self._find_kubernetes_manifests()
        
        return self.artifacts
    
    def _find_dockerfiles(self):
        """Find all Dockerfiles in the repository"""
        for dockerfile in self.repo_path.rglob('Dockerfile*'):
            if dockerfile.is_file():
                self.artifacts['dockerfiles'].append(str(dockerfile))
    
    def _find_helm_charts(self):
        """Find Helm charts (Chart.yaml files)"""
        for chart_file in self.repo_path.rglob('Chart.yaml'):
            if chart_file.is_file():
                # Store the chart directory, not the Chart.yaml file
                chart_dir = str(chart_file.parent)
                self.artifacts['helm_charts'].append(chart_dir)
    
    def _find_build_files(self):
        """Find Java build files (pom.xml, build.gradle)"""
        # Maven
        for pom in self.repo_path.rglob('pom.xml'):
            if pom.is_file():
                self.artifacts['build_files'].append({
                    'type': 'maven',
                    'path': str(pom),
                    'dir': str(pom.parent)
                })
        
        # Gradle
        for gradle in self.repo_path.rglob('build.gradle*'):
            if gradle.is_file():
                self.artifacts['build_files'].append({
                    'type': 'gradle',
                    'path': str(gradle),
                    'dir': str(gradle.parent)
                })
    
    def _find_java_artifacts(self):
        """Find built Java artifacts (JAR, WAR, EAR files)"""
        for jar in self.repo_path.rglob('*.jar'):
            if jar.is_file() and 'target' in jar.parts or 'build' in jar.parts:
                self.artifacts['jar_files'].append(str(jar))
        
        for war in self.repo_path.rglob('*.war'):
            if war.is_file() and 'target' in war.parts or 'build' in war.parts:
                self.artifacts['war_files'].append(str(war))
    
    def _find_kubernetes_manifests(self):
        """Find Kubernetes manifest files"""
        k8s_patterns = ['deployment.yaml', 'deployment.yml', 'service.yaml', 
                       'service.yml', 'ingress.yaml', 'ingress.yml']
        
        for pattern in k8s_patterns:
            for manifest in self.repo_path.rglob(pattern):
                if manifest.is_file():
                    manifest_path = str(manifest)
                    if manifest_path not in self.artifacts['kubernetes_manifests']:
                        self.artifacts['kubernetes_manifests'].append(manifest_path)
    
    def build_artifacts(self) -> bool:
        """
        Build Java artifacts using detected build tools
        
        Returns:
            True if build succeeded
        """
        if not self.config['build']['enabled']:
            print("   Build disabled in configuration")
            return False
        
        if not self.artifacts['build_files']:
            print("   No build files found")
            return False
        
        success = True
        for build_file in self.artifacts['build_files']:
            build_type = build_file['type']
            build_dir = build_file['dir']
            
            print(f"   Building {build_type} project in {build_dir}")
            
            try:
                if build_type == 'maven':
                    success &= self._build_maven(build_dir)
                elif build_type == 'gradle':
                    success &= self._build_gradle(build_dir)
            except Exception as e:
                print(f"   ⚠️  Build failed: {str(e)}")
                success = False
        
        # Re-scan for newly built artifacts
        if success:
            self._find_java_artifacts()
        
        return success
    
    def _build_maven(self, build_dir: str) -> bool:
        """Build Maven project"""
        cmd = self.config['build'].get('command', 'mvn clean package -DskipTests')
        
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✓ Maven build successful")
                return True
            else:
                print(f"   ✗ Maven build failed: {result.stderr[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Maven build timed out")
            return False
        except Exception as e:
            print(f"   ✗ Maven build error: {str(e)}")
            return False
    
    def _build_gradle(self, build_dir: str) -> bool:
        """Build Gradle project"""
        # Check for gradle wrapper
        gradle_wrapper = Path(build_dir) / 'gradlew'
        if gradle_wrapper.exists():
            cmd = './gradlew clean build -x test'
        else:
            cmd = 'gradle clean build -x test'
        
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✓ Gradle build successful")
                return True
            else:
                print(f"   ✗ Gradle build failed: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Gradle build timed out")
            return False
        except Exception as e:
            print(f"   ✗ Gradle build error: {str(e)}")
            return False
