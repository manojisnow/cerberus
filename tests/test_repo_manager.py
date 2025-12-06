"""
Tests for repo_manager module
"""

import pytest
import os
from utils.repo_manager import RepoManager


def test_repo_manager_initialization(mock_config):
    """Test RepoManager initialization"""
    repo_config = mock_config['repository']
    manager = RepoManager(repo_config)
    
    assert manager.temp_dir == repo_config['temp_dir']
    assert manager.cleanup_enabled == repo_config['cleanup']


def test_is_git_repo_false(temp_repo):
    """Test is_git_repo returns False for non-git directory"""
    repo_config = {'temp_dir': '/tmp/cerberus-test', 'cleanup': True}
    manager = RepoManager(repo_config)
    
    # temp_repo is not a git repository
    assert manager.is_git_repo(temp_repo) == False


def test_cleanup_disabled(temp_repo):
    """Test cleanup when disabled"""
    repo_config = {'temp_dir': '/tmp/cerberus-test', 'cleanup': False}
    manager = RepoManager(repo_config)
    
    # Should not raise error and directory should still exist
    manager.cleanup(temp_repo)
    assert os.path.exists(temp_repo)


def test_cleanup_enabled(mock_config):
    """Test cleanup when enabled"""
    import tempfile
    import shutil
    
    # Create a temp directory in the manager's temp_dir
    repo_config = mock_config['repository']
    manager = RepoManager(repo_config)
    
    # Create temp dir within manager's temp_dir
    os.makedirs(manager.temp_dir, exist_ok=True)
    test_dir = tempfile.mkdtemp(dir=manager.temp_dir)
    
    assert os.path.exists(test_dir)
    manager.cleanup(test_dir)
    assert not os.path.exists(test_dir)
    
    # Cleanup manager's temp_dir
    if os.path.exists(manager.temp_dir):
        shutil.rmtree(manager.temp_dir)
