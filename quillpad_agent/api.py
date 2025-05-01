from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Union

import requests
import json
import random
import os


@dataclass
class UserAuth:
    id: int
    token:str

@dataclass
class UserInfo:
    id:int
    email:str
    username:str
    password:str

@dataclass
class Post:
    title:str
    slug:str
    content:str
    id: Optional[int] = None
    category: Optional[str] = None
    tags_str: Optional[List[str]] = None
    image_path: Optional[str] = None
    is_published: bool = True
    featured: bool = False
    date: str = ""

@dataclass
class Comment:
    author:str
    content:str
    id: Optional[int] = None
    date:str = ""
    replies:list[Comment] = field(default_factory=lambda: [])


def api_request(
    session: requests.Session,
    api_base_url: str,
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    require_auth: bool = False,
    current_auth_token: Optional[str] = None
) -> Dict[str, Any]:
    url = f"{api_base_url}{endpoint}"
    headers: Dict[str, str] = {}
    response_info: Dict[str, Any] = {
        "success": False,
        "status": None,
        "data": None,
        "error": None,
        "method": method,
        "url": url
    }

    if require_auth:
        if not current_auth_token:
            response_info["error"] = "Authentication required, but no auth_token provided."
            response_info["status"] = 401
            return response_info
        headers['Authorization'] = f"Token {current_auth_token}"

    try:
        response: requests.Response
        if files:
            response = session.request(method, url, headers=headers, data=data, files=files, timeout=15)
        elif data:
            headers['Content-Type'] = 'application/json'
            response = session.request(method, url, headers=headers, data=json.dumps(data), timeout=15)
        else:
            response = session.request(method, url, headers=headers, timeout=15)

        response_info["status"] = response.status_code

        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                response_info["success"] = True
                response_info["data"] = None
            else:
                try:
                    json_data: Union[Dict, List, str] = response.json()
                    response_info["success"] = True
                    response_info["data"] = json_data
                except json.JSONDecodeError:
                    response_info["success"] = False
                    response_info["error"] = "Failed to decode JSON response from server."
                    response_info["data"] = response.text
        else:
            response_info["success"] = False
            response_info["error"] = f"HTTP Error {response.status_code}"
            try:
                error_data: Union[Dict, List, str] = response.json()
                response_info["data"] = error_data
            except json.JSONDecodeError:
                error_text: str = response.text
                response_info["data"] = error_text

    except requests.exceptions.RequestException as e:
        response_info["success"] = False
        response_info["error"] = f"Network Request Exception: {e}"
        response_info["status"] = None

    return response_info


class UserSession:
    __api_url = ""

    def __init__(self, info:UserInfo, api_url:str) -> None:
        self.__api_url = api_url
        self.__info:UserInfo = info
        self.__session:requests.Session = requests.Session()
        self.__auth:UserAuth | None = None


    @property
    def username(self) -> str:
        return self.__info.username

    @property
    def user_id(self) -> int:
        return self.__info.id

    @property
    def is_logged_in(self) -> bool:
        return self.__auth is not None


    def login(self) -> dict:
        result = {"username": self.username}
        if self.is_logged_in:
            result["status"] = "Already logged in"
            result["success"] = True
            return result

        login_data = {"username": self.__info.username, "password": self.__info.password}
        response_info = api_request(
            self.__session, self.__api_url, "POST", "/login/", data=login_data, require_auth=False
        )

        if response_info["success"] and isinstance(response_info["data"], dict):
            data = response_info["data"]
            if 'token' in data and 'user_id' in data:
                self.__auth = UserAuth(id=data['user_id'], token=data['token'])
                result["status"] = "logged in"
                result["success"] = True
                return result

        self.__auth = None
        result.update({
            "status": "failed",
            "success": False,
            "error": response_info.get('error', 'Unknown'),
            "data": response_info.get('data')
        })
        return result

    def logout(self):
        result:dict[Any,Any] = {"username": self.username}
        if not self.is_logged_in or not self.__auth:
            result["status"] = "Already logged out"
            result["success"] = True
            return result

        response_info = api_request(
            self.__session, self.__api_url, "POST", "/auth/token/logout/",
            require_auth=True, current_auth_token=self.__auth.token
        )
        success = response_info["success"] or response_info["status"] == 401
        self.__auth = None

        if success:
            result["status"] = "logged out"
            result["success"] = True
        else:
            result.update({
                "status": response_info["status"],
                "success": False,
                "error": response_info.get('error', 'Unknown'),
                "data": response_info.get('data')
            })
        return result


    def create_post(self, post_details: Post) -> Optional[Dict[str, Any]]:
        if not self.is_logged_in or not self.__auth:
            return {"success": False, "error": "User not logged in", "data": None}

        post_data: Dict[str, Any] = {
            'title': post_details.title,
            'content': post_details.content,
            'is_published': str(post_details.is_published).lower(),
            'featured': str(post_details.featured).lower()
        }
        if post_details.category:
            post_data['category'] = post_details.category
        if post_details.tags_str:
            post_data['tags'] = post_details.tags_str.split(",")

        files = {}
        file_handle = None
        if post_details.image_path and os.path.exists(post_details.image_path):
            try:
                file_handle = open(post_details.image_path, 'rb')
                files['featured_image'] = (os.path.basename(post_details.image_path), file_handle)
            except IOError as e:
                if file_handle: file_handle.close()
                return {"success": False, "error": f"Could not open image file: {e}", "data": None}

        response_info = api_request(
            self.__session, self.__api_url, "POST", "/posts/",
            data=post_data,
            files=files if file_handle else None,
            require_auth=True,
            current_auth_token=self.__auth.token
        )

        if file_handle:
            file_handle.close()

        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }


    def post_comment(self, post_id: int, content: str) -> Optional[Dict[str, Any]]:
        if not self.is_logged_in or not self.__auth:
             return {"success": False, "error": "User not logged in", "data": None}

        comment_data = {
            "post": post_id,
            "content": content,
            "parent": None
        }
        response_info = api_request(
            self.__session, self.__api_url, "POST", "/comments/",
            data=comment_data, require_auth=True, current_auth_token=self.__auth.token
        )
        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def reply_comment(self, post_id: int, parent_comment_id: int, content: str) -> Optional[Dict[str, Any]]:
        if not self.is_logged_in or not self.__auth:
            return {"success": False, "error": "User not logged in", "data": None}

        reply_data = {
            "post": post_id,
            "content": content,
            "parent": parent_comment_id
        }
        response_info = api_request(
            self.__session, self.__api_url, "POST", "/comments/",
            data=reply_data, require_auth=True, current_auth_token=self.__auth.token
        )

        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def like(self, post_slug: str) -> Optional[Dict[str, Any]]:
        if not self.is_logged_in or not self.__auth:
            return {"success": False, "error": "User not logged in", "data": None}

        response_info = api_request(
            self.__session, self.__api_url, "POST", f"/posts/{post_slug}/like/",
            require_auth=True, current_auth_token=self.__auth.token
        )

        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def get_post_comments(self, post_id: int) -> Dict[str, Any]:
        token = self.__auth.token if self.is_logged_in and self.__auth else None
        use_auth = self.is_logged_in
        endpoint = f"/comments/by_post/?post_id={post_id}"

        response_info = api_request(
            self.__session, self.__api_url, "GET", endpoint,
            require_auth=use_auth,
            current_auth_token=token
        )

        if response_info["success"] and not isinstance(response_info["data"], list):
             return {
                 "success": False,
                 "error": f"Fetched data format is not a list: {type(response_info['data']).__name__}",
                 "data": response_info["data"]
             }

        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def create_category(self, category_name: str) -> Dict[str, Any]:
         if not self.is_logged_in or not self.__auth:
             return {"success": False, "error": "User not logged in", "data": None}

         category_data = {"name": category_name}
         response_info = api_request(
             self.__session, self.__api_url, "POST", "/categories/",
             data=category_data, require_auth=True, current_auth_token=self.__auth.token
         )

         return {
             "success": response_info["success"],
             "data": response_info["data"],
             "error": response_info["error"] if not response_info["success"] else None
         }


class BlogApi:

    def __init__(self, base_url:str = "http://localhost:8000/api"):
        self.__api_url = base_url
        self.__session = requests.Session()
        self.__user_sessions:Dict[int, UserSession] = {}
        self.__users:List[UserInfo] = []
        self.load_users()

    @property
    def users(self):
        return self.__users


    def list_posts(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        response_info = api_request(
            self.__session, self.__api_url, "GET", f"/posts/?limit={limit}&offset={offset}",
            require_auth=False
        )
        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def list_users(self):
            return [asdict(user) for user in self.__users]

    def register(self, username:str, email:str, password:str):
        result:dict[Any,Any] = {"status_msg": ""}
        #user_id = random.randint(1000000,9999999)
        if any(u.username == username for u in self.__users):
            result["status_msg"] += " user already exists. "
            return result
        if any(u.email == email for u in self.__users):
                result["status_msg"] = "email already exists"
                return result

        reg_data = {"username": username, "email": email, "password": password}
        response_info = api_request(
            self.__session, self.__api_url, "POST", "/register/", data=reg_data, require_auth=False
        )

        if response_info["success"] and isinstance(response_info["data"], dict):
            user_data = response_info["data"]
            if 'username' in user_data:
                new_user_info = UserInfo(
                    id=user_data["id"],
                    username=user_data['username'],
                    password=password,
                    email=user_data.get('email', email)
                )

                self.__users.append(new_user_info)
                self.save_users()

                user_session = UserSession(new_user_info, self.__api_url)
                self.__user_sessions[new_user_info.id] = user_session

                result.update({
                    "status_msg": "user created",
                    "data": response_info["data"]
                })
        else:
            result["error"] = response_info.get('error', 'Unknown')
        return result


    def user_login(self, user_id: int) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}
        return user_session.login()

    def user_logout(self, user_id: int) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}
        return user_session.logout()

    def is_user_logged_in(self, user_id: int) -> bool:
        user_session = self.get_user_session(user_id=user_id)
        if user_session:
            return user_session.is_logged_in
        return False # User not found locally, so can't be logged in

    def user_create_post(
        self,
        user_id: int,
        title: str,
        content: str,
        category: str,
        tags_str:str, 
        image_path: Optional[str] = None,
        is_published: bool = True,
        featured: bool = False,
        slug: str = ""
    ) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}

        post_details = Post(
            title=title,
            content=content,
            category=category,
            # Pass tags_str to the Post dataclass
            tags_str=tags_str,
            image_path=image_path,
            is_published=is_published,
            featured=featured,
            slug=slug
        )

        return user_session.create_post(post_details)

    def user_post_comment(self, user_id: int, post_id: int, content: str) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}
        return user_session.post_comment(post_id=post_id, content=content)

    def user_reply_comment(
        self,
        user_id: int,
        post_id: int,
        parent_comment_id: int,
        content: str
    ) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}
        return user_session.reply_comment(post_id=post_id, parent_comment_id=parent_comment_id, content=content)

    def user_like_post(self, user_id: int, post_slug: str) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}
        return user_session.like(post_slug=post_slug)


    def get_post_details(self, post_slug: str) -> Dict[str, Any]:
        response_info = api_request(
            self.__session, self.__api_url, "GET", f"/posts/{post_slug}/",
        )
        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def get_post_comments(self, post_id: int) -> Dict[str, Any]:
        endpoint = f"/comments/by_post/?post_id={post_id}"
        # Find any user session to make the call, or call directly if none exist
        # This assumes get_post_comments itself handles auth correctly if needed
        user_session = next(iter(self.__user_sessions.values()), None)
        if user_session:
            return user_session.get_post_comments(post_id)
        else:
             response_info = api_request(self.__session, self.__api_url, "GET", endpoint)
             if response_info["success"] and not isinstance(response_info["data"], list):
                  return {
                      "success": False,
                      "error": f"Fetched data format is not a list: {type(response_info['data']).__name__}",
                      "data": response_info["data"]
                  }
             return {
                 "success": response_info["success"],
                 "data": response_info["data"],
                 "error": response_info["error"] if not response_info["success"] else None
             }

    def list_categories(self, limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
        response_info = api_request(
            self.__session, self.__api_url, "GET", f"/categories/?limit={limit}&offset={offset}",
            require_auth=False
        )
        return {
            "success": response_info["success"],
            "data": response_info["data"],
            "error": response_info["error"] if not response_info["success"] else None
        }

    def user_create_category(self, user_id: int, category_name: str) -> Dict[str, Any]:
        user_session = self.get_user_session(user_id=user_id)
        if user_session is None:
            return {"success": False, "error": f"User with ID {user_id} not found locally", "data": None}
        return user_session.create_category(category_name)


    def get_user_session(self, user_id:int|None = None, username: str|None = None) -> Optional[UserSession]:
        user_info: Optional[UserInfo] = None
        if username is not None:
            user_info = next((u for u in self.__users if u.username == username), None)
        elif user_id is not None:
            # Check loaded sessions first
            if user_id in self.__user_sessions:
                return self.__user_sessions[user_id]
            # Check persistent user list if not in active sessions
            user_info = next((u for u in self.__users if u.id == user_id), None)

        if not user_info:
            return None

        # Create session if user exists but session wasn't loaded/created yet
        if user_info.id not in self.__user_sessions:
             self.__user_sessions[user_info.id] = UserSession(user_info, self.__api_url, self.__session)
        return self.__user_sessions[user_info.id]

    def save_users(self, file_path:str = "users.json") -> Optional[str]:
        try:
            with open(file_path, 'w') as fp:
                json.dump([asdict(user) for user in self.__users], fp, indent=4)
            return None
        except IOError as e:
            return f"IOError saving users: {e}"
        except TypeError as e:
             return f"TypeError saving users: {e}"


    def load_users(self, file_path:str = "users.json") -> Optional[str]:
        if not os.path.exists(file_path):
            self.__users = []
            return None

        try:
            with open(file_path, 'r') as fp:
                users_data = json.load(fp)
                self.__users = [UserInfo(**user_data) for user_data in users_data if isinstance(user_data, dict)]
            self.__user_sessions = {user.id: UserSession(user, self.__api_url, self.__session) for user in self.__users}
            return None
        except (IOError, json.JSONDecodeError) as e:
            self.__users = []
            self.__user_sessions = {}
            return f"Error loading users: {e}"
        except TypeError as e:
            self.__users = []
            self.__user_sessions = {}
            return f"Data structure error loading users: {e}"


    def add_user(self, user_info:UserInfo):
        if any(u.id == user_info.id for u in self.__users):
             return
        self.__users.append(user_info)
        self.save_users()
        if user_info.id not in self.__user_sessions:
            self.__user_sessions[user_info.id] = UserSession(user_info, self.__api_url)