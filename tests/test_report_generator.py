"""
Tests for report_generator module
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime
from utils.report_generator import ReportGenerator


def test_report_generator_initialization(mock_config):
    """Test ReportGenerator initialization"""
    generator = ReportGenerator(mock_config)
    
    assert generator.config == mock_config['reporting']
    assert generator.output_dir == Path(mock_config['reporting']['output_dir'])


def test_generate_json_report(mock_config, tmp_path):
    """Test JSON report generation"""
    # Update config to use tmp_path
    mock_config['reporting']['output_dir'] = str(tmp_path)
    generator = ReportGenerator(mock_config)
    
    # Mock results
    results = {
        'secrets': {'gitleaks': {'findings': [], 'status': 'completed'}},
        'sast': {'semgrep': {'findings': [], 'status': 'completed'}}
    }
    
    metadata = {
        'repo_path': '/test/repo',
        'start_time': datetime.now(),
        'end_time': datetime.now(),
        'duration': 10.5
    }
    
    generator.generate(results, metadata, 'json')
    
    # Check that JSON file was created
    json_files = list(tmp_path.glob('cerberus_report_*.json'))
    assert len(json_files) == 1
    
    # Verify JSON content
    with open(json_files[0]) as f:
        report = json.load(f)
    
    assert 'metadata' in report
    assert 'summary' in report
    assert 'results' in report
    assert report['metadata']['repository'] == '/test/repo'


def test_generate_markdown_report(mock_config, tmp_path):
    """Test Markdown report generation"""
    mock_config['reporting']['output_dir'] = str(tmp_path)
    generator = ReportGenerator(mock_config)
    
    results = {'secrets': {'gitleaks': {'findings': []}}}
    metadata = {
        'repo_path': '/test/repo',
        'start_time': datetime.now(),
        'end_time': datetime.now(),
        'duration': 10.5
    }
    
    generator.generate(results, metadata, 'markdown')
    
    # Check that Markdown file was created
    md_files = list(tmp_path.glob('cerberus_report_*.md'))
    assert len(md_files) == 1
    
    # Verify Markdown content
    content = md_files[0].read_text()
    assert '# Cerberus Security Scan Report' in content
    assert '/test/repo' in content


def test_generate_html_report(mock_config, tmp_path):
    """Test HTML report generation"""
    mock_config['reporting']['output_dir'] = str(tmp_path)
    generator = ReportGenerator(mock_config)
    
    results = {'secrets': {'gitleaks': {'findings': []}}}
    metadata = {
        'repo_path': '/test/repo',
        'start_time': datetime.now(),
        'end_time': datetime.now(),
        'duration': 10.5
    }
    
    generator.generate(results, metadata, 'html')
    
    # Check that HTML file was created
    html_files = list(tmp_path.glob('cerberus_report_*.html'))
    assert len(html_files) == 1
    
    # Verify HTML content
    content = html_files[0].read_text()
    assert '<!DOCTYPE html>' in content
    assert 'Cerberus Security Scan Report' in content
    assert '/test/repo' in content


def test_generate_summary(mock_config):
    """Test summary generation"""
    generator = ReportGenerator(mock_config)
    
    results = {
        'secrets': {'findings': [1, 2, 3]},
        'sast': {'findings': [1, 2]}
    }
    
    summary = generator._generate_summary(results)
    
    assert 'secrets' in summary
    assert 'sast' in summary
    assert all(key in summary['secrets'] for key in ['critical', 'high', 'medium', 'low', 'info'])
