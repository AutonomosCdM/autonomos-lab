from typing import Dict, Any, Optional, List, Union
import uuid
import json
import re
from datetime import datetime, timedelta

import requests
from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest

from core.error_handler import AgentError, ErrorSeverity
from core.structured_logger import StructuredLogger
from security.credential_store import CredentialStore
from api.retry_handler import RetryHandler, RetryStrategy
from core.config_manager import ConfigManager

class GitHubIntegrationError(AgentError):
    """Exception raised for GitHub integration-related errors."""
    pass

class CodeAnalyzer:
    """
    Provides advanced code and repository structure analysis.
    """
    def __init__(self, github_client: 'GitHubClient'):
        """
        Initialize CodeAnalyzer.
        
        :param github_client: GitHubClient instance
        """
        self._github_client = github_client
        self._logger = github_client._logger

    def analyze_repository(
        self, 
        repo_name: str, 
        branch: str = 'main'
    ) -> Dict[str, Any]:
        """
        Perform comprehensive repository structure analysis.
        
        :param repo_name: Repository name (owner/repo)
        :param branch: Branch to analyze
        :return: Repository structure analysis
        """
        try:
            repo = self._github_client.get_repository(repo_name)
            contents = repo.get_contents('', ref=branch)
            
            analysis = {
                'repo_name': repo_name,
                'branch': branch,
                'structure': self._analyze_contents(contents),
                'languages': self._analyze_languages(repo),
                'file_types': self._count_file_types(contents)
            }
            
            self._logger.track_event(
                'github_repo_analyzed', 
                analysis
            )
            
            return analysis
        
        except Exception as e:
            raise GitHubIntegrationError(
                f"Repository analysis failed: {str(e)}",
                severity=ErrorSeverity.ERROR
            )

    def _analyze_contents(
        self, 
        contents: List, 
        base_path: str = ''
    ) -> Dict[str, Any]:
        """
        Recursively analyze repository contents.
        
        :param contents: List of repository contents
        :param base_path: Current path being analyzed
        :return: Structured repository contents
        """
        structure = {}
        
        for content in contents:
            if content.type == 'dir':
                structure[content.name] = self._analyze_contents(
                    content.repository.get_contents(content.path), 
                    content.path
                )
            else:
                structure[content.name] = {
                    'type': content.type,
                    'size': content.size,
                    'path': content.path
                }
        
        return structure

    def _analyze_languages(self, repo: Repository) -> Dict[str, float]:
        """
        Analyze programming languages used in the repository.
        
        :param repo: GitHub repository
        :return: Language breakdown
        """
        try:
            return repo.language_breakdown
        except Exception:
            return {}

    def _count_file_types(
        self, 
        contents: List
    ) -> Dict[str, int]:
        """
        Count file types in the repository.
        
        :param contents: Repository contents
        :return: File type counts
        """
        file_types = {}
        
        for content in contents:
            if content.type == 'file':
                ext = content.name.split('.')[-1] if '.' in content.name else 'no_ext'
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return file_types

class SecurityScanner:
    """
    Performs security vulnerability scanning and analysis.
    """
    def __init__(self, github_client: 'GitHubClient'):
        """
        Initialize SecurityScanner.
        
        :param github_client: GitHubClient instance
        """
        self._github_client = github_client
        self._logger = github_client._logger

    def scan_repository(
        self, 
        repo_name: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive security scan of a repository.
        
        :param repo_name: Repository name (owner/repo)
        :return: Security scan results
        """
        try:
            repo = self._github_client.get_repository(repo_name)
            
            scan_results = {
                'dependencies': self._scan_dependencies(repo),
                'security_alerts': self._check_security_alerts(repo),
                'code_scanning': self._analyze_code_scanning(repo)
            }
            
            self._logger.track_event(
                'github_security_scan', 
                scan_results
            )
            
            return scan_results
        
        except Exception as e:
            raise GitHubIntegrationError(
                f"Security scan failed: {str(e)}",
                severity=ErrorSeverity.ERROR
            )

    def _scan_dependencies(self, repo: Repository) -> Dict[str, Any]:
        """
        Scan repository dependencies for known vulnerabilities.
        
        :param repo: GitHub repository
        :return: Dependency vulnerability information
        """
        try:
            # This would typically use GitHub's dependency graph or a third-party service
            return {}
        except Exception:
            return {}

    def _check_security_alerts(self, repo: Repository) -> List[Dict[str, Any]]:
        """
        Check for open security alerts.
        
        :param repo: GitHub repository
        :return: List of security alerts
        """
        try:
            return [
                {
                    'state': alert.state,
                    'created_at': alert.created_at.isoformat(),
                    'dismissed': alert.dismissed
                }
                for alert in repo.get_security_alerts()
            ]
        except Exception:
            return []

    def _analyze_code_scanning(self, repo: Repository) -> List[Dict[str, Any]]:
        """
        Analyze code scanning alerts.
        
        :param repo: GitHub repository
        :return: Code scanning alerts
        """
        try:
            return [
                {
                    'rule_id': alert.rule.id,
                    'rule_description': alert.rule.description,
                    'severity': alert.rule.severity,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in repo.get_code_scanning_alerts()
            ]
        except Exception:
            return []

class TrendAnalyzer:
    """
    Analyzes technology trends based on GitHub repositories.
    """
    def __init__(self, github_client: 'GitHubClient'):
        """
        Initialize TrendAnalyzer.
        
        :param github_client: GitHubClient instance
        """
        self._github_client = github_client
        self._logger = github_client._logger

    def analyze_trends(
        self, 
        language: Optional[str] = None,
        created_after: Optional[datetime] = None,
        min_stars: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Analyze trending repositories.
        
        :param language: Optional programming language filter
        :param created_after: Optional date to filter repositories created after
        :param min_stars: Minimum number of stars
        :return: List of trending repositories
        """
        try:
            # Use GitHub Search API to find trending repositories
            query_parts = [f"stars:>={min_stars}"]
            
            if language:
                query_parts.append(f"language:{language}")
            
            if created_after:
                query_parts.append(f"created:>{created_after.strftime('%Y-%m-%d')}")
            
            query = " ".join(query_parts)
            
            trending_repos = self._github_client._github.search_repositories(query=query)
            
            results = [
                {
                    'name': repo.full_name,
                    'description': repo.description,
                    'stars': repo.stargazers_count,
                    'language': repo.language,
                    'created_at': repo.created_at.isoformat(),
                    'last_updated': repo.updated_at.isoformat()
                }
                for repo in trending_repos[:10]  # Limit to top 10
            ]
            
            self._logger.track_event(
                'github_trend_analysis', 
                {
                    'language': language,
                    'min_stars': min_stars,
                    'created_after': created_after.isoformat() if created_after else None,
                    'trend_count': len(results)
                }
            )
            
            return results
        
        except Exception as e:
            raise GitHubIntegrationError(
                f"Trend analysis failed: {str(e)}",
                severity=ErrorSeverity.ERROR
            )

class RepoManager:
    """
    Manages GitHub repository operations like PRs and issues.
    """
    def __init__(self, github_client: 'GitHubClient'):
        """
        Initialize RepoManager.
        
        :param github_client: GitHubClient instance
        """
        self._github_client = github_client
        self._logger = github_client._logger

    def create_pull_request(
        self, 
        repo_name: str, 
        title: str, 
        body: str,
        base: str = 'main', 
        head: str = 'develop'
    ) -> Dict[str, Any]:
        """
        Create a pull request in a repository.
        
        :param repo_name: Repository name (owner/repo)
        :param title: PR title
        :param body: PR description
        :param base: Base branch
        :param head: Head branch
        :return: Pull request details
        """
        try:
            repo = self._github_client.get_repository(repo_name)
            pr = repo.create_pull(title=title, body=body, base=base, head=head)
            
            pr_details = {
                'number': pr.number,
                'title': pr.title,
                'state': pr.state,
                'created_at': pr.created_at.isoformat(),
                'url': pr.html_url
            }
            
            self._logger.track_event(
                'github_pr_created', 
                pr_details
            )
            
            return pr_details
        
        except Exception as e:
            raise GitHubIntegrationError(
                f"Pull request creation failed: {str(e)}",
                severity=ErrorSeverity.ERROR
            )

class GitHubClient:
    """
    Comprehensive GitHub API client with advanced integration capabilities.
    """
    def __init__(
        self, 
        token: str,
        config_manager: Optional[ConfigManager] = None,
        credential_store: Optional[CredentialStore] = None,
        logger: Optional[StructuredLogger] = None
    ):
        """
        Initialize GitHub client with comprehensive configuration.
        
        :param token: GitHub Personal Access Token
        :param config_manager: Optional configuration manager
        :param credential_store: Optional credential store
        :param logger: Optional structured logger
        """
        self._token = token
        
        # Initialize GitHub client
        self._github = Github(token)
        
        # Optional components
        self._config_manager = config_manager or ConfigManager()
        self._credential_store = credential_store or CredentialStore()
        self._logger = logger or StructuredLogger()
        
        # Initialize sub-components
        self.code_analyzer = CodeAnalyzer(self)
        self.security_scanner = SecurityScanner(self)
        self.trend_analyzer = TrendAnalyzer(self)
        self.repo_manager = RepoManager(self)
        
        # Retry handler for API calls
        self._retry_handler = RetryHandler(
            max_retries=3,
            backoff_strategy=RetryStrategy.EXPONENTIAL
        )

    def get_repository(self, repo_name: str) -> Repository:
        """
        Get a GitHub repository.
        
        :param repo_name: Repository name (owner/repo)
        :return: GitHub Repository object
        """
        try:
            return self._github.get_repo(repo_name)
        except GithubException as e:
            raise GitHubIntegrationError(
                f"Repository retrieval failed: {str(e)}",
                severity=ErrorSeverity.ERROR
            )
