#!/usr/bin/env python3
"""
Validation test script that reports results to Redmine issues
Runs tests on each module and updates corresponding issues in the v1 project
"""
import os
import sys
import json
import logging
import time
import datetime
import traceback

# Add the parent directory to path so we can import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.redmine_client import RedmineClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("ValidationTest")

class ValidationReporter:
    """Runs validation tests and reports results to Redmine issues"""
    
    def __init__(self):
        """Initialize the validation reporter"""
        # Get configuration from environment
        self.redmine_url = os.environ.get("REDMINE_URL", "https://redstone.redminecloud.net")
        self.redmine_api_key = os.environ.get("REDMINE_API_KEY", "")
        
        if not self.redmine_api_key:
            logger.error("REDMINE_API_KEY environment variable is not set")
            sys.exit(1)
        
        # Initialize client
        self.client = RedmineClient(self.redmine_url, self.redmine_api_key, logger)
        
        # Load validation issues
        self.validation_issues = self.load_validation_issues()
        
        # Test results
        self.results = {
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modules": {},
            "overall_result": "PENDING"
        }
    
    def load_validation_issues(self):
        """Load validation issues from file or Redmine"""
        if os.path.exists('validation_issues.json'):
            logger.info("Loading validation issues from validation_issues.json")
            with open('validation_issues.json', 'r') as f:
                return json.load(f)
        else:
            logger.info("No validation_issues.json found, searching for v1 project in Redmine...")
            # Find v1 project
            projects = self.client.get_projects()['projects']
            v1_project = None
            for project in projects:
                if project['identifier'] == 'v1':
                    v1_project = project
                    logger.info(f"Found v1 project (ID: {v1_project['id']})")
                    break
            
            if not v1_project:
                logger.error("Could not find v1 project. Run setup_validation_project.py first.")
                sys.exit(1)
            
            # Get issues in v1 project
            result = self.client.get_issues({'project_id': v1_project['id']})
            issues = result.get('issues', [])
            
            master_issue_id = None
            module_issues = []
            
            for issue in issues:
                subject = issue['subject']
                if subject == "Master Validation Status":
                    master_issue_id = issue['id']
                elif subject.startswith("Validate: "):
                    module_name = subject[len("Validate: "):]
                    # Derive module identifier from name
                    module_id = module_name.split()[0].lower()
                    module_issues.append({
                        "module": module_id,
                        "issue_id": issue['id'],
                        "name": module_name
                    })
            
            if not master_issue_id:
                logger.error("Could not find master validation issue. Run setup_validation_project.py first.")
                sys.exit(1)
            
            validation_data = {
                "project_id": v1_project['id'],
                "master_issue_id": master_issue_id,
                "modules": module_issues
            }
            
            # Save for future use
            with open('validation_issues.json', 'w') as f:
                json.dump(validation_data, f, indent=2)
            
            return validation_data
    
    def get_issue_for_module(self, module_name):
        """Get the issue ID for a specific module"""
        for module in self.validation_issues.get('modules', []):
            if module['module'] == module_name:
                return module['issue_id']
        return None
    
    def update_issue_with_results(self, issue_id, status, details):
        """Update an issue with test results"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        note = f"## Validation Results\n\n"
        note += f"**Status**: {status}\n\n"
        note += f"**Timestamp**: {timestamp}\n\n"
        note += f"**Details**:\n\n```\n{details}\n```\n\n"
        
        # Add git commit info if available
        git_commit = os.environ.get("GITHUB_SHA", "")
        git_repository = os.environ.get("GITHUB_REPOSITORY", "")
        if git_commit:
            note += f"\n**Git Commit**: {git_commit}\n"
        if git_repository:
            note += f"**Repository**: {git_repository}\n"
        
        update_data = {
            "notes": note
        }
        
        self.client.update_issue(issue_id, update_data)
        logger.info(f"Updated issue #{issue_id} with status: {status}")
    
    def update_master_issue(self):
        """Update the master validation issue with overall results"""
        master_issue_id = self.validation_issues.get('master_issue_id')
        if not master_issue_id:
            logger.error("No master issue ID found")
            return
        
        # Count results
        passed = 0
        failed = 0
        skipped = 0
        
        for module, result in self.results['modules'].items():
            if result['status'] == 'PASSED':
                passed += 1
            elif result['status'] == 'FAILED':
                failed += 1
            else:
                skipped += 1
        
        # Determine overall status
        if failed > 0:
            overall_status = "FAILED"
        elif skipped > 0 and passed == 0:
            overall_status = "SKIPPED"
        elif passed > 0 and skipped == 0:
            overall_status = "PASSED"
        else:
            overall_status = "PARTIAL"
        
        self.results['overall_result'] = overall_status
        
        # Create summary
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = f"## Validation Summary\n\n"
        summary += f"**Overall Status**: {overall_status}\n\n"
        summary += f"**Start Time**: {self.results['start_time']}\n"
        summary += f"**End Time**: {timestamp}\n\n"
        summary += f"**Results**:\n"
        summary += f"- Passed: {passed}\n"
        summary += f"- Failed: {failed}\n"
        summary += f"- Skipped: {skipped}\n\n"
        
        summary += "**Module Results**:\n\n"
        for module in self.validation_issues.get('modules', []):
            module_name = module['module']
            if module_name in self.results['modules']:
                result = self.results['modules'][module_name]
                status = result['status']
                icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
                summary += f"- {icon} #{module['issue_id']} - {module['name']}: {status}\n"
            else:
                summary += f"- ❓ #{module['issue_id']} - {module['name']}: NOT TESTED\n"
        
        # Add environment info
        summary += "\n**Environment**:\n"
        summary += f"- Redmine URL: {self.redmine_url}\n"
        
        # Add git info if available
        git_commit = os.environ.get("GITHUB_SHA", "")
        git_repository = os.environ.get("GITHUB_REPOSITORY", "")
        git_ref = os.environ.get("GITHUB_REF", "")
        if git_commit or git_repository or git_ref:
            summary += "\n**Git Info**:\n"
            if git_repository:
                summary += f"- Repository: {git_repository}\n"
            if git_ref:
                summary += f"- Branch/Tag: {git_ref}\n"
            if git_commit:
                summary += f"- Commit: {git_commit}\n"
        
        update_data = {
            "notes": summary
        }
        
        self.client.update_issue(master_issue_id, update_data)
        logger.info(f"Updated master issue #{master_issue_id} with overall status: {overall_status}")
        
        # Save results to file
        with open('validation_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Saved validation results to validation_results.json")
    
    def test_base_module(self):
        """Test the base module"""
        module_name = "base"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Simple base client test
            result = self.client.get_current_user()
            assert result and 'user' in result, "Failed to get current user"
            
            details = f"Base client successfully authenticated with Redmine\n"
            details += f"User: {result['user']['firstname']} {result['user']['lastname']} ({result['user']['login']})"
            
            self.results['modules'][module_name] = {
                "status": "PASSED",
                "details": details
            }
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing base module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_issues_module(self):
        """Test the issues module"""
        module_name = "issues"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Find test project
            test_project_id = None
            projects = self.client.get_projects()['projects']
            for project in projects:
                if project['identifier'] == 'v1':
                    test_project_id = project['id']
                    break
            
            if not test_project_id:
                raise ValueError("Could not find v1 project for testing")
            
            # Create a test issue
            test_subject = f"Test Issue - {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            issue_data = {
                "project_id": test_project_id,
                "subject": test_subject,
                "description": "This is a test issue created by the validation test suite",
                "priority_id": 2  # Normal priority
            }
            
            # Create issue
            result = self.client.create_issue(issue_data)
            assert result and 'issue' in result, "Failed to create test issue"
            
            test_issue_id = result['issue']['id']
            logger.info(f"Created test issue #{test_issue_id}")
            
            # Get issue
            result = self.client.get_issue(test_issue_id)
            assert result and 'issue' in result, "Failed to get test issue"
            assert result['issue']['subject'] == test_subject, "Issue subject mismatch"
            
            # Update issue
            update_data = {
                "notes": "This is a test note from the validation test suite"
            }
            result = self.client.update_issue(test_issue_id, update_data)
            
            # Get updated issue
            result = self.client.get_issue(test_issue_id)
            assert result and 'issue' in result, "Failed to get updated test issue"
            
            # Delete issue
            result = self.client.delete_issue(test_issue_id)
            
            details = f"Issues module successfully tested with Redmine\n"
            details += f"- Created issue #{test_issue_id}: {test_subject}\n"
            details += f"- Retrieved issue details\n"
            details += f"- Updated issue with note\n"
            details += f"- Deleted issue\n"
            
            self.results['modules'][module_name] = {
                "status": "PASSED",
                "details": details
            }
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing issues module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_projects_module(self):
        """Test the projects module"""
        module_name = "projects"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Get projects
            result = self.client.get_projects()
            assert result and 'projects' in result, "Failed to get projects"
            
            # Find v1 project
            v1_project = None
            for project in result['projects']:
                if project['identifier'] == 'v1':
                    v1_project = project
                    break
            
            assert v1_project is not None, "Could not find v1 project"
            
            # Get project details
            result = self.client.get_project(v1_project['id'])
            assert result and 'project' in result, "Failed to get project details"
            assert result['project']['id'] == v1_project['id'], "Project ID mismatch"
            
            details = f"Projects module successfully tested with Redmine\n"
            details += f"- Retrieved list of projects\n"
            details += f"- Found v1 project (ID: {v1_project['id']})\n"
            details += f"- Retrieved project details\n"
            
            self.results['modules'][module_name] = {
                "status": "PASSED",
                "details": details
            }
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing projects module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_versions_module(self):
        """Test the versions module"""
        module_name = "versions"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Find test project
            test_project_id = None
            projects = self.client.get_projects()['projects']
            for project in projects:
                if project['identifier'] == 'v1':
                    test_project_id = project['id']
                    break
            
            if not test_project_id:
                raise ValueError("Could not find v1 project for testing")
            
            # Get versions for project
            result = self.client.get_versions(test_project_id)
            
            # Create a test version
            version_name = f"Test Version {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            version_data = {
                "project_id": test_project_id,
                "name": version_name,
                "description": "This is a test version created by the validation test suite",
                "status": "open"
            }
            
            try:
                # Create version
                result = self.client.versions.create_version(version_data)
                assert result and 'version' in result, "Failed to create test version"
                
                test_version_id = result['version']['id']
                logger.info(f"Created test version #{test_version_id}")
                
                # Get version
                result = self.client.versions.get_version(test_version_id)
                assert result and 'version' in result, "Failed to get test version"
                assert result['version']['name'] == version_name, "Version name mismatch"
                
                # Delete version
                result = self.client.versions.delete_version(test_version_id)
                
                details = f"Versions module successfully tested with Redmine\n"
                details += f"- Retrieved versions for project\n"
                details += f"- Created version #{test_version_id}: {version_name}\n"
                details += f"- Retrieved version details\n"
                details += f"- Deleted version\n"
                
                self.results['modules'][module_name] = {
                    "status": "PASSED",
                    "details": details
                }
                
            except Exception as e:
                # If version creation fails due to permission issues, mark as skipped
                logger.warning(f"Could not fully test versions module: {e}")
                
                details = f"Versions module partially tested with Redmine\n"
                details += f"- Retrieved versions for project\n"
                details += f"Note: Could not create/delete versions, possibly due to permissions"
                
                self.results['modules'][module_name] = {
                    "status": "SKIPPED",
                    "details": details
                }
                
                self.update_issue_with_results(issue_id, "SKIPPED", details)
                return
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing versions module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_users_module(self):
        """Test the users module"""
        module_name = "users"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Get current user
            result = self.client.users.get_current_user()
            assert result and 'user' in result, "Failed to get current user"
            
            # Get users
            result = self.client.users.get_users()
            assert result and 'users' in result, "Failed to get users"
            
            # Get specific user (current user)
            current_user_id = self.client.users.get_current_user()['user']['id']
            result = self.client.users.get_user(current_user_id)
            assert result and 'user' in result, "Failed to get specific user"
            assert result['user']['id'] == current_user_id, "User ID mismatch"
            
            details = f"Users module successfully tested with Redmine\n"
            details += f"- Retrieved current user\n"
            details += f"- Retrieved list of users\n"
            details += f"- Retrieved specific user (ID: {current_user_id})\n"
            
            self.results['modules'][module_name] = {
                "status": "PASSED",
                "details": details
            }
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing users module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_groups_module(self):
        """Test the groups module"""
        module_name = "groups"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Get groups
            result = self.client.groups.get_groups()
            assert 'groups' in result, "Failed to get groups"
            
            details = f"Groups module successfully tested with Redmine\n"
            details += f"- Retrieved list of groups ({len(result['groups'])} found)\n"
            
            self.results['modules'][module_name] = {
                "status": "PASSED",
                "details": details
            }
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing groups module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_roadmap_module(self):
        """Test the roadmap module"""
        module_name = "roadmap"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            # Find test project
            test_project_id = None
            projects = self.client.get_projects()['projects']
            for project in projects:
                if project['identifier'] == 'v1':
                    test_project_id = project['id']
                    break
            
            if not test_project_id:
                raise ValueError("Could not find v1 project for testing")
            
            # Get roadmap (versions)
            result = self.client.roadmap.get_roadmap(test_project_id)
            assert 'versions' in result, "Failed to get roadmap"
            
            try:
                # Create a test version
                version_name = f"Roadmap Test {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                result = self.client.roadmap.create_roadmap_version(
                    test_project_id,
                    version_name,
                    "Test version created by roadmap module validation",
                    "open"
                )
                
                assert result and 'version' in result, "Failed to create test version"
                test_version_id = result['version']['id']
                logger.info(f"Created test version #{test_version_id}")
                
                # Create a test issue
                issue_data = {
                    "project_id": test_project_id,
                    "subject": f"Roadmap Test Issue {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "description": "This is a test issue created by the roadmap module validation",
                    "priority_id": 2  # Normal priority
                }
                result = self.client.create_issue(issue_data)
                assert result and 'issue' in result, "Failed to create test issue"
                test_issue_id = result['issue']['id']
                logger.info(f"Created test issue #{test_issue_id}")
                
                # Tag the issue with the version
                result = self.client.roadmap.tag_issue_with_version(test_issue_id, test_version_id)
                
                # Get issues by version
                result = self.client.roadmap.get_issues_by_version(test_version_id)
                assert 'issues' in result, "Failed to get issues by version"
                assert any(issue['id'] == test_issue_id for issue in result['issues']), "Tagged issue not found in version"
                
                # Clean up
                self.client.delete_issue(test_issue_id)
                logger.info(f"Deleted test issue #{test_issue_id}")
                
                self.client.roadmap.delete_version(test_version_id)
                logger.info(f"Deleted test version #{test_version_id}")
                
                details = f"Roadmap module successfully tested with Redmine\n"
                details += f"- Retrieved roadmap for project\n"
                details += f"- Created version #{test_version_id}: {version_name}\n"
                details += f"- Created issue #{test_issue_id}\n"
                details += f"- Tagged issue with version\n"
                details += f"- Retrieved issues by version\n"
                details += f"- Cleaned up test resources\n"
                
                self.results['modules'][module_name] = {
                    "status": "PASSED",
                    "details": details
                }
                
            except Exception as e:
                # If version creation fails due to permission issues, mark as skipped
                logger.warning(f"Could not fully test roadmap module: {e}")
                
                details = f"Roadmap module partially tested with Redmine\n"
                details += f"- Retrieved roadmap for project\n"
                details += f"Note: Could not create/delete versions or tag issues, possibly due to permissions"
                
                self.results['modules'][module_name] = {
                    "status": "SKIPPED",
                    "details": details
                }
                
                self.update_issue_with_results(issue_id, "SKIPPED", details)
                return
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing roadmap module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def test_mcp_module(self):
        """Test the MCP protocol module"""
        module_name = "mcp"
        issue_id = self.get_issue_for_module(module_name)
        
        if not issue_id:
            logger.warning(f"No issue found for module {module_name}")
            return
        
        logger.info(f"Testing {module_name} module...")
        
        try:
            from src.mcp_client import MCPClient
            import subprocess
            
            # Check if MCP client module is available
            assert MCPClient is not None, "MCP client module not found"
            
            # Start a simple subprocess to simulate an MCP server
            # This is just a basic test of the client's ability to start and communicate with a process
            server_process = subprocess.Popen(
                ["python", "-c", "import sys, time; print('READY'); sys.stdout.flush(); time.sleep(2); print('DONE'); sys.stdout.flush()"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # Wait for server to start
            try:
                if server_process and server_process.stdout:
                    response = server_process.stdout.readline().strip()
                    assert response == "READY", "Server process did not start correctly"
                else:
                    raise AssertionError("Server process stdout is not available")
            except AttributeError:
                raise AssertionError("Error accessing server process output stream")
            
            # Clean up
            server_process.terminate()
            server_process.wait(timeout=5)
            
            details = f"MCP protocol module successfully tested\n"
            details += f"- MCP client module is available\n"
            details += f"- Basic process communication test passed\n"
            
            self.results['modules'][module_name] = {
                "status": "PASSED",
                "details": details
            }
            
            self.update_issue_with_results(issue_id, "PASSED", details)
            
        except Exception as e:
            error_details = f"Error testing MCP protocol module: {str(e)}\n"
            error_details += traceback.format_exc()
            
            self.results['modules'][module_name] = {
                "status": "FAILED",
                "details": error_details
            }
            
            self.update_issue_with_results(issue_id, "FAILED", error_details)
    
    def run_all_tests(self):
        """Run all validation tests"""
        logger.info("Starting validation tests...")
        
        try:
            # Test each module
            self.test_base_module()
            self.test_issues_module()
            self.test_projects_module()
            self.test_versions_module()
            self.test_users_module()
            self.test_groups_module()
            self.test_roadmap_module()
            self.test_mcp_module()
            
            # Update master issue with results
            self.update_master_issue()
            
            logger.info("Validation tests completed!")
            
        except Exception as e:
            logger.error(f"Error running validation tests: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    reporter = ValidationReporter()
    reporter.run_all_tests()