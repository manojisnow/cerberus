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
        """Find all Dockerfiles in the repository, excluding vendor directories"""
        exclusions = {'node_modules', 'vendor', '.git', 'target', 'build', 'dist', 'reports'}
        
        for dockerfile in self.repo_path.rglob('Dockerfile*'):
            if dockerfile.is_file():
                # Check for exclusions in path parts
                # We iterate parts to avoid partial string matches (e.g. 'builder' matching 'build')
                if not any(ex in dockerfile.parts for ex in exclusions):
                    self.artifacts['dockerfiles'].append(str(dockerfile))
    
    def _find_helm_charts(self):
        """Find Helm charts (Chart.yaml files)"""
        for chart_file in self.repo_path.rglob('Chart.yaml'):
            if chart_file.is_file():
                # Store the chart directory, not the Chart.yaml file
                chart_dir = str(chart_file.parent)
                self.artifacts['helm_charts'].append(chart_dir)
    
    def _find_build_files(self):
        """Find Maven and Gradle build files"""
        exclusions = {'node_modules', 'vendor', '.git', 'target', 'build', 'dist', 'reports'}
        
        # Maven
        for pom in self.repo_path.rglob('pom.xml'):
            if pom.is_file() and not any(ex in pom.parts for ex in exclusions):
                self.artifacts['build_files'].append({
                    'type': 'maven',
                    'path': str(pom),
                    'dir': str(pom.parent)
                })
        
        # Gradle
        for gradle in self.repo_path.rglob('build.gradle*'):
            if gradle.is_file() and not any(ex in gradle.parts for ex in exclusions):
                self.artifacts['build_files'].append({
                    'type': 'gradle',
                    'path': str(gradle),
                    'dir': str(gradle.parent)
                })
    
    def _find_java_artifacts(self):
        """Find compiled Java artifacts (JARs, WARs)"""
        exclusions = {'node_modules', 'vendor', '.git', 'reports'} # Don't exclude target/build here as that's where JARs are!
        
        for ext in ['*.jar', '*.war', '*.ear']:
            for artifact in self.repo_path.rglob(ext):
                if artifact.is_file() and not any(ex in artifact.parts for ex in exclusions):
                    self.artifacts['jar_files'].append(str(artifact))
        
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
    
    def build_artifacts(self) -> Dict[str, List[Dict]]:
        """
        Build artifacts using detected build tools and Dockerfiles.
        Only builds "Root" projects (multi-module parents) to avoid redundancy.
        
        Returns:
            Dictionary of build results (log, status) by tool
        """
        build_results = {
            'maven': [],
            'gradle': [],
            'docker': []
        }

        if not self.config['build']['enabled']:
            return build_results
        
        # Smart Build: Filter out child modules
        build_roots = self._filter_build_roots(self.artifacts['build_files'])
        
        # Build Java projects
        for build_file in build_roots:
            build_type = build_file['type']
            build_dir = build_file['dir']
            artifact_res = {'type': build_type, 'dir': build_dir, 'status': 'pending', 'log': ''}
            
            print(f"   Building {build_type} project in {build_dir}")
            
            try:
                if build_type == 'maven':
                    success, log = self._build_maven(build_dir)
                elif build_type == 'gradle':
                    success, log = self._build_gradle(build_dir)
                else:
                    success, log = False, "Unknown build type"
                
                artifact_res['status'] = 'success' if success else 'failed'
                artifact_res['log'] = log
                build_results[build_type].append(artifact_res)
                
            except Exception as e:
                print(f"   ⚠️  Build failed: {str(e)}")
                artifact_res['status'] = 'error'
                artifact_res['log'] = str(e)
                build_results[build_type].append(artifact_res)
        
        # Build Docker images
        if self.artifacts['dockerfiles']:
             docker_results = self._build_docker_images()
             build_results['docker'] = docker_results
        
        # Re-scan for newly built artifacts
        self._find_java_artifacts()
        
        return build_results

    def _filter_build_roots(self, build_files: List[Dict]) -> List[Dict]:
        """
        Identify root projects and exclude child modules.
        Currently supports Maven <modules>.
        """
        if not build_files:
            return []
            
        # 1. Index all build directories
        # Normalize paths to handle potential symlinks or formatting differences
        all_dirs = {str(Path(b['dir']).resolve()) for b in build_files}
        child_dirs = set()
        
        import xml.etree.ElementTree as ET
        
        for b in build_files:
            if b['type'] == 'maven':
                try:
                    pom_path = b['path']
                    tree = ET.parse(pom_path)
                    root = tree.getroot()
                    
                    # Namespace handling for pom.xml
                    ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
                    # Register namespace to search
                    
                    # Find modules
                    # Note: XML searching with namespaces can be tricky, try with and without
                    modules = root.findall('.//mvn:module', ns)
                    if not modules:
                        # Fallback for no namespace or default namespace
                        modules = root.findall('.//module')
                        
                    current_dir = Path(b['dir']).resolve()
                    
                    for module in modules:
                        module_name = module.text.strip()
                        child_path = (current_dir / module_name).resolve()
                        child_dirs.add(str(child_path))
                        
                except Exception as e:
                    # If we can't parse a pom, assume it's standalone
                    pass

        # 2. Filter list
        roots = []
        for b in build_files:
            b_dir = str(Path(b['dir']).resolve())
            if b_dir not in child_dirs:
                roots.append(b)
            else:
                # Debug log could go here
                pass
                
        return roots

    def _build_docker_images(self) -> List[Dict]:
        """Build discovered Dockerfiles"""
        print("   🐳 Building Docker images...")
        results = []
        
        for dockerfile_path in self.artifacts['dockerfiles']:
            res = {'file': dockerfile_path, 'status': 'pending', 'log': ''}
            try:
                path_obj = Path(dockerfile_path)
                build_dir = path_obj.parent
                
                # Create a unique tag based on folder name
                folder_name = build_dir.name
                if folder_name == '.':
                    folder_name = self.repo_path.name
                
                tag_name = "".join(c if c.isalnum() else "-" for c in folder_name).lower()
                image_tag = f"cerberus-scan/{tag_name}:latest"
                res['image'] = image_tag
                
                print(f"   Building Docker image for {folder_name} ({image_tag})...")
                
                cmd = ['docker', 'build', '-t', image_tag, '-f', path_obj.name, '.']
                
                result = subprocess.run(
                    cmd,
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                res['log'] = result.stdout + "\n" + result.stderr
                
                if result.returncode == 0:
                    print(f"   ✓ Image built: {image_tag}")
                    self.artifacts['docker_images'].append(image_tag)
                    res['status'] = 'success'
                else:
                    print(f"   ✗ Image build failed: {result.stderr[:200]}")
                    res['status'] = 'failed'
                    
            except Exception as e:
                print(f"   ✗ Error building Docker image: {str(e)}")
                res['status'] = 'error'
                res['log'] = str(e)
            
            results.append(res)
                
        return results
    
    def _build_maven(self, build_dir: str) -> (bool, str):
        """Build Maven project"""
        cmd = self.config['build'].get('command', 'mvn clean package -DskipTests')
        
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            log = result.stdout + "\n" + result.stderr
            if result.returncode == 0:
                print(f"   ✓ Maven build successful")
                return True, log
            else:
                print(f"   ✗ Maven build failed: {result.stderr[:500]}")
                return False, log
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Maven build timed out")
            return False, "Timed out"
        except Exception as e:
            print(f"   ✗ Maven build error: {str(e)}")
            return False, str(e)
    
    def _build_gradle(self, build_dir: str) -> (bool, str):
        """Build Gradle project"""
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
                timeout=600
            )
            
            log = result.stdout + "\n" + result.stderr
            if result.returncode == 0:
                print(f"   ✓ Gradle build successful")
                return True, log
            else:
                print(f"   ✗ Gradle build failed: {result.stderr[:200]}")
                return False, log
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ Gradle build timed out")
            return False, "Timed out"
        except Exception as e:
            print(f"   ✗ Gradle build error: {str(e)}")
            return False, str(e)
