"""
Repository Manager - Handles Git repository cloning and cleanup
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from git import Repo, GitCommandError


class RepoManager:
    """Manages repository cloning and cleanup operations"""
    
    def __init__(self, config: dict):
        """
        Initialize RepoManager
        
        Args:
            config: Repository configuration from main config
        """
        self.temp_dir = config.get('temp_dir', '/tmp/cerberus')
        self.cleanup_enabled = config.get('cleanup', True)
        
        # Ensure temp directory exists
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def clone(self, repo_url: str, branch: Optional[str] = None) -> str:
        """
        Clone a Git repository
        
        Args:
            repo_url: URL of the repository to clone
            branch: Optional branch name to checkout
        
        Returns:
            Path to cloned repository
        
        Raises:
            GitCommandError: If cloning fails
        """
        # Create unique directory for this clone
        clone_dir = tempfile.mkdtemp(dir=self.temp_dir, prefix='repo_')
        
        try:
            print(f"   Cloning into: {clone_dir}")
            
            if branch:
                Repo.clone_from(repo_url, clone_dir, branch=branch, depth=1)
            else:
                Repo.clone_from(repo_url, clone_dir, depth=1)
            
            print(f"   ✓ Repository cloned successfully")
            return clone_dir
            
        except GitCommandError as e:
            # Cleanup on failure
            if os.path.exists(clone_dir):
                shutil.rmtree(clone_dir)
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def cleanup(self, repo_path: str):
        """
        Clean up cloned repository
        
        Args:
            repo_path: Path to repository to clean up
        """
        if not self.cleanup_enabled:
            print(f"   Cleanup disabled, keeping: {repo_path}")
            return
        
        try:
            if os.path.exists(repo_path) and repo_path.startswith(self.temp_dir):
                shutil.rmtree(repo_path)
                print(f"   ✓ Cleaned up: {repo_path}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup {repo_path}: {str(e)}")
    
    def is_git_repo(self, path: str) -> bool:
        """
        Check if path is a Git repository
        
        Args:
            path: Path to check
        
        Returns:
            True if path is a Git repository
        """
        try:
            _ = Repo(path)
            return True
        except:
            return False
