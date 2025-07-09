"""
Unit tests for WikiClient
"""

import unittest
from unittest.mock import MagicMock, patch
from src.wiki.client import WikiClient

class TestWikiClient(unittest.TestCase):
    """Test cases for WikiClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://redmine.example.com"
        self.api_key = "test_api_key"
        self.client = WikiClient(self.base_url, self.api_key)
        self.project_id = "test-project"
        self.page_name = "TestPage"
        
        # Mock the make_request method
        self.client.make_request = MagicMock()
    
    def test_list_wiki_pages_success(self):
        """Test successful listing of wiki pages"""
        # Mock response
        mock_response = {
            'wiki_pages': [
                {'title': 'Page1'},
                {'title': 'Page2'}
            ]
        }
        self.client.make_request.return_value = mock_response
        
        # Call the method
        result = self.client.list_wiki_pages(self.project_id)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(len(result['pages']), 2)
        self.assertEqual(result['pages'][0]['title'], 'Page1')
        self.client.make_request.assert_called_once_with(
            'GET', f'/projects/{self.project_id}/wiki/index.json'
        )
    
    def test_list_wiki_pages_error(self):
        """Test error handling in list_wiki_pages"""
        # Mock error response
        error_msg = "API error"
        self.client.make_request.return_value = {'error': error_msg}
        
        # Call the method
        result = self.client.list_wiki_pages(self.project_id)
        
        # Assertions
        self.assertEqual(result, {'error': error_msg})
    
    def test_get_wiki_page_success(self):
        """Test successful retrieval of a wiki page"""
        # Mock response
        mock_page = {
            'title': self.page_name,
            'text': 'Test content',
            'version': 1
        }
        self.client.make_request.return_value = {'wiki_page': mock_page}
        
        # Call the method
        result = self.client.get_wiki_page(self.project_id, self.page_name)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['page']['title'], self.page_name)
        self.client.make_request.assert_called_once_with(
            'GET', f'/projects/{self.project_id}/wiki/{self.page_name}.json',
            params={}
        )
    
    def test_get_wiki_page_with_version(self):
        """Test retrieving a specific version of a wiki page"""
        version = 2
        
        # Call the method
        self.client.get_wiki_page(self.project_id, self.page_name, version=version)
        
        # Assertions
        self.client.make_request.assert_called_once_with(
            'GET', f'/projects/{self.project_id}/wiki/{self.page_name}.json',
            params={'version': version}
        )
    
    def test_create_wiki_page_success(self):
        """Test successful creation of a wiki page using POST method"""
        # Mock response
        mock_response = {
            'wiki_page': {
                'title': 'NewPage',
                'text': 'Test content',
                'version': 1,
                'created_on': '2025-01-01T00:00:00Z',
                'updated_on': '2025-01-01T00:00:00Z'
            }
        }
        self.client.make_request.return_value = mock_response
        
        # Call the method
        result = self.client.create_wiki_page(
            self.project_id, 'NewPage', 'Test content',
            parent_title='ParentPage', comments='Initial version'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['page']['title'], 'NewPage')
        self.assertEqual(result['method_used'], 'POST')
        self.client.make_request.assert_called_once()
        
        # Check the request parameters
        args, kwargs = self.client.make_request.call_args
        self.assertEqual(args[0], 'POST')
        self.assertEqual(args[1], f'/projects/{self.project_id}/wiki.json')
        self.assertEqual(kwargs['data']['wiki_page']['title'], 'NewPage')
        self.assertEqual(kwargs['data']['wiki_page']['text'], 'Test content')
        self.assertEqual(kwargs['data']['wiki_page']['parent_title'], 'ParentPage')
        self.assertEqual(kwargs['data']['wiki_page']['comments'], 'Initial version')
    
    def test_create_wiki_page_post_failure_put_fallback(self):
        """Test fallback to PUT method when POST fails with an error response"""
        # Configure the mock to return different responses for POST and PUT
        # First POST fails with an error, then PUT succeeds
        self.client.make_request.side_effect = [
            {'error': 'Method not allowed'},  # POST response (error)
            {                                 # PUT response (success)
                'wiki_page': {
                    'title': 'NewPage',
                    'version': 1,
                    'created_on': '2025-01-01T00:00:00Z'
                }
            }
        ]
        
        # Call the method
        result = self.client.create_wiki_page(
            self.project_id, 'NewPage', 'Test content'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['method_used'], 'PUT')
        self.assertEqual(result['page']['title'], 'NewPage')
        self.assertEqual(self.client.make_request.call_count, 2)
        
        # Check both API calls
        post_call = self.client.make_request.call_args_list[0]
        put_call = self.client.make_request.call_args_list[1]
        
        self.assertEqual(post_call[0][0], 'POST')
        self.assertEqual(post_call[0][1], f'/projects/{self.project_id}/wiki.json')
        
        self.assertEqual(put_call[0][0], 'PUT')
        self.assertEqual(put_call[0][1], f'/projects/{self.project_id}/wiki/NewPage.json')

    def test_create_wiki_page_post_exception_put_fallback(self):
        """Test fallback to PUT method when POST raises an exception"""
        # Configure the mock to raise an exception on first call (POST)
        # and return success on second call (PUT)
        def side_effect(*args, **kwargs):
            if args[0] == 'POST':
                raise ConnectionError("Connection error during POST")
            return {
                'wiki_page': {
                    'title': 'NewPage',
                    'version': 1
                }
            }
            
        self.client.make_request.side_effect = side_effect
        
        # Call the method
        result = self.client.create_wiki_page(
            self.project_id, 'NewPage', 'Test content'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['method_used'], 'PUT')
        self.assertEqual(self.client.make_request.call_count, 2)

    def test_create_wiki_page_minimal_required(self):
        """Test creating a wiki page with only required fields"""
        # Mock response with empty body (some Redmine versions do this on success)
        self.client.make_request.return_value = {}
        
        # Call the method
        result = self.client.create_wiki_page(
            self.project_id, 'MinimalPage', 'Content'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['page']['title'], 'MinimalPage')
        self.assertEqual(result['method_used'], 'POST')
        self.client.make_request.assert_called_once()
    
    def test_create_wiki_page_validation_error(self):
        """Test validation errors in create_wiki_page"""
        # Test missing title
        result = self.client.create_wiki_page(self.project_id, '', 'Content')
        self.assertIn('error', result)
        self.assertIn('VALIDATION_ERROR', str(result))
        
        # Test missing text
        result = self.client.create_wiki_page(self.project_id, 'Title', '')
        self.assertIn('error', result)
        self.assertIn('VALIDATION_ERROR', str(result))
        
        # Test invalid project_id
        result = self.client.create_wiki_page(None, 'Title', 'Content')
        self.assertIn('error', result)
        self.assertIn('VALIDATION_ERROR', str(result))
    
    def test_create_wiki_page_api_error(self):
        """Test API error handling in create_wiki_page"""
        # Mock error response for both POST and PUT attempts
        error_msg = "Permission denied"
        self.client.make_request.return_value = {'error': error_msg}
        
        # Call the method
        result = self.client.create_wiki_page(
            self.project_id, 'NewPage', 'Content'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertIn(error_msg, result['error'])
        
        # Should make two calls - first POST, then PUT
        self.assertEqual(self.client.make_request.call_count, 2)
        
        # Verify both calls
        post_call = self.client.make_request.call_args_list[0]
        put_call = self.client.make_request.call_args_list[1]
        
        self.assertEqual(post_call[0][0], 'POST')
        self.assertEqual(post_call[0][1], f'/projects/{self.project_id}/wiki.json')
        
        self.assertEqual(put_call[0][0], 'PUT')
        self.assertEqual(put_call[0][1], f'/projects/{self.project_id}/wiki/NewPage.json')
    
    @patch('src.wiki.client.WikiClient.validate_input')
    def test_create_wiki_page_validation_failure(self, mock_validate):
        """Test validation failure in create_wiki_page"""
        # Mock validation error
        mock_validate.return_value = {
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'Validation failed',
            'details': {'field': 'title', 'error': 'Required field'}
        }
        
        # Call the method
        result = self.client.create_wiki_page(
            self.project_id, 'Invalid', 'Content'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'VALIDATION_ERROR')
        mock_validate.assert_called_once()
    
    # Placeholder for update_wiki_page test
    def test_update_wiki_page_exception_handling(self):
        """Test exception handling in update_wiki_page"""
        # Force an exception by making make_request raise an exception
        self.client.make_request.side_effect = Exception("Connection failed")
        
        # Call the method
        result = self.client.update_wiki_page(
            self.project_id, self.page_name, 'Content'
        )
        
        # Assertions
        self.assertTrue('error' in result, "Response should contain error field")
        self.assertEqual(result.get('error_code', ''), 'UNEXPECTED_ERROR', "Error code should be UNEXPECTED_ERROR")
        self.assertIn('Connection failed', str(result.get('details', {}).get('error_message', '')), "Error message should contain the exception message")

    def test_update_wiki_page_success(self):
        """Test successful update of a wiki page"""
        # Mock response
        mock_page = {
            'title': self.page_name,
            'text': 'Updated content',
            'version': 2
        }
        self.client.make_request.return_value = {'wiki_page': mock_page}
        
        # Call the method
        result = self.client.update_wiki_page(
            self.project_id, self.page_name, 'Updated content',
            comments='Update comment'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['page']['title'], self.page_name)
        self.assertEqual(result['page']['version'], 2)
        self.client.make_request.assert_called_once()
        
        # Check the request parameters
        args, kwargs = self.client.make_request.call_args
        self.assertEqual(args[0], 'PUT')
        self.assertEqual(args[1], f'/projects/{self.project_id}/wiki/{self.page_name}.json')
        self.assertEqual(kwargs['data']['wiki_page']['text'], 'Updated content')
        self.assertEqual(kwargs['data']['wiki_page']['comments'], 'Update comment')
    
    def test_update_wiki_page_empty_response(self):
        """Test wiki page update with empty response (204 No Content)"""
        # Mock empty response (some Redmine versions return empty on success)
        self.client.make_request.return_value = {}
        
        # Call the method
        result = self.client.update_wiki_page(
            self.project_id, self.page_name, 'New content'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertIn('message', result)
        self.assertIn(self.page_name, result['message'])
    
    def test_update_wiki_page_validation_error(self):
        """Test validation errors in update_wiki_page"""
        # Test empty page name
        result = self.client.update_wiki_page(self.project_id, '', 'Content')
        self.assertIn('error', result)
        self.assertIn('VALIDATION_ERROR', str(result))
        
        # Test empty text
        result = self.client.update_wiki_page(self.project_id, self.page_name, '')
        self.assertIn('error', result)
        self.assertIn('VALIDATION_ERROR', str(result))
        
        # Test None project_id
        result = self.client.update_wiki_page(None, self.page_name, 'Content')
        self.assertIn('error', result)
        self.assertIn('VALIDATION_ERROR', str(result))
    
    def test_update_wiki_page_error_response(self):
        """Test error handling in update_wiki_page"""
        # Mock error response
        error_msg = "API error during update"
        self.client.make_request.return_value = {'error': error_msg}
        
        # Call the method
        result = self.client.update_wiki_page(
            self.project_id, self.page_name, 'Content'
        )
        
        # Assertions
        self.assertFalse(result.get('success', False))
        self.assertEqual(result, {'success': False, 'error': f"Failed to update wiki page: {error_msg}"})

    def test_delete_wiki_page_success(self):
        """Test successful wiki page deletion"""
        # Setup the mock to return empty response (common for DELETE operations)
        self.client.make_request.return_value = {}
        
        # Call the method
        result = self.client.delete_wiki_page(self.project_id, self.page_name)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertIn(f"Wiki page '{self.page_name}' deleted successfully", result['message'])
        
        # Verify request was made correctly
        self.client.make_request.assert_called_once_with(
            'DELETE', 
            f"/projects/{self.project_id}/wiki/{self.page_name}.json"
        )
    
    def test_delete_wiki_page_validation_errors(self):
        """Test validation errors in delete_wiki_page"""
        # Test with empty project_id
        result = self.client.delete_wiki_page('', self.page_name)
        self.assertTrue('error' in result)
        self.assertEqual(result.get('error_code'), 'VALIDATION_ERROR')
        
        # Test with empty page_name
        result = self.client.delete_wiki_page(self.project_id, '')
        self.assertTrue('error' in result)
        self.assertEqual(result.get('error_code'), 'VALIDATION_ERROR')
        
        # Reset call count
        self.client.make_request.reset_mock()
        
        # Verify no API calls were made due to validation errors
        self.client.make_request.assert_not_called()
    
    def test_delete_wiki_page_error_response(self):
        """Test handling of error responses from the API"""
        # Setup the mock to return an error
        error_response = {'error': 'Page not found'}
        self.client.make_request.return_value = error_response
        
        # Call the method
        result = self.client.delete_wiki_page(self.project_id, self.page_name)
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertIn('Failed to delete wiki page', result['error'])
    
    def test_delete_wiki_page_exception_handling(self):
        """Test exception handling in delete_wiki_page"""
        # Force an exception by making make_request raise an exception
        self.client.make_request.side_effect = Exception("Connection failed")
        
        # Call the method
        result = self.client.delete_wiki_page(self.project_id, self.page_name)
        
        # Assertions
        self.assertTrue('error' in result, "Response should contain error field")
        self.assertEqual(result.get('error_code', ''), 'UNEXPECTED_ERROR', "Error code should be UNEXPECTED_ERROR")
        self.assertIn('Connection failed', str(result.get('details', {}).get('error_message', '')), "Error message should contain the exception message")


if __name__ == '__main__':
    unittest.main()
