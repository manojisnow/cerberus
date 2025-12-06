"""
Tests for artifact_detector module
"""

import pytest
from pathlib import Path
from utils.artifact_detector import ArtifactDetector


def test_detect_maven_project(temp_repo, mock_config):
    """Test detection of Maven project"""
    detector = ArtifactDetector(temp_repo, mock_config)
    artifacts = detector.detect()
    
    assert 'build_files' in artifacts
    assert len(artifacts['build_files']) > 0
    assert artifacts['build_files'][0]['type'] == 'maven'
    assert 'pom.xml' in artifacts['build_files'][0]['path']


def test_detect_dockerfile(temp_repo, mock_config):
    """Test detection of Dockerfile"""
    detector = ArtifactDetector(temp_repo, mock_config)
    artifacts = detector.detect()
    
    assert 'dockerfiles' in artifacts
    assert len(artifacts['dockerfiles']) > 0
    assert 'Dockerfile' in artifacts['dockerfiles'][0]


def test_detect_java_files(temp_repo, mock_config):
    """Test that Java source files are present"""
    detector = ArtifactDetector(temp_repo, mock_config)
    
    # Verify Java files exist
    java_files = list(Path(temp_repo).rglob('*.java'))
    assert len(java_files) > 0


def test_no_helm_charts(temp_repo, mock_config):
    """Test that no Helm charts are detected when none exist"""
    detector = ArtifactDetector(temp_repo, mock_config)
    artifacts = detector.detect()
    
    assert 'helm_charts' in artifacts
    assert len(artifacts['helm_charts']) == 0


def test_artifact_detector_initialization(temp_repo, mock_config):
    """Test ArtifactDetector initialization"""
    detector = ArtifactDetector(temp_repo, mock_config)
    
    assert detector.repo_path == Path(temp_repo)
    assert detector.config == mock_config
    assert isinstance(detector.artifacts, dict)
