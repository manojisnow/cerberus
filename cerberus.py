#!/usr/bin/env python3
"""
Cerberus Security Scanner
A comprehensive defense-in-depth security scanning tool for Java projects
"""

import sys
import os
import click
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from utils.repo_manager import RepoManager
from utils.artifact_detector import ArtifactDetector
from utils.report_generator import ReportGenerator
from scanners.secrets_scanner import SecretsScanner
from scanners.sast_scanner import SASTScanner
from scanners.dependency_scanner import DependencyScanner
from scanners.iac_scanner import IaCScanner
from scanners.container_scanner import ContainerScanner
from scanners.helm_scanner import HelmScanner
from scanners.lint_scanner import LintScanner
from scanners.consistency_scanner import ConsistencyScanner


class Cerberus:
    """Main orchestrator for Cerberus security scanning"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize Cerberus with configuration"""
        self.config = self._load_config(config_path)
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.repo_display_name = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            click.echo(f"⚠️  Config file not found: {config_path}", err=True)
            click.echo("Using default configuration", err=True)
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'build': {'enabled': True, 'tool': 'auto'},
            'scanners': {
                'secrets': {'enabled': True},
                'sast': {'enabled': True},
                'dependencies': {'enabled': True},
                'iac': {'enabled': True},
                'containers': {'enabled': True},
                'helm': {'enabled': True},
                'helm': {'enabled': True},
                'linting': {'enabled': True},
                'consistency': {'enabled': True}
            },
            'severity': {'fail_on': 'HIGH', 'report_threshold': 'MEDIUM'},
            'reporting': {
                'formats': ['json', 'html', 'markdown'],
                'output_dir': './reports',
                'include_remediation': True,
                'executive_summary': True
            },
            'repository': {'temp_dir': '/tmp/cerberus', 'cleanup': True},
            'performance': {'max_parallel_scanners': 3, 'scanner_timeout': 1800}
        }
    
    def scan(self, repo_path: str, is_url: bool = False) -> Dict:
        """
        Execute comprehensive security scan
        
        Args:
            repo_path: Path to local repository or repository URL
            is_url: Whether repo_path is a URL (requires cloning)
        
        Returns:
            Dictionary containing all scan results
        """
        self.start_time = datetime.now()
        click.echo("🐕 Cerberus Security Scanner Starting...")
        click.echo(f"⏰ Scan started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Store original repo path for reporting
        original_repo_path = repo_path
        
        # Step 1: Repository Management
        click.echo("📦 Step 1: Repository Management")
        repo_manager = RepoManager(self.config['repository'])
        
        if is_url:
            click.echo(f"   Cloning repository: {repo_path}")
            local_path = repo_manager.clone(repo_path)
        else:
            local_path = repo_path
            click.echo(f"   Using local repository: {local_path}")
        
        # Step 2: Artifact Detection
        click.echo("\n🔍 Step 2: Artifact Detection")
        detector = ArtifactDetector(local_path, self.config)
        artifacts = detector.detect()
        
        click.echo(f"   Found artifacts:")
        for artifact_type, items in artifacts.items():
            if items:
                click.echo(f"   • {artifact_type}: {len(items)} item(s)")
        
        # Step 3: Build Artifacts (if enabled)
        if self.config['build']['enabled'] and artifacts.get('build_files'):
            click.echo("\n🔨 Step 3: Building Artifacts")
            detector.build_artifacts()
        
        # Step 4: Source Code Scanning
        click.echo("\n🔐 Step 4: Source Code Security Scanning")
        self._run_source_scanners(local_path, artifacts)
        
        # Step 5: Artifact Scanning
        click.echo("\n📦 Step 5: Artifact Security Scanning")
        self._run_artifact_scanners(local_path, artifacts)
        
        # Step 6: Generate Reports (use original repo path)
        click.echo("\n📊 Step 6: Generating Reports")
        self._generate_reports(original_repo_path)
        
        # Cleanup
        if self.config['repository']['cleanup'] and is_url:
            click.echo("\n🧹 Cleaning up temporary files...")
            repo_manager.cleanup(local_path)
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        click.echo(f"\n✅ Scan completed in {duration:.2f} seconds")
        click.echo(f"📁 Reports saved to: {self.config['reporting']['output_dir']}")
        
        return self.results
    
    def _run_source_scanners(self, repo_path: str, artifacts: Dict):
        """Run all source code scanners"""
        scanners_config = self.config['scanners']
        
        # Secrets Scanner
        if scanners_config.get('secrets', {}).get('enabled', True):
            click.echo("   🔑 Running secrets detection...")
            scanner = SecretsScanner(self.config)
            self.results['secrets'] = scanner.scan(repo_path)
        
        # SAST Scanner
        if scanners_config.get('sast', {}).get('enabled', True):
            click.echo("   🐛 Running static application security testing...")
            scanner = SASTScanner(self.config)
            self.results['sast'] = scanner.scan(repo_path, artifacts)
        
        # Dependency Scanner
        if scanners_config.get('dependencies', {}).get('enabled', True):
            click.echo("   📚 Running dependency vulnerability scanning...")
            scanner = DependencyScanner(self.config)
            self.results['dependencies'] = scanner.scan(repo_path, artifacts)
        
        # IaC Scanner
        if scanners_config.get('iac', {}).get('enabled', True):
            click.echo("   ☁️  Running infrastructure-as-code scanning...")
            scanner = IaCScanner(self.config)
            self.results['iac'] = scanner.scan(repo_path, artifacts)
    
    def _run_artifact_scanners(self, repo_path: str, artifacts: Dict):
        """Run all artifact scanners"""
        scanners_config = self.config['scanners']
        
        # Container Scanner
        if scanners_config.get('containers', {}).get('enabled', True) and artifacts.get('docker_images'):
            click.echo("   🐳 Running container image scanning...")
            scanner = ContainerScanner(self.config)
            self.results['containers'] = scanner.scan(repo_path, artifacts)
        
        # Helm Scanner
        if scanners_config.get('helm', {}).get('enabled', True) and artifacts.get('helm_charts'):
            click.echo("   ⎈  Running Helm chart scanning...")
            scanner = HelmScanner(self.config)
            self.results['helm'] = scanner.scan(repo_path, artifacts)
        
        # Linting Scanner
        if scanners_config.get('linting', {}).get('enabled', True):
            click.echo("   ✨ Running linting checks...")
            scanner = LintScanner(self.config)
            self.results['linting'] = scanner.scan(repo_path, artifacts)

        # Consistency Scanner
        if scanners_config.get('consistency', {}).get('enabled', True):
            click.echo("   🔗 Checking Dependency Consistency (Diamond Dependencies)...")
            scanner = ConsistencyScanner(self.config)
            self.results['consistency'] = scanner.scan(repo_path, artifacts)
    
    def _generate_reports(self, repo_path: str):
        """Generate all configured report formats"""
        # Ensure end_time is set
        if self.end_time is None:
            self.end_time = datetime.now()
        
        report_gen = ReportGenerator(self.config)
        
        # Use display name if set, otherwise use repo_path
        display_path = self.repo_display_name if self.repo_display_name else repo_path
        
        scan_metadata = {
            'repo_path': display_path,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': (self.end_time - self.start_time).total_seconds()
        }
        
        formats = self.config['reporting']['formats']
        for fmt in formats:
            click.echo(f"   Generating {fmt.upper()} report...")
            report_gen.generate(self.results, scan_metadata, fmt)


@click.command()
@click.argument('repository', required=True)
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
@click.option('--url', is_flag=True, help='Repository argument is a URL (will be cloned)')
@click.option('--output', '-o', help='Output directory for reports (overrides config)')
@click.option('--repo-name', help='Display name for repository in reports (useful when running in Docker)')
def main(repository: str, config: str, url: bool, output: Optional[str], repo_name: Optional[str]):
    """
    Cerberus Security Scanner - Defense-in-depth security scanning for Java projects
    
    REPOSITORY: Path to local repository or repository URL (use --url flag for URLs)
    
    Examples:
    
        # Scan local repository
        cerberus /path/to/repo
        
        # Scan remote repository
        cerberus https://github.com/user/repo --url
        
        # Use custom config
        cerberus /path/to/repo --config custom-config.yaml
        
        # Override output directory
        cerberus /path/to/repo --output ./my-reports
    """
    try:
        scanner = Cerberus(config)
        
        # Override output directory if specified
        if output:
            scanner.config['reporting']['output_dir'] = output
        
        # Override repository display name if specified
        if repo_name:
            scanner.repo_display_name = repo_name
        else:
            scanner.repo_display_name = repository
        
        # Run scan
        results = scanner.scan(repository, is_url=url)
        
        # Check for failures based on severity threshold
        fail_threshold = scanner.config['severity']['fail_on']
        # TODO: Implement severity checking and exit code
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Scan interrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
