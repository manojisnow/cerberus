"""
Tests for scanner modules
"""

import pytest
from scanners.secrets_scanner import SecretsScanner
from scanners.sast_scanner import SASTScanner
from scanners.dependency_scanner import DependencyScanner
from scanners.iac_scanner import IaCScanner
from scanners.container_scanner import ContainerScanner
from scanners.helm_scanner import HelmScanner
from scanners.lint_scanner import LintScanner


def test_secrets_scanner_initialization(mock_config):
    """Test SecretsScanner initialization"""
    scanner = SecretsScanner(mock_config)
    
    assert scanner.config == mock_config
    assert 'gitleaks' in scanner.tools


def test_sast_scanner_initialization(mock_config):
    """Test SASTScanner initialization"""
    scanner = SASTScanner(mock_config)
    
    assert scanner.config == mock_config
    assert scanner.scanner_config == mock_config['scanners']['sast']


def test_dependency_scanner_initialization(mock_config):
    """Test DependencyScanner initialization"""
    scanner = DependencyScanner(mock_config)
    
    assert scanner.config == mock_config
    assert scanner.tools is not None


def test_iac_scanner_initialization(mock_config):
    """Test IaCScanner initialization"""
    scanner = IaCScanner(mock_config)
    
    assert scanner.config == mock_config
    assert scanner.scanner_config == mock_config['scanners']['iac']


def test_container_scanner_initialization(mock_config):
    """Test ContainerScanner initialization"""
    scanner = ContainerScanner(mock_config)
    
    assert scanner.config == mock_config


def test_helm_scanner_initialization(mock_config):
    """Test HelmScanner initialization"""
    scanner = HelmScanner(mock_config)
    
    assert scanner.config == mock_config


def test_lint_scanner_initialization(mock_config):
    """Test LintScanner initialization"""
    scanner = LintScanner(mock_config)
    
    assert scanner.config == mock_config


def test_scanner_returns_dict(temp_repo, mock_config):
    """Test that scanners return dictionary results"""
    scanner = SecretsScanner(mock_config)
    results = scanner.scan(temp_repo)
    
    assert isinstance(results, dict)
    assert 'gitleaks' in results or 'trufflehog' in results


def test_scanner_handles_missing_tools(temp_repo, mock_config):
    """Test that scanners handle missing tools gracefully"""
    scanner = SecretsScanner(mock_config)
    results = scanner.scan(temp_repo)
    
    # Should return results even if tools aren't installed
    assert isinstance(results, dict)
    
    # Check for error status if tool not found
    for tool_result in results.values():
        if tool_result and isinstance(tool_result, dict):
            assert 'status' in tool_result or 'error' in tool_result or 'findings' in tool_result
