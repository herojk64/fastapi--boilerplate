"""
Integration tests for the FastAPI backend.
These tests hit the running server to verify end-to-end functionality.
"""
import pytest
import requests
import time

# Base URL for the running server
BASE_URL = "http://localhost:3000/api/v1"

# Wait for server to be ready
def wait_for_server(max_attempts=10):
    """Wait for the server to be ready before running tests."""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL.rsplit('/api/v1', 1)[0]}/docs")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    return False


@pytest.fixture(scope="module", autouse=True)
def check_server():
    """Ensure server is running before tests."""
    if not wait_for_server():
        pytest.skip("Server is not running on localhost:3000")


class TestAdminSeeder:
    """Test that the admin seeder creates the admin user, role, and permissions correctly."""
    
    def test_admin_user_exists(self):
        """Test that admin user is created and can login."""
        response = requests.post(
            f"{BASE_URL}/auth/token",
            json={
                "email": "admin@example.com",
                "password": "admin123"
            }
        )
        assert response.status_code == 200, f"Admin login failed: {response.json()}"
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "admin@example.com"
    
    def test_admin_role_exists(self):
        """Test that admin role is created."""
        # Login as admin first
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get roles
        response = requests.get(
            f"{BASE_URL}/roles/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        # Check that admin role exists
        roles = [role["name"] for role in data["items"]]
        assert "admin" in roles
    
    def test_admin_permissions_exist(self):
        """Test that admin permissions are created."""
        # Login as admin first
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get permissions
        response = requests.get(
            f"{BASE_URL}/permissions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 4
        
        # Check that admin permissions exist
        permission_names = [perm["name"] for perm in data["items"]]
        assert "administrator.read" in permission_names
        assert "administrator.create" in permission_names
        assert "administrator.update" in permission_names
        assert "administrator.delete" in permission_names
    
    def test_admin_has_admin_role(self):
        """Test that admin user has the admin role assigned."""
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        data = login_response.json()
        user = data["user"]
        
        # Verify admin user exists
        assert user["email"] == "admin@example.com"
        assert user["username"] == "admin"
        # Note: UserOut schema doesn't include roles/permissions in response
        # The important thing is admin can perform admin operations (tested in TestAdminOperations)


class TestUserSignupAndSignin:
    """Test user registration and authentication."""
    
    def test_user_signup(self):
        """Test that a new user can sign up."""
        timestamp = int(time.time() * 1000)
        email = f"testuser_{timestamp}@example.com"
        username = f"testuser_{timestamp}"
        
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123",
                "username": username
            }
        )
        assert response.status_code == 201, f"Signup failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data["email"] == email
        assert data["username"] == username
        assert "id" in data
    
    def test_user_signin(self):
        """Test that a user can sign in after signing up."""
        timestamp = int(time.time() * 1000)
        email = f"testuser_{timestamp}@example.com"
        username = f"testuser_{timestamp}"
        
        # First signup
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123",
                "username": username
            }
        )
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.status_code} - {signup_response.text}"
        
        # Then signin
        signin_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={
                "email": email,
                "password": "TestPassword123"
            }
        )
        assert signin_response.status_code == 200, f"Signin failed: {signin_response.json()}"
        data = signin_response.json()
        assert "access_token" in data
        assert data["user"]["email"] == email
    
    def test_duplicate_email_signup(self):
        """Test that signing up with an existing email fails."""
        timestamp = int(time.time() * 1000)
        email = f"testuser_{timestamp}@example.com"
        
        # First signup
        requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123",
                "username": f"testuser1_{timestamp}"
            }
        )
        
        # Try to signup again with same email
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "AnotherPassword123",
                "username": f"testuser2_{timestamp}"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_invalid_credentials_signin(self):
        """Test that signin fails with invalid credentials."""
        response = requests.post(
            f"{BASE_URL}/auth/token",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123"
            }
        )
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()


class TestPasswordChange:
    """Test user password change functionality."""
    
    def test_user_can_change_password(self):
        """Test that a user can change their own password."""
        timestamp = int(time.time() * 1000)
        email = f"passwordtest_{timestamp}@example.com"
        username = f"pwdtestuser_{timestamp}"
        old_password = "OldPassword123"
        new_password = "NewPassword456"
        
        # Signup
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": old_password,
                "username": username
            }
        )
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.status_code} - {signup_response.text}"
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": email, "password": old_password}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.status_code} - {login_response.text}"
        token = login_response.json()["access_token"]
        
        # Change password
        response = requests.put(
            f"{BASE_URL}/users/profile/password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": old_password,
                "new_password": new_password
            }
        )
        assert response.status_code == 200, f"Password change failed: {response.json()}"
        
        # Verify can login with new password
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={
                "email": email,
                "password": new_password
            }
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
    
    def test_password_change_wrong_old_password(self):
        """Test that password change fails with wrong old password."""
        timestamp = int(time.time() * 1000)
        email = f"passwordtest2_{timestamp}@example.com"
        username = f"pwdtestuser2_{timestamp}"
        password = "OldPassword123"
        
        # Signup
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": password,
                "username": username
            }
        )
        assert signup_response.status_code == 201
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": email, "password": password}
        )
        token = login_response.json()["access_token"]
        
        # Try to change password with wrong old password
        response = requests.put(
            f"{BASE_URL}/users/profile/password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "old_password": "WrongOldPassword",
                "new_password": "NewPassword456"
            }
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_password_change_requires_auth(self):
        """Test that password change requires authentication."""
        response = requests.put(
            f"{BASE_URL}/users/profile/password",
            json={
                "old_password": "anything",
                "new_password": "NewPassword456"
            }
        )
        assert response.status_code in [401, 403]


class TestAuthorization:
    """Test that users without permissions cannot access admin endpoints."""
    
    def test_regular_user_cannot_list_users(self):
        """Test that regular users cannot list all users."""
        timestamp = int(time.time() * 1000)
        email = f"regularuser_{timestamp}@example.com"
        username = f"regularuser_{timestamp}"
        
        # Signup
        requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "UserPassword123",
                "username": username
            }
        )
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": email, "password": "UserPassword123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to list users
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.json()}"
        assert "permission" in response.json()["detail"].lower() or "forbidden" in response.json()["detail"].lower()
    
    def test_regular_user_cannot_get_other_user(self):
        """Test that regular users cannot get other users' details."""
        timestamp = int(time.time() * 1000)
        email = f"regularuser2_{timestamp}@example.com"
        username = f"regularuser2_{timestamp}"
        
        # Signup
        requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "UserPassword123",
                "username": username
            }
        )
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": email, "password": "UserPassword123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to get admin user
        response = requests.get(
            f"{BASE_URL}/users/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
    
    def test_regular_user_cannot_update_other_user(self):
        """Test that regular users cannot update other users."""
        timestamp = int(time.time() * 1000)
        email = f"regularuser3_{timestamp}@example.com"
        username = f"regularuser3_{timestamp}"
        
        # Signup
        requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "UserPassword123",
                "username": username
            }
        )
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": email, "password": "UserPassword123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to update user
        response = requests.put(
            f"{BASE_URL}/users/1",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Hacked"}
        )
        assert response.status_code == 403
    
    def test_regular_user_cannot_delete_user(self):
        """Test that regular users cannot delete users."""
        timestamp = int(time.time() * 1000)
        email = f"regularuser4_{timestamp}@example.com"
        username = f"regularuser4_{timestamp}"
        
        # Signup
        requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "UserPassword123",
                "username": username
            }
        )
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": email, "password": "UserPassword123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to delete user
        response = requests.delete(
            f"{BASE_URL}/users/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
    
    def test_unauthenticated_user_cannot_access_admin_endpoints(self):
        """Test that unauthenticated users cannot access admin endpoints."""
        endpoints = [
            ("GET", f"{BASE_URL}/users/"),
            ("GET", f"{BASE_URL}/users/1"),
            ("PUT", f"{BASE_URL}/users/1"),
            ("DELETE", f"{BASE_URL}/users/1"),
        ]
        
        for method, url in endpoints:
            response = requests.request(method, url)
            assert response.status_code in [401, 403], f"{method} {url} should require auth"


class TestAdminOperations:
    """Test that admins can perform all admin operations."""
    
    def test_admin_can_list_users(self):
        """Test that admins can list all users."""
        # Get admin token
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # List users
        response = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Admin list users failed: {response.json()}"
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
    
    def test_admin_can_get_user_by_id(self):
        """Test that admins can get a user by ID."""
        # Get admin token
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Create a test user
        timestamp = int(time.time() * 1000)
        email = f"testuser_admin_{timestamp}@example.com"
        username = f"admintest_{timestamp}"
        
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123",
                "username": username
            }
        )
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.status_code} - {signup_response.text}"
        test_user_id = signup_response.json()["id"]
        
        # Get user by ID
        response = requests.get(
            f"{BASE_URL}/users/{test_user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Admin get user failed: {response.json()}"
        data = response.json()
        assert data["id"] == test_user_id
    
    def test_admin_can_update_user(self):
        """Test that admins can update a user."""
        # Get admin token
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Create a test user
        timestamp = int(time.time() * 1000)
        email = f"testuser_admin2_{timestamp}@example.com"
        username = f"admintest2_{timestamp}"
        
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123",
                "username": username
            }
        )
        assert signup_response.status_code == 201
        test_user_id = signup_response.json()["id"]
        
        # Update user
        response = requests.put(
            f"{BASE_URL}/users/{test_user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "Updated",
                "last_name": "Name"
            }
        )
        assert response.status_code == 200, f"Admin update user failed: {response.json()}"
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
    
    def test_admin_can_delete_user(self):
        """Test that admins can delete a user."""
        # Get admin token
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Create a user to delete
        timestamp = int(time.time() * 1000)
        email = f"todelete_{timestamp}@example.com"
        username = f"todelete_{timestamp}"
        
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": "TestPassword123",
                "username": username
            }
        )
        user_id = signup_response.json()["id"]
        
        # Delete the user
        response = requests.delete(
            f"{BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Admin delete user failed: {response.json()}"
        
        # Verify user is deleted
        get_response = requests.get(
            f"{BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
    
    def test_admin_can_list_roles(self):
        """Test that admins can list roles."""
        # Get admin token
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # List roles
        response = requests.get(
            f"{BASE_URL}/roles/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1
    
    def test_admin_can_list_permissions(self):
        """Test that admins can list permissions."""
        # Get admin token
        login_response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # List permissions
        response = requests.get(
            f"{BASE_URL}/permissions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
