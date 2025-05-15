"""
Data models for the Redmine MCPServer
"""
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IssueStatus:
    """Redmine issue status model"""
    id: int
    name: str
    is_closed: bool = False


@dataclass
class Tracker:
    """Redmine tracker model"""
    id: int
    name: str


@dataclass
class Priority:
    """Redmine priority model"""
    id: int
    name: str


@dataclass
class User:
    """Redmine user model"""
    id: int
    login: str
    firstname: str
    lastname: str
    mail: Optional[str] = None
    created_on: Optional[datetime] = None
    last_login_on: Optional[datetime] = None
    admin: bool = False
    status: int = 1
    
    @property
    def full_name(self) -> str:
        """Get the user's full name"""
        return f"{self.firstname} {self.lastname}"


@dataclass
class Group:
    """Redmine group model"""
    id: int
    name: str
    users: List[User] = None


@dataclass
class CustomField:
    """Redmine custom field model"""
    id: int
    name: str
    value: Any


@dataclass
class Version:
    """Redmine version model"""
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    status: str = "open"
    due_date: Optional[datetime] = None
    sharing: str = "none"
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None


@dataclass
class Project:
    """Redmine project model"""
    id: int
    name: str
    identifier: str
    description: Optional[str] = None
    status: int = 1
    is_public: bool = True
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    parent_id: Optional[int] = None
    custom_fields: List[CustomField] = None
    trackers: List[Tracker] = None
    versions: List[Version] = None


@dataclass
class Issue:
    """Redmine issue model"""
    id: int
    project_id: int
    tracker_id: int
    status_id: int
    priority_id: int
    subject: str
    description: Optional[str] = None
    assigned_to_id: Optional[int] = None
    category_id: Optional[int] = None
    fixed_version_id: Optional[int] = None
    parent_issue_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    done_ratio: int = 0
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    closed_on: Optional[datetime] = None
    custom_fields: List[CustomField] = None
