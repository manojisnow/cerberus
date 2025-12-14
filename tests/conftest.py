"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing"""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Create sample Java project structure
    (repo_path / "src" / "main" / "java").mkdir(parents=True)
    (repo_path / "src" / "test" / "java").mkdir(parents=True)
    
    # Create sample pom.xml
    pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>test-project</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>log4j</groupId>
            <artifactId>log4j</artifactId>
            <version>1.2.17</version>
        </dependency>
    </dependencies>
</project>
"""
    (repo_path / "pom.xml").write_text(pom_content)
    
    # Create sample Java file with potential issues
    java_content = """
package com.example;

public class TestClass {
    private static final String API_KEY = "TEST_KEY_PLACEHOLDER";
    
    public void vulnerableMethod(String input) {
        // SQL Injection vulnerability
        String query = "SELECT * FROM users WHERE name = '" + input + "'";
    }
}
"""
    (repo_path / "src" / "main" / "java" / "TestClass.java").write_text(java_content)
    
    # Create Dockerfile
    dockerfile_content = """FROM ubuntu:latest
RUN apt-get update
USER root
"""
    (repo_path / "Dockerfile").write_text(dockerfile_content)
    
    yield str(repo_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'build': {'enabled': False, 'tool': 'auto'},
        'scanners': {
            'secrets': {'enabled': True, 'tools': ['gitleaks']},
            'sast': {'enabled': True, 'tools': ['semgrep']},
            'dependencies': {'enabled': True, 'tools': ['trivy']},
            'iac': {'enabled': True, 'tools': ['trivy']},
            'containers': {'enabled': True, 'tools': ['trivy']},
            'helm': {'enabled': True, 'tools': ['helm-lint']},
            'linting': {'enabled': True, 'tools': ['hadolint']}
        },
        'severity': {'fail_on': 'HIGH', 'report_threshold': 'MEDIUM'},
        'reporting': {
            'formats': ['json'],
            'output_dir': './test-reports',
            'include_remediation': True,
            'executive_summary': True
        },
        'repository': {'temp_dir': '/tmp/cerberus-test', 'cleanup': True},
        'performance': {'max_parallel_scanners': 1, 'scanner_timeout': 60}
    }
