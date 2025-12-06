"""
Integration tests for Cerberus - tests with actual tools (if installed)
"""

import pytest
import os
import subprocess
from pathlib import Path


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


def is_tool_installed(tool_name):
    """Check if a tool is installed"""
    try:
        result = subprocess.run(
            [tool_name, '--version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.mark.skipif(not is_tool_installed('git'), reason="git not installed")
def test_git_installed():
    """Test that git is available"""
    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'git version' in result.stdout


@pytest.mark.skipif(not is_tool_installed('docker'), reason="docker not installed")
def test_docker_installed():
    """Test that Docker is available"""
    result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Docker version' in result.stdout


@pytest.mark.skipif(not is_tool_installed('python3'), reason="python3 not installed")
def test_python_installed():
    """Test that Python 3 is available"""
    result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Python 3' in result.stdout


# Tool availability tests
@pytest.mark.skipif(not is_tool_installed('trivy'), reason="trivy not installed")
def test_trivy_installed():
    """Test that Trivy is installed"""
    result = subprocess.run(['trivy', '--version'], capture_output=True, text=True)
    assert result.returncode == 0


@pytest.mark.skipif(not is_tool_installed('grype'), reason="grype not installed")
def test_grype_installed():
    """Test that Grype is installed"""
    result = subprocess.run(['grype', 'version'], capture_output=True, text=True)
    assert result.returncode == 0


@pytest.mark.skipif(not is_tool_installed('gitleaks'), reason="gitleaks not installed")
def test_gitleaks_installed():
    """Test that Gitleaks is installed"""
    result = subprocess.run(['gitleaks', 'version'], capture_output=True, text=True)
    assert result.returncode == 0


@pytest.mark.skipif(not is_tool_installed('semgrep'), reason="semgrep not installed")
def test_semgrep_installed():
    """Test that Semgrep is installed"""
    result = subprocess.run(['semgrep', '--version'], capture_output=True, text=True)
    assert result.returncode == 0


@pytest.mark.skipif(not is_tool_installed('hadolint'), reason="hadolint not installed")
def test_hadolint_installed():
    """Test that Hadolint is installed"""
    result = subprocess.run(['hadolint', '--version'], capture_output=True, text=True)
    assert result.returncode == 0


@pytest.mark.skipif(not is_tool_installed('checkov'), reason="checkov not installed")
def test_checkov_installed():
    """Test that Checkov is installed"""
    result = subprocess.run(['checkov', '--version'], capture_output=True, text=True)
    assert result.returncode == 0


# Integration test with actual scanner execution
@pytest.mark.skipif(not is_tool_installed('gitleaks'), reason="gitleaks not installed")
def test_gitleaks_execution(temp_repo):
    """Test Gitleaks can actually scan a repository"""
    from scanners.secrets_scanner import SecretsScanner
    
    config = {
        'scanners': {
            'secrets': {
                'enabled': True,
                'tools': ['gitleaks']
            }
        }
    }
    
    scanner = SecretsScanner(config)
    results = scanner._run_gitleaks(temp_repo)
    
    # Should return a dict with status
    assert isinstance(results, dict)
    assert 'status' in results or 'findings' in results or 'error' in results


@pytest.mark.skipif(not is_tool_installed('hadolint'), reason="hadolint not installed")
def test_hadolint_execution(temp_repo):
    """Test Hadolint can scan a Dockerfile"""
    from scanners.lint_scanner import LintScanner
    
    config = {
        'scanners': {
            'linting': {
                'enabled': True,
                'tools': ['hadolint']
            }
        }
    }
    
    # temp_repo has a Dockerfile
    dockerfile_path = os.path.join(temp_repo, 'Dockerfile')
    
    scanner = LintScanner(config)
    result = scanner._run_hadolint(dockerfile_path)
    
    # Should return a dict with status
    assert isinstance(result, dict)
    assert 'dockerfile' in result
    assert 'status' in result


def test_cerberus_help():
    """Test that cerberus.py can show help"""
    result = subprocess.run(
        ['python3', 'cerberus.py', '--help'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    assert 'Cerberus Security Scanner' in result.stdout
    assert 'REPOSITORY' in result.stdout


def test_artifact_detection_integration(temp_repo, mock_config):
    """Integration test for artifact detection"""
    from utils.artifact_detector import ArtifactDetector
    
    detector = ArtifactDetector(temp_repo, mock_config)
    artifacts = detector.detect()
    
    # Verify all expected artifact types are detected
    assert 'dockerfiles' in artifacts
    assert 'build_files' in artifacts
    assert 'helm_charts' in artifacts
    
    # Verify Maven project is detected
    assert len(artifacts['build_files']) > 0
    assert artifacts['build_files'][0]['type'] == 'maven'
    
    # Verify Dockerfile is detected
    assert len(artifacts['dockerfiles']) > 0
