# Install httpx: pip install httpx
import httpx # Replaces requests
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Union, Any, Tuple, TypeVar, Generic, Set
from enum import Enum
# Note: httpx uses different exception types
from httpx import RequestError, TimeoutException, ConnectError, HTTPStatusError
from io import IOBase
import os
from urllib.parse import urljoin

# --- Dataclasses (User, AuthToken, Post, Comment, Category, Tag, Stats, UserRole) ---
# (Keep the dataclasses as they were previously defined)
@dataclass
class User:
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    is_staff: bool = False
    is_active: bool = True
    date_joined: Optional[datetime] = None

@dataclass
class AuthToken:
    token: str
    user_id: int
    username: str
    role: str

@dataclass
class Post:
    id: int
    title: str
    slug: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    category: Optional[str]
    comment_count: int
    featured_image_url: Optional[str]
    is_published: bool
    featured: bool
    view_count: int

@dataclass
class Comment:
    id: int
    post: int
    author: str
    author_avatar: Optional[str]
    content: str
    created_at: datetime
    parent: Optional[int] = None
    replies: List['Comment'] = field(default_factory=list)

@dataclass
class Category:
    id: int
    name: str
    slug: str

@dataclass
class Tag:
    id: int
    name: str
    slug: str
    post_count: int

@dataclass
class Stats:
    total_posts: int
    published_posts: int
    total_comments: int
    total_categories: int
    total_tags: int

class UserRole(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    READER = "reader"
# --- End Dataclasses ---

class BlogApi:

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        """Initializes the API client with httpx.Client for persistent sessions."""
        self.base_url = base_url if base_url.endswith('/') else f"{base_url}/"
        self.api_url = self.base_url
        # Use httpx.Client for persistent headers/connection pooling
        self.client = httpx.Client(base_url=self.api_url, timeout=15.0, follow_redirects=True)
        # Optional: Store user info locally after login
        self._user_id: Optional[int] = None
        self._username: Optional[str] = None
        self._role: Optional[str] = None
        self._instance_id = os.urandom(4).hex() # For debugging instance issues
        print(f"DEBUG: BlogApi instance CREATED with ID: {self._instance_id} using httpx")

    def _make_url(self, endpoint: str) -> str:
        """Constructs the full API URL (relative to base_url for httpx.Client)."""
        # httpx.Client handles joining base_url, so just return relative path
        return endpoint.lstrip('/')

    def _process_response(self, response: httpx.Response) -> Dict:
        """Parses the httpx.Response into a standard dictionary format."""
        try:
            # Raise exceptions for 4xx/5xx errors immediately
            # response.raise_for_status() # We'll handle status codes manually below

            if response.status_code == 204:
                return {"success": True, "status_code": response.status_code, "message": "No Content", "data": None}

            data = None
            is_json = 'application/json' in response.headers.get('content-type', '')
            if response.content and is_json:
                 try:
                     data = response.json()
                 except json.JSONDecodeError:
                     return {"success": False, "status_code": response.status_code, "error": f"Invalid JSON response body (Status {response.status_code})", "data": None}
            elif not is_json and response.text:
                # Response has text content but isn't JSON
                pass # data remains None

            success = 200 <= response.status_code < 300
            result = {"success": success, "status_code": response.status_code, "data": data}

            if not success:
                error_detail = f"Error {response.status_code}: {response.reason_phrase}"
                if data and isinstance(data, dict):
                    detail = data.get('detail', data.get('error', data.get('non_field_errors', data)))
                    if isinstance(detail, list): detail = "; ".join(map(str, detail))
                    elif isinstance(detail, dict): detail = json.dumps(detail)
                    if detail: error_detail = str(detail)
                elif data and isinstance(data, str):
                    error_detail = data
                elif data is None and response.text:
                     error_detail = f"Error {response.status_code}: {response.reason_phrase}. Server response: {response.text[:200]}..."
                result["error"] = error_detail

            return result
        except HTTPStatusError as e: # Catch errors raised by raise_for_status() if used
            # This block might be less necessary if we handle status codes manually
            error_body = e.response.text[:200] if e.response else "N/A"
            return {"success": False, "status_code": e.response.status_code, "error": f"HTTP Error {e.response.status_code}: {e.response.reason_phrase}. Body: {error_body}...", "data": None}
        except Exception as e:
            status = response.status_code if 'response' in locals() else 0
            return {"success": False, "status_code": status, "error": f"Critical error processing response: {str(e)}", "data": None}

    def _handle_request(self, method: str, endpoint: str,
                        params: Optional[Dict] = None,
                        data: Optional[Dict] = None,
                        files: Optional[Dict] = None) -> Dict:
        """Handles sending the request using the internal httpx client."""
        url = self._make_url(endpoint)
        # --- Debugging Auth Header ---
        current_auth_header = self.client.headers.get("Authorization")
        print(f"DEBUG: Instance {self._instance_id} sending {method.upper()} to {url}. Auth Header Present: {current_auth_header is not None}")
        # --- End Debugging ---

        # Prepare data/json/files payload
        json_payload = None
        data_payload = None
        files_payload = None

        if data is not None and not files:
            json_payload = data # Send as JSON if no files
        elif data is not None and files:
             # Send as form data if files are present
             data_payload = {k: (json.dumps(v) if isinstance(v, (list, dict)) else str(v)) for k, v in data.items()}
             files_payload = files
        elif files:
            files_payload = files # Send only files if no data

        try:
            response = self.client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_payload,
                data=data_payload,
                files=files_payload
            )

            processed_response = self._process_response(response)

            # Clear potentially invalid token on 401
            if processed_response.get('status_code') == 401:
                 print(f"WARNING: Instance {self._instance_id} received 401 Unauthorized for {method.upper()} {url}. Clearing session auth header.")
                 self.clear_auth()

            return processed_response

        # Handle specific httpx exceptions
        except ConnectError: return {"success": False, "error": "Connection error.", "data": None}
        except TimeoutException: return {"success": False, "error": "Request timed out.", "data": None}
        except RequestError as e: return {"success": False, "error": f"Request error: {str(e)}", "data": None}
        except Exception as e: return {"success": False, "error": f"Unexpected error during request: {str(e)}", "data": None}

    # --- Authentication Methods ---
    def register(self, username: str, email: str, password: str) -> Dict:
        """Registers a new user."""
        data = {"username": username, "email": email, "password": password}
        # Use a temporary httpx client for registration to avoid session issues
        try:
            with httpx.Client(base_url=self.api_url, timeout=15.0) as temp_client:
                response = temp_client.post("register/", json=data)
                return self._process_response(response)
        except Exception as e: return {"success": False, "error": f"Registration request error: {str(e)}", "data": None}

    def login(self, username: str, password: str) -> Dict:
        """Logs in a user and sets the token on the internal httpx client."""
        data = {"username": username, "password": password}
        print(f"DEBUG: Instance {self._instance_id} attempting login for '{username}'. Clearing previous auth state.")
        self.clear_auth()
        # Use a temporary httpx client for login itself
        try:
            with httpx.Client(base_url=self.api_url, timeout=15.0) as temp_client:
                response = temp_client.post("login/", json=data)
                result = self._process_response(response)
        except Exception as e: return {"success": False, "error": f"Login request error: {str(e)}", "data": None}

        if result["success"] and result.get("data"):
            user_data = result["data"]
            token = user_data.get("token", user_data.get("access_token"))
            user_id = user_data.get("id", user_data.get("user_id"))
            uname = user_data.get("username")
            role = user_data.get("role")

            if token and user_id is not None and uname and role:
                try:
                    self._user_id = int(user_id)
                    self._username = uname
                    self._role = role
                    # CRITICAL: Set the Authorization header on the persistent client
                    self.client.headers["Authorization"] = f"Token {token}"
                    print(f"DEBUG: Instance {self._instance_id} login successful. Auth header SET on client for '{uname}'.")
                except (ValueError, TypeError):
                     self.clear_auth()
                     result["success"] = False; result["error"] = f"Login succeeded but user ID '{user_id}' is invalid."
                     result["data"] = None
            else:
                self.clear_auth()
                result["success"] = False; result["error"] = "Login succeeded but response missing essential data (token, id/user_id, username, role)."
                result["data"] = None
        else:
            self.clear_auth()

        return result

    def logout(self) -> Dict:
        """Logs out by calling the API (using client token) and clearing client header."""
        print(f"DEBUG: Instance {self._instance_id} attempting logout for '{self._username}'.")
        # Use the persistent client (which should have the header)
        result = self._handle_request("post", "auth/token/logout/")
        print(f"DEBUG: Instance {self._instance_id} logout API response: Status={result.get('status_code')}, Success={result.get('success')}")
        self.clear_auth() # Always clear local state/header on logout intent
        return result

    def clear_auth(self) -> None:
        """Clears the Authorization header from the httpx client and local user info."""
        header_was_present = "Authorization" in self.client.headers
        if header_was_present:
            # httpx headers are immutable, create new default headers
             self.client.headers = httpx.Headers()
             # Or del self.client.headers["Authorization"] might work depending on httpx version/details
        self._user_id = None
        self._username = None
        self._role = None
        print(f"DEBUG: Instance {self._instance_id} cleared auth state. Header was present: {header_was_present}")


    # --- Public methods matching api_desc.py ---
    # --- Keep all method signatures and logic the same as the ---
    # --- last requests.Session version. They will automatically ---
    # --- use self._handle_request which now uses self.client   ---

    def get_posts(self, limit: Optional[int] = None, offset: Optional[int] = None,
                  category: Optional[int] = None, author_username: Optional[str] = None,
                  tags: Optional[List[str]] = None, is_published: Optional[bool] = None,
                  featured: Optional[bool] = None, created_after: Optional[str] = None,
                  created_before: Optional[str] = None, search: Optional[str] = None,
                  ordering: Optional[str] = None) -> Dict:
        params: Dict[str, Any] = {}
        if limit is not None: params["limit"] = limit
        if offset is not None: params["offset"] = offset
        if category is not None: params["category"] = category
        if author_username is not None: params["author__username"] = author_username
        if tags is not None: params["tags"] = ','.join(tags)
        if is_published is not None: params["is_published"] = str(is_published).lower()
        if featured is not None: params["featured"] = str(featured).lower()
        if created_after is not None: params["created_after"] = created_after
        if created_before is not None: params["created_before"] = created_before
        if search is not None: params["search"] = search
        if ordering is not None: params["ordering"] = ordering
        return self._handle_request("get", "posts/", params=params)

    def create_post(self, title: str, content: str, tags: List[str],
                    category: Optional[str] = None,
                    featured_image: Optional[IOBase] = None,
                    is_published: bool = True, featured: bool = False) -> Dict:
        data: Dict[str, Any] = {"title": title, "content": content, "tags": tags, "is_published": is_published, "featured": featured}
        if category: data["category"] = category
        files = None
        if featured_image:
            # httpx expects files in a specific tuple format: (filename, file_obj, content_type)
            filename = os.path.basename(getattr(featured_image, 'name', 'image.jpg'))
            # Basic content type guessing, might need improvement
            content_type = 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png' if filename.lower().endswith('.png') else 'application/octet-stream'
            files = {"featured_image": (filename, featured_image, content_type)}
        return self._handle_request("post", "posts/", data=data, files=files)

    def get_post(self, slug: str) -> Dict:
        return self._handle_request("get", f"posts/{slug}/")

    def update_post(self, slug: str, title: Optional[str] = None,
                    content: Optional[str] = None, category: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    featured_image: Optional[IOBase] = None,
                    is_published: Optional[bool] = None, featured: Optional[bool] = None) -> Dict:
        data: Dict[str, Any] = {}
        if title is not None: data["title"] = title
        if content is not None: data["content"] = content
        if category is not None: data["category"] = category
        if tags is not None: data["tags"] = tags
        if is_published is not None: data["is_published"] = is_published
        if featured is not None: data["featured"] = featured
        files = None
        if featured_image:
            filename = os.path.basename(getattr(featured_image, 'name', 'image.jpg'))
            content_type = 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png' if filename.lower().endswith('.png') else 'application/octet-stream'
            files = {"featured_image": (filename, featured_image, content_type)}
        if not data and not files: return {"success": False, "error": "No update data provided.", "data": None}
        # Note: httpx might require PATCH data to be sent differently if files are involved
        # This implementation assumes sending 'data' alongside 'files' works similarly to requests
        return self._handle_request("patch", f"posts/{slug}/", data=data, files=files)

    def delete_post(self, slug: str) -> Dict:
        return self._handle_request("delete", f"posts/{slug}/")

    def view_post(self, slug: str) -> Dict:
        return self._handle_request("post", f"posts/{slug}/view/")

    def like_post(self, slug: str) -> Dict:
        return self._handle_request("post", f"posts/{slug}/like/")

    def save_post(self, slug: str) -> Dict:
        return self._handle_request("post", f"posts/{slug}/save/")

    def get_my_posts(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "posts/my_posts/", params=params)

    def get_saved_posts(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "posts/saved/", params=params)

    def get_featured_posts(self) -> Dict:
        return self._handle_request("get", "posts/featured/")

    def get_stats(self) -> Dict:
        return self._handle_request("get", "posts/stats/")

    def get_recent_posts(self, count: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "posts/recent/", params=params)

    def get_posts_by_category(self, slug: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        params['slug'] = slug
        return self._handle_request("get", "posts/by_category/", params=params)

    def get_posts_by_tag(self, name: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        params['name'] = name
        return self._handle_request("get", "posts/by_tag/", params=params)

    def get_posts_by_user(self, username: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        params['username'] = username
        return self._handle_request("get", "posts/by_user/", params=params)

    def get_comments(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "comments/", params=params)

    def create_comment(self, post_id: int, content: str, parent_id: Optional[int] = None) -> Dict:
        data = {"post": post_id, "content": content}
        if parent_id is not None: data["parent"] = parent_id
        return self._handle_request("post", "comments/", data=data)

    def get_comment(self, comment_id: int) -> Dict:
        return self._handle_request("get", f"comments/{comment_id}/")

    def update_comment(self, comment_id: int, content: str) -> Dict:
        data = {"content": content}
        return self._handle_request("patch", f"comments/{comment_id}/", data=data)

    def delete_comment(self, comment_id: int) -> Dict:
        return self._handle_request("delete", f"comments/{comment_id}/")

    def get_comments_by_post(self, post_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        params['post_id'] = post_id
        return self._handle_request("get", "comments/by_post/", params=params)

    def get_categories(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "categories/", params=params)

    def create_category(self, name: str) -> Dict:
        data = {"name": name}
        return self._handle_request("post", "categories/", data=data)

    def get_category(self, category_id: int) -> Dict:
        return self._handle_request("get", f"categories/{category_id}/")

    def update_category(self, category_id: int, name: str) -> Dict:
        data = {"name": name}
        return self._handle_request("patch", f"categories/{category_id}/", data=data)

    def delete_category(self, category_id: int) -> Dict:
        return self._handle_request("delete", f"categories/{category_id}/")

    def get_tags(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "tags/", params=params)

    def get_tag(self, tag_id: int) -> Dict:
        return self._handle_request("get", f"tags/{tag_id}/")

    def get_popular_tags(self) -> Dict:
        return self._handle_request("get", "tags/popular/")

    def get_posts_by_tag_id(self, tag_id: int, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k not in ['self', 'tag_id'] and v is not None}
        return self._handle_request("get", f"tags/{tag_id}/posts/", params=params)

    def get_users(self, limit: Optional[int] = None, offset: Optional[int] = None) -> Dict:
        params = {k: v for k, v in locals().items() if k != 'self' and v is not None}
        return self._handle_request("get", "users/", params=params)

    def get_user(self, user_id_to_get: int) -> Dict:
        return self._handle_request("get", f"users/{user_id_to_get}/")

    def update_user(self, user_id_to_update: int, username: Optional[str] = None,
                    email: Optional[str] = None, role: Optional[str] = None,
                    is_staff: Optional[bool] = None, is_active: Optional[bool] = None) -> Dict:
        data = {k: v for k, v in locals().items() if k not in ['self', 'user_id_to_update', 'data'] and v is not None}
        if not data: return {"success": False, "error": "No user update data provided.", "data": None}
        return self._handle_request("patch", f"users/{user_id_to_update}/", data=data)

    def delete_user(self, user_id_to_delete: int) -> Dict:
        return self._handle_request("delete", f"users/{user_id_to_delete}/")

    def get_profile(self) -> Dict:
        return self._handle_request("get", "profile/")

    def update_profile(self, bio: Optional[str] = None, avatar: Optional[IOBase] = None) -> Dict:
        data = {}
        if bio is not None: data["bio"] = bio
        files = None
        if avatar:
            filename = os.path.basename(getattr(avatar, 'name', 'avatar.jpg'))
            content_type = 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png' if filename.lower().endswith('.png') else 'application/octet-stream'
            files = {"avatar": (filename, avatar, content_type)}
        if not data and not files: return {"success": False, "error": "No profile update data provided.", "data": None}
        return self._handle_request("patch", "profile/", data=data, files=files)

    def change_password(self, current_password: str, new_password: str) -> Dict:
        data = {"current_password": current_password, "new_password": new_password}
        result = self._handle_request("post", "change-password/", data=data)
        if result.get("success"):
            self.clear_auth() # Clear session as token is now invalid
        return result

    def get_activity(self) -> Dict:
        return self._handle_request("get", "activity/")

    # --- Data Parsing Methods (Unchanged) ---
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        if not dt_string: return None
        try:
            if dt_string.endswith('Z'): dt_string = dt_string[:-1] + '+00:00'
            return datetime.fromisoformat(dt_string)
        except (ValueError, TypeError): return None

    def parse_post_data(self, post_data: Dict) -> Optional[Post]:
        if not isinstance(post_data, dict): return None
        try: return Post(id=post_data["id"], title=post_data["title"], slug=post_data["slug"], content=post_data["content"], author=post_data.get("author", "Unknown"), created_at=self._parse_datetime(post_data.get("created_at")), updated_at=self._parse_datetime(post_data.get("updated_at")), tags=post_data.get("tags", []), category=post_data.get("category"), comment_count=post_data.get("comment_count", 0), featured_image_url=post_data.get("featured_image_url"), is_published=post_data.get("is_published", False), featured=post_data.get("featured", False), view_count=post_data.get("view_count", 0))
        except KeyError: return None

    def parse_comment_data(self, comment_data: Dict) -> Optional[Comment]:
         if not isinstance(comment_data, dict): return None
         try:
            replies = [self.parse_comment_data(reply_data) for reply_data in comment_data.get("replies", []) if isinstance(reply_data, dict)]
            replies = [r for r in replies if r]
            return Comment(id=comment_data["id"], post=comment_data["post"], author=comment_data.get("author", "Unknown"), author_avatar=comment_data.get("author_avatar"), content=comment_data["content"], created_at=self._parse_datetime(comment_data.get("created_at")), parent=comment_data.get("parent"), replies=replies)
         except KeyError: return None

    def parse_category_data(self, category_data: Dict) -> Optional[Category]:
        if not isinstance(category_data, dict): return None
        try: return Category(id=category_data["id"], name=category_data["name"], slug=category_data["slug"])
        except KeyError: return None

    def parse_tag_data(self, tag_data: Dict) -> Optional[Tag]:
        if not isinstance(tag_data, dict): return None
        try: return Tag(id=tag_data["id"], name=tag_data["name"], slug=tag_data["slug"], post_count=tag_data.get("post_count", 0))
        except KeyError: return None

    def parse_user_data(self, user_data: Dict) -> Optional[User]:
        if not isinstance(user_data, dict): return None
        try: return User(id=user_data["id"], username=user_data["username"], email=user_data["email"], first_name=user_data.get("first_name"), last_name=user_data.get("last_name"), bio=user_data.get("bio"), avatar_url=user_data.get("avatar_url"), role=user_data.get("role"), is_staff=user_data.get("is_staff", False), is_active=user_data.get("is_active", True), date_joined=self._parse_datetime(user_data.get("date_joined")))
        except KeyError: return None

    def parse_stats_data(self, stats_data: Dict) -> Optional[Stats]:
        if not isinstance(stats_data, dict): return None
        try: return Stats(total_posts=stats_data["total_posts"], published_posts=stats_data["published_posts"], total_comments=stats_data["total_comments"], total_categories=stats_data["total_categories"], total_tags=stats_data["total_tags"])
        except KeyError: return None


    # Add a close method to clean up the httpx client
    def close(self):
        """Closes the underlying httpx client session."""
        try:
            self.client.close()
            print(f"DEBUG: Instance {self._instance_id} httpx client closed.")
        except Exception as e:
            print(f"ERROR: Failed to close httpx client for instance {self._instance_id}: {e}")

    def __del__(self):
        # Attempt to close the client when the object is garbage collected
        self.close()