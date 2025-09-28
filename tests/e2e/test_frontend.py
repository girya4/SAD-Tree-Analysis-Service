"""
End-to-end tests for frontend functionality using Playwright.
"""
import pytest
from playwright.sync_api import sync_playwright, Page, Browser
import tempfile
import os
from PIL import Image
import io


@pytest.fixture(scope="session")
def browser():
    """Create browser instance for E2E tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    """Create new page for each test."""
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def sample_image_file():
    """Create a sample image file for testing."""
    img = Image.new('RGB', (200, 200), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestFrontendBasic:
    """Test basic frontend functionality."""
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_page_loads(self, page: Page):
        """Test that the main page loads correctly."""
        page.goto("http://localhost:8000")
        
        # Check page title
        assert page.title() == "Tree Analysis Service"
        
        # Check main elements are present
        assert page.locator("h1").text_content() == "Tree Analysis Service"
        assert page.locator("#file-input").is_visible()
        assert page.locator("#upload-btn").is_visible()
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_file_input_accepts_images(self, page: Page):
        """Test that file input accepts image files."""
        page.goto("http://localhost:8000")
        
        file_input = page.locator("#file-input")
        assert file_input.get_attribute("accept") == "image/*"
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_upload_button_disabled_initially(self, page: Page):
        """Test that upload button is disabled initially."""
        page.goto("http://localhost:8000")
        
        upload_btn = page.locator("#upload-btn")
        assert upload_btn.is_disabled()


class TestFileUpload:
    """Test file upload functionality."""
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_file_selection_enables_upload(self, page: Page, sample_image_file):
        """Test that selecting a file enables the upload button."""
        page.goto("http://localhost:8000")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(sample_image_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Select file
            page.locator("#file-input").set_input_files(tmp_file_path)
            
            # Check that upload button is now enabled
            upload_btn = page.locator("#upload-btn")
            assert not upload_btn.is_disabled()
            
            # Check that file name is displayed
            file_name = page.locator("#file-name")
            assert file_name.is_visible()
            assert "test" in file_name.text_content().lower()
            
        finally:
            os.unlink(tmp_file_path)
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_file_upload_success(self, page: Page, sample_image_file):
        """Test successful file upload."""
        page.goto("http://localhost:8000")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(sample_image_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Select and upload file
            page.locator("#file-input").set_input_files(tmp_file_path)
            page.locator("#upload-btn").click()
            
            # Wait for upload to complete
            page.wait_for_selector("#upload-status", timeout=10000)
            
            # Check upload status
            upload_status = page.locator("#upload-status")
            assert upload_status.is_visible()
            
        finally:
            os.unlink(tmp_file_path)
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_file_upload_invalid_format(self, page: Page):
        """Test file upload with invalid format."""
        page.goto("http://localhost:8000")
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"This is not an image")
            tmp_file_path = tmp_file.name
        
        try:
            # Select invalid file
            page.locator("#file-input").set_input_files(tmp_file_path)
            page.locator("#upload-btn").click()
            
            # Check for error message
            page.wait_for_selector(".error-message", timeout=5000)
            error_msg = page.locator(".error-message")
            assert error_msg.is_visible()
            
        finally:
            os.unlink(tmp_file_path)


class TestTaskManagement:
    """Test task management functionality."""
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_task_list_display(self, page: Page):
        """Test that task list is displayed."""
        page.goto("http://localhost:8000")
        
        # Check that task list container exists
        task_list = page.locator("#task-list")
        assert task_list.is_visible()
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_task_status_updates(self, page: Page, sample_image_file):
        """Test that task status updates are displayed."""
        page.goto("http://localhost:8000")
        
        # Create and upload file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(sample_image_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            page.locator("#file-input").set_input_files(tmp_file_path)
            page.locator("#upload-btn").click()
            
            # Wait for task to appear in list
            page.wait_for_selector(".task-item", timeout=10000)
            
            # Check task status
            task_item = page.locator(".task-item").first
            assert task_item.is_visible()
            
            # Check status indicator
            status_indicator = task_item.locator(".status-indicator")
            assert status_indicator.is_visible()
            
        finally:
            os.unlink(tmp_file_path)
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_task_details_modal(self, page: Page, sample_image_file):
        """Test task details modal functionality."""
        page.goto("http://localhost:8000")
        
        # Create and upload file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(sample_image_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            page.locator("#file-input").set_input_files(tmp_file_path)
            page.locator("#upload-btn").click()
            
            # Wait for task to appear
            page.wait_for_selector(".task-item", timeout=10000)
            
            # Click on task to open details
            task_item = page.locator(".task-item").first
            task_item.click()
            
            # Check that modal opens
            modal = page.locator("#task-details-modal")
            assert modal.is_visible()
            
            # Check modal content
            assert page.locator("#modal-title").is_visible()
            assert page.locator("#modal-content").is_visible()
            
            # Close modal
            close_btn = page.locator("#close-modal")
            close_btn.click()
            
            # Check that modal is closed
            assert not modal.is_visible()
            
        finally:
            os.unlink(tmp_file_path)


class TestResponsiveDesign:
    """Test responsive design functionality."""
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_mobile_viewport(self, page: Page):
        """Test that page works on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:8000")
        
        # Check that main elements are still visible
        assert page.locator("h1").is_visible()
        assert page.locator("#file-input").is_visible()
        assert page.locator("#upload-btn").is_visible()
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_tablet_viewport(self, page: Page):
        """Test that page works on tablet viewport."""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("http://localhost:8000")
        
        # Check that layout adapts to tablet size
        assert page.locator("h1").is_visible()
        assert page.locator("#file-input").is_visible()
        assert page.locator("#upload-btn").is_visible()


class TestErrorHandling:
    """Test error handling in frontend."""
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_network_error_handling(self, page: Page):
        """Test handling of network errors."""
        # Mock network failure
        page.route("**/api/tasks", lambda route: route.abort())
        
        page.goto("http://localhost:8000")
        
        # Try to upload file (should fail)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_file, format='JPEG')
            tmp_file_path = tmp_file.name
        
        try:
            page.locator("#file-input").set_input_files(tmp_file_path)
            page.locator("#upload-btn").click()
            
            # Check for error message
            page.wait_for_selector(".error-message", timeout=5000)
            error_msg = page.locator(".error-message")
            assert error_msg.is_visible()
            
        finally:
            os.unlink(tmp_file_path)
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    def test_large_file_handling(self, page: Page):
        """Test handling of large files."""
        page.goto("http://localhost:8000")
        
        # Create large file (simulate)
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(large_content)
            tmp_file_path = tmp_file.name
        
        try:
            page.locator("#file-input").set_input_files(tmp_file_path)
            page.locator("#upload-btn").click()
            
            # Check for file size error
            page.wait_for_selector(".error-message", timeout=5000)
            error_msg = page.locator(".error-message")
            assert error_msg.is_visible()
            assert "too large" in error_msg.text_content().lower()
            
        finally:
            os.unlink(tmp_file_path)
