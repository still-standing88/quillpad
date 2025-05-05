import os
import json
from textwrap import dedent
import datetime # Added for logging timestamp
import logging # Ensure logging is imported here too

# Helper function to create directories if they don't exist
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

# --- File Contents (Revised with dedent and corrected indentation/string literal) ---

env_content = dedent("""
    ADMIN_USERNAME=admin1
    ADMIN_PASSWORD=KQX78b42
    ADMIN_EMAIL=oussamabengatrane@gmail.com
    API_KEY=YOUR_GOOGLE_API_KEY_HERE # <-- IMPORTANT: Replace with your actual key
    BASE_URL=http://172.189.176.11/api # <-- Or http://localhost:8000/api or your actual backend URL
    MODEL_NAME=gemini-1.5-flash-latest
    MODEL_TEMPRATURE=0.8
    # Optional: Set log level for the agent/runner (DEBUG, INFO, WARNING, ERROR)
    LOG_LEVEL=INFO
""")

api_py_content = dedent(r"""
    from __future__ import annotations
    from dataclasses import dataclass, field
    from typing import Dict, Any, List, Optional, Union

    import requests
    import json
    import os
    import logging

    # Setup basic logging
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger("BlogApi")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    @dataclass
    class PostData:
        title: str
        content: str
        category: Optional[str] = None
        tags_str: Optional[str] = None # Comma-separated string
        image_path: Optional[str] = None
        is_published: bool = True
        featured: bool = False
        slug: Optional[str] = None

    @dataclass
    class UserCredentials:
        username: str
        password: str
        email: Optional[str] = None

    def api_request(
        session: requests.Session,
        api_base_url: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers: Dict[str, str] = {}
        response_info: Dict[str, Any] = {
            "success": False, "status": None, "data": None,
            "error": None, "method": method, "url": url
        }

        if auth_token:
            headers['Authorization'] = f"Token {auth_token}"

        log.debug(f"API Request: {method} {url} | JSON: {json_data is not None} | Form Data: {data is not None} | Files: {files is not None} | Auth: {auth_token is not None}")

        try:
            response: requests.Response
            request_kwargs = {"headers": headers, "timeout": 25}

            if files:
                request_kwargs["data"] = data
                request_kwargs["files"] = files
                log.debug(f"Sending multipart request. Files: {list(files.keys()) if files else 'None'}, Data fields: {list(data.keys()) if data else 'None'}")
            elif json_data:
                headers['Content-Type'] = 'application/json'
                request_kwargs["data"] = json.dumps(json_data)
                log.debug(f"Sending JSON request. Data: {json_data}")
            elif data:
                 headers['Content-Type'] = 'application/x-www-form-urlencoded'
                 request_kwargs["data"] = data
                 log.debug(f"Sending Form data request. Data: {data}")
            else:
                log.debug("Sending request with no body.")
                pass

            response = session.request(method, url, **request_kwargs)
            response_info["status"] = response.status_code
            log.debug(f"API Response: Status {response.status_code} | URL: {url}")

            response_data = None
            response_text = response.text
            try:
                if response.status_code != 204 and response.content:
                     content_type = response.headers.get('Content-Type', '').lower()
                     if 'application/json' in content_type:
                         response_data = response.json()
                         response_info["data"] = response_data
                         log.debug(f"API Response JSON: {response_data}")
                     else:
                          log.debug(f"API Response content type is '{content_type}', not parsing as JSON. Raw text: {response_text[:200]}...")
                          response_info["data"] = response_text
                elif response.status_code == 204:
                     log.debug("API Response is 204 No Content.")
                     response_info["data"] = None
                else:
                    log.debug("API Response has no content.")
                    response_info["data"] = None
            except json.JSONDecodeError:
                response_info["data"] = response_text
                log.warning(f"Failed to decode JSON response from {url}. Raw text: {response_text[:200]}...")
                if 200 <= response.status_code < 300:
                    response_info["error"] = "Server returned success status but response was not valid JSON."

            if 200 <= response.status_code < 300:
                response_info["success"] = True
                if response_info.get("error") == "Server returned success status but response was not valid JSON.":
                     response_info["error"] = None
            else:
                response_info["success"] = False
                error_msg = f"HTTP Error {response.status_code}"
                if isinstance(response_data, dict):
                    detail = response_data.get('detail')
                    non_field = response_data.get('non_field_errors')
                    other_errors = {k: v for k, v in response_data.items() if k not in ['detail', 'non_field_errors']}
                    if detail: error_msg += f": {detail}"
                    elif non_field: error_msg += f": {', '.join(non_field)}"
                    elif other_errors:
                        error_parts = [f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in other_errors.items()]
                        error_msg += f": {'; '.join(error_parts)}"
                elif response_text:
                     error_msg += f" - Server Response: {response_text[:200]}"
                response_info["error"] = error_msg
                log.error(f"API Error: {error_msg} | Status: {response.status_code} | URL: {url}")

        except requests.exceptions.Timeout:
            response_info["success"] = False
            response_info["error"] = "Network Request Exception: Request timed out."
            response_info["status"] = None
            log.error(f"API Request Timeout for {method} {url}")
        except requests.exceptions.ConnectionError as e:
            response_info["success"] = False
            response_info["error"] = f"Network Request Exception: Connection error ({e})."
            response_info["status"] = None
            log.error(f"API Connection Error for {method} {url}: {e}")
        except requests.exceptions.RequestException as e:
            response_info["success"] = False
            response_info["error"] = f"Network Request Exception: {type(e).__name__}"
            response_info["status"] = None
            log.error(f"API Request Exception for {method} {url}: {e}")

        return response_info

    class BlogApi:
        def __init__(self, base_url: str = "http://localhost:8000/api"):
            self.__api_url = base_url.rstrip('/')
            self.__session = requests.Session()
            self.__active_tokens: Dict[int, str] = {}
            log.info(f"BlogApi initialized with base URL: {self.__api_url}")

        def _get_token(self, user_id: int) -> Optional[str]:
            return self.__active_tokens.get(user_id)

        def list_posts(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
            log.info(f"Listing posts (limit={limit}, offset={offset})")
            return api_request(self.__session, self.__api_url, "GET", f"/posts/?limit={limit}&offset={offset}")

        def list_users(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
            log.info(f"Listing users from API (limit={limit}, offset={offset})")
            admin_token = next(iter(self.__active_tokens.values()), None)
            if not admin_token:
                 log.warning("Listing users called without a locally known admin token.")
            return api_request(
                self.__session, self.__api_url, "GET", f"/users/?limit={limit}&offset={offset}",
                auth_token=admin_token
            )

        def register(self, credentials: UserCredentials) -> Dict[str, Any]:
            log.info(f"Registering user: {credentials.username}")
            if not credentials.email:
                 return {"success": False, "error": "Email is required for registration.", "data": None}
            reg_data = {"username": credentials.username, "email": credentials.email, "password": credentials.password}
            response = api_request(self.__session, self.__api_url, "POST", "/register/", json_data=reg_data)
            if not response["success"]: log.error(f"User registration failed for '{credentials.username}': {response.get('error')}")
            return response

        def user_login(self, credentials: UserCredentials) -> Dict[str, Any]:
            log.info(f"Attempting login for user: {credentials.username}")
            login_data = {"username": credentials.username, "password": credentials.password}
            response = api_request(self.__session, self.__api_url, "POST", "/login/", json_data=login_data)
            if response["success"] and isinstance(response["data"], dict):
                api_data = response["data"]
                token = api_data.get("token")
                user_id = None
                try: user_id = int(api_data.get("user_id")) if api_data.get("user_id") is not None else None
                except (ValueError, TypeError): log.error(f"Login API returned non-integer user_id: {api_data.get('user_id')}")
                if token and user_id is not None:
                    self.__active_tokens[user_id] = token
                    log.info(f"User '{credentials.username}' (ID: {user_id}) logged in successfully.")
                    response["data"]["logged_in_user_id"] = user_id
                else:
                    log.error(f"Login succeeded for '{credentials.username}', but response missing token or valid user_id.")
                    response["success"] = False; response["error"] = "API response malformed"; response["data"] = None
            elif response["success"]:
                 log.error(f"Login succeeded for '{credentials.username}', but response data format unexpected: {type(response.get('data'))}")
                 response["success"] = False; response["error"] = "API response format unexpected"; response["data"] = None
            else: log.error(f"Login failed for '{credentials.username}': {response.get('error')}")
            return response

        def user_logout(self, user_id: int) -> Dict[str, Any]:
            log.info(f"Attempting logout for user ID: {user_id}")
            token = self._get_token(user_id)
            if not token:
                log.warning(f"Logout requested for User ID {user_id}, but no active token found locally.")
                if user_id in self.__active_tokens: del self.__active_tokens[user_id]
                return {"success": True, "status": 200, "data": {"message": "User not logged in locally."}, "error": None}
            response = api_request(self.__session, self.__api_url, "POST", "/auth/token/logout/", auth_token=token)
            if user_id in self.__active_tokens:
                del self.__active_tokens[user_id]; log.info(f"Removed stored token for user ID: {user_id}")
            if response["success"] or response["status"] == 401:
                log.info(f"Logout successful/token invalid for user ID: {user_id}")
                response["success"] = True; response["error"] = None
            else: log.error(f"Logout API call failed for user ID {user_id}: {response.get('error')} (Status: {response.get('status')})")
            return response

        def is_user_logged_in(self, user_id: int) -> bool:
            is_logged_in = user_id in self.__active_tokens
            log.debug(f"Checking login status for User ID {user_id}: {'Logged In' if is_logged_in else 'Not Logged In'}")
            return is_logged_in

        def user_create_post(self, user_id: int, post_data: PostData) -> Dict[str, Any]:
            log.info(f"User ID {user_id} creating post: '{post_data.title}'")
            token = self._get_token(user_id)
            if not token: return {"success": False, "error": "User not logged in.", "data": None}
            form_data: Dict[str, Any] = {
                'title': post_data.title, 'content': post_data.content,
                'is_published': str(post_data.is_published).lower(), 'featured': str(post_data.featured).lower(),
            }
            if post_data.category: form_data['category'] = post_data.category
            if post_data.tags_str: form_data['tags'] = post_data.tags_str
            if post_data.slug: form_data['slug'] = post_data.slug
            files: Optional[Dict[str, Any]] = None; file_handle = None
            if post_data.image_path and os.path.exists(post_data.image_path):
                try:
                    file_handle = open(post_data.image_path, 'rb')
                    files = {'featured_image': (os.path.basename(post_data.image_path), file_handle)}
                except IOError as e: log.error(f"Could not open image file {post_data.image_path}: {e}"); return {"success": False, "error": f"IOError opening image: {e}", "data": None}
            elif post_data.image_path: log.warning(f"Image path specified but not found: {post_data.image_path}")
            try:
                 response = api_request(self.__session, self.__api_url, "POST", "/posts/", data=form_data if files else None, json_data=form_data if not files else None, files=files, auth_token=token)
            finally:
                 if file_handle: file_handle.close()
            if not response["success"]: log.error(f"Failed to create post '{post_data.title}' by User ID {user_id}: {response.get('error')}")
            return response

        def user_post_comment(self, user_id: int, post_id: int, content: str) -> Dict[str, Any]:
            log.info(f"User ID {user_id} commenting on Post ID {post_id}")
            token = self._get_token(user_id)
            if not token: return {"success": False, "error": "User not logged in.", "data": None}
            comment_data = {"post": post_id, "content": content, "parent": None}
            response = api_request(self.__session, self.__api_url, "POST", "/comments/", json_data=comment_data, auth_token=token)
            if not response["success"]: log.error(f"Failed comment by User ID {user_id} on Post ID {post_id}: {response.get('error')}")
            return response

        def user_reply_comment(self, user_id: int, post_id: int, parent_comment_id: int, content: str) -> Dict[str, Any]:
            log.info(f"User ID {user_id} replying to Comment ID {parent_comment_id} on Post ID {post_id}")
            token = self._get_token(user_id)
            if not token: return {"success": False, "error": "User not logged in.", "data": None}
            reply_data = {"post": post_id, "content": content, "parent": parent_comment_id}
            response = api_request(self.__session, self.__api_url, "POST", "/comments/", json_data=reply_data, auth_token=token)
            if not response["success"]: log.error(f"Failed reply by User ID {user_id} to Comment ID {parent_comment_id}: {response.get('error')}")
            return response

        def user_like_post(self, user_id: int, post_slug: str) -> Dict[str, Any]:
            log.info(f"User ID {user_id} liking Post Slug: {post_slug}")
            token = self._get_token(user_id)
            if not token: return {"success": False, "error": "User not logged in.", "data": None}
            response = api_request(self.__session, self.__api_url, "POST", f"/posts/{post_slug}/like/", auth_token=token)
            if not response["success"]: log.error(f"Failed like toggle for Post Slug {post_slug} by User ID {user_id}: {response.get('error')}")
            return response

        def get_post_details(self, post_slug: str) -> Dict[str, Any]:
            log.info(f"Fetching details for Post Slug: {post_slug}")
            return api_request(self.__session, self.__api_url, "GET", f"/posts/{post_slug}/")

        def get_post_comments(self, post_id: int) -> Dict[str, Any]:
            log.info(f"Fetching comments for Post ID: {post_id}")
            return api_request(self.__session, self.__api_url, "GET", f"/comments/by_post/?post_id={post_id}")

        def list_categories(self, limit: int = 1000, offset: int = 0) -> Dict[str, Any]:
            log.info(f"Listing categories (limit={limit}, offset={offset})")
            return api_request(self.__session, self.__api_url, "GET", f"/categories/?limit={limit}&offset={offset}")

        def user_create_category(self, user_id: int, category_name: str) -> Dict[str, Any]:
            log.info(f"User ID {user_id} creating category: '{category_name}'")
            token = self._get_token(user_id)
            if not token: return {"success": False, "error": "User not logged in (required for category creation).", "data": None}
            category_data = {"name": category_name}
            response = api_request(self.__session, self.__api_url, "POST", "/categories/", json_data=category_data, auth_token=token)
            if not response["success"]: log.error(f"Failed to create category '{category_name}' by User ID {user_id}: {response.get('error')}")
            return response

        def get_logged_in_user_ids(self) -> List[int]:
            return list(self.__active_tokens.keys())

        def clear_all_sessions(self):
            log.warning("Clearing all stored user tokens.")
            self.__active_tokens.clear()
""")

# agent.py: Corrected string literal termination and indentation around line 551
agent_py_content = dedent(r"""
    import datetime as dt
    import json
    import logging
    import time
    import os # Added for path manipulation
    from typing import Any, Dict, List, Optional

    from google.generativeai import Client, Types as GenAiTypes
    from api import BlogApi, PostData, UserCredentials
    from api_desc import blog_api_tools

    log = logging.getLogger("QuillpadAgent")

    system_prompt = """
You are an AI agent simulating activity on a blogging platform (QuillPad).
Your goal is to create realistic user interactions over time using the provided API tools.

**Workflow:**
1.  **Choose an Action:** Decide what action to take (register, login, create post, comment, list things, etc.).
2.  **Select User:** If the action requires a logged-in user, decide which user will perform it. You need their *username* and *password* (which you should remember from registration). You can list users or posts to get IDs/slugs if needed.
3.  **Login (If Necessary):** Check `is_user_logged_in` for the *user_id*. If not logged in, use the `user_login` tool with their *username* and *password*. The result will indicate success and provide the `logged_in_user_id`. Remember this ID!
4.  **Perform Action:** Use the appropriate tool, passing the correct `user_id` of the *currently logged-in user* for authenticated actions (like creating posts, commenting, liking, creating categories).
5.  **Logout (Optional):** You can log users out using `user_logout` with their `user_id` to simulate session endings.
6.  **Log Results:** After each *complete action sequence* (e.g., register -> login -> create post -> logout), provide a concise log message summarizing what you did, the user involved, the outcome (success/failure), any relevant IDs/slugs, and any errors encountered.

**Guidelines:**
*   **User Simulation:** Create diverse users with plausible names, emails, and passwords. Register them first, then log them in to act. **Remember the credentials you create!**
*   **Content Generation:** Write varied and relatively coherent blog posts (using Markdown) and comments. Simulate discussions, questions, and replies in comment threads. Use Markdown formatting for posts.
*   **Error Handling:** If a tool call fails (e.g., login failure, post creation error, non-existent resource), acknowledge the error in your log and decide whether to retry (e.g., login again), try something else, or abandon the action. Don't get stuck retrying indefinitely if something is fundamentally wrong.
*   **State Awareness:** Use `is_user_logged_in` to check the status before performing authenticated actions. Use `list_users` or `list_posts` or `list_categories` if you need to find existing entities or IDs.
*   **Realism:** Vary the actions. Have users comment, reply, and like posts. Simulate different user roles (readers commenting, authors posting). You can suggest a user should be promoted to 'author' in your log.
*   **Admin User:** An admin user (username specified at startup) exists. You might need to log in as the admin to perform actions like creating categories or listing all users. Remember the admin password!

You will receive periodic prompts to take an action. Respond ONLY with the API tool calls needed to complete your chosen action sequence. Once the tools return results, you will be prompted again, and you should respond with your summary log message.
""" # <-- CORRECTLY TERMINATED STRING LITERAL

    class QuillpadAgent:
        """
        AI Agent using Google GenAI to interact with the BlogApi.
        """
        def __init__(
            self,
            blog_instance: BlogApi,
            api_key: str,
            model_id: str,
            admin_credentials: UserCredentials,
            model_temperature: float = 1.0,
            log_file: str = "agent_activity.log",
            print_log: bool = False
        ) -> None:
            self.__log_file = log_file
            self.__print_log = print_log
            self.__blog: BlogApi = blog_instance
            self.__admin_credentials = admin_credentials

            self.__api_function_map = {
                "list_posts": self.__blog.list_posts,
                "list_users": self.__blog.list_users,
                "register": self._handle_register,
                "user_login": self._handle_login,
                "user_logout": self.__blog.user_logout,
                "is_user_logged_in": self._handle_is_logged_in,
                "user_create_post": self._handle_create_post,
                "user_post_comment": self.__blog.user_post_comment,
                "user_reply_comment": self.__blog.user_reply_comment,
                "user_like_post": self.__blog.user_like_post,
                "get_post_details": self.__blog.get_post_details,
                "get_post_comments": self.__blog.get_post_comments,
                "list_categories": self.__blog.list_categories,
                "user_create_category": self.__blog.user_create_category,
            }

            if not api_key: raise ValueError("Google GenAI API Key is required.")
            self.__client = Client(api_key=api_key)
            self.__model_id = model_id
            self.__chat_config = GenAiTypes.GenerationConfig(temperature=model_temperature)

            self.__chat_history: List[Dict[str, Any]] = [
                 {'role': 'user', 'parts': [GenAiTypes.Part(text=system_prompt)]}, # Use Part object
                 {'role': 'model', 'parts': [GenAiTypes.Part(text="Understood. I am ready to simulate activity on the QuillPad blog platform using the provided API tools. I will manage user sessions by logging users in before they perform actions and logging the results.")]}
            ]

            log.info(f"QuillpadAgent initialized with model: {self.__model_id}, temperature: {model_temperature}")
            self._initial_admin_login()

        def _initial_admin_login(self):
            log.info(f"Attempting initial login for admin user '{self.__admin_credentials.username}'...")
            result = self.__blog.user_login(self.__admin_credentials)
            if result.get("success"):
                admin_data = result.get("data", {})
                admin_id = admin_data.get("logged_in_user_id", "Unknown")
                log.info(f"Admin user '{self.__admin_credentials.username}' (ID: {admin_id}) logged in successfully at startup.")
            else:
                log.warning(f"Initial admin login failed: {result.get('error')}")

        def _log_action(self, message: str):
            timestamp = dt.datetime.now().isoformat()
            log_entry = f"{timestamp} - AGENT_LOG: {message}\n"
            if self.__print_log: print(log_entry.strip())
            try:
                log_dir = os.path.dirname(self.__log_file)
                if log_dir and not os.path.exists(log_dir): os.makedirs(log_dir)
                with open(self.__log_file, 'a', encoding='utf-8') as fp: fp.write(log_entry)
            except IOError as e: log.error(f"Failed to write to agent log file '{self.__log_file}': {e}")
            except Exception as e: log.exception(f"Unexpected error writing to agent log file: {e}")

        def _handle_register(self, username: str, email: str, password: str) -> Dict[str, Any]:
            credentials = UserCredentials(username=username, email=email, password=password)
            return self.__blog.register(credentials)

        def _handle_login(self, username: str, password: str) -> Dict[str, Any]:
            credentials = UserCredentials(username=username, password=password)
            return self.__blog.user_login(credentials)

        def _handle_is_logged_in(self, user_id: int) -> Dict[str, Any]:
             is_logged_in = self.__blog.is_user_logged_in(user_id)
             return {"is_logged_in": is_logged_in}

        def _handle_create_post(
            self, user_id: int, title: str, content: str, category: Optional[str] = None,
            tags_str: Optional[str] = None, image_path: Optional[str] = None,
            is_published: bool = True, featured: bool = False, slug: Optional[str] = None
        ) -> Dict[str, Any]:
            if not title or not content: return {"success": False, "error": "Title and content are required."}
            post_data = PostData(
                title=title, content=content, category=category, tags_str=tags_str,
                image_path=image_path, is_published=is_published, featured=featured, slug=slug
            )
            return self.__blog.user_create_post(user_id, post_data)

        def trigger_action(self, prompt: str = "What action should be taken next?"):
            log.info(f"Triggering agent action with prompt: '{prompt}'")
            logged_in_ids = self.__blog.get_logged_in_user_ids()
            system_context = f"Current UTC time: {dt.datetime.utcnow().isoformat()}Z.\nCurrently logged in user IDs (agent state): {logged_in_ids if logged_in_ids else 'None'}."
            user_message = f"{system_context}\n\nPrompt: {prompt}"
            self._add_to_history('user', user_message)

            try:
                response = self._send_chat_message_with_retry(self.__chat_history)
                log.debug("Raw model response received.")
                model_content_obj = response.candidates[0].content
                self._add_to_history('model', model_content_obj)

                final_response = self._process_function_calls(response)
                final_text = self._extract_text_from_response(final_response)

                if final_text:
                     log.info("Model provided final text response.")
                     self._log_action(f"Model Summary/Response: {final_text}")
                else:
                     log.warning("Model did not provide a final text response after processing tool calls.")
                     last_model_part_repr = 'N/A'
                     if self.__chat_history and self.__chat_history[-1]['role'] == 'model':
                         try: last_model_part_repr = repr(self.__chat_history[-1]['parts'][0]) if self.__chat_history[-1]['parts'] else 'Empty Parts'
                         except Exception: last_model_part_repr = '(Error getting representation)'
                     self._log_action(f"WARNING: No final text response from model. Last model part: {last_model_part_repr}")

            except Exception as e:
                log.exception(f"An error occurred during agent action processing: {e}")
                self._log_action(f"ERROR: An unexpected error occurred during agent turn: {e}")
                self._handle_chat_error()

        def _process_function_calls(self, initial_response: GenAiTypes.GenerateContentResponse) -> GenAiTypes.GenerateContentResponse:
            current_response = initial_response
            max_tool_cycles = 5
            cycle_count = 0

            while cycle_count < max_tool_cycles:
                last_model_content = current_response.candidates[0].content
                function_calls = []
                if last_model_content and hasattr(last_model_content, 'parts'):
                     function_calls = [part.function_call for part in last_model_content.parts if hasattr(part, 'function_call')]

                if not function_calls:
                    log.debug("No function calls in the latest model response. Exiting loop.")
                    return current_response

                cycle_count += 1
                log.info(f"--- Starting Tool Execution Cycle {cycle_count}/{max_tool_cycles} ---")

                api_responses: List[GenAiTypes.Part] = []
                log.info(f"Model requested {len(function_calls)} function call(s).")

                for func_call in function_calls:
                     if not func_call or not hasattr(func_call, 'name'): continue
                     func_name = func_call.name
                     args = dict(func_call.args) if hasattr(func_call, 'args') and func_call.args is not None else {}
                     log.info(f"Executing tool: {func_name} with args: {args}")

                     if func_name in self.__api_function_map:
                         try:
                             result = self.__api_function_map[func_name](**args)
                             log.debug(f"Tool '{func_name}' executed. Raw result: {result}")
                             try:
                                 result_package = result if isinstance(result, dict) else {"result": result}
                                 json.dumps(result_package) # Test serialization
                                 log.debug(f"Tool '{func_name}' sending result package: {result_package}")
                                 api_responses.append(GenAiTypes.Part(function_response=GenAiTypes.FunctionResponse(name=func_name, response=result_package)))
                             except TypeError as json_error:
                                 log.error(f"Result for {func_name} not JSON serializable: {json_error}. Result: {result}")
                                 api_responses.append(GenAiTypes.Part(function_response=GenAiTypes.FunctionResponse(name=func_name, response={"error": f"Tool result not JSON serializable: {json_error}"})))
                         except TypeError as e:
                             log.error(f"TypeError calling {func_name} with args {args}: {e}")
                             api_responses.append(GenAiTypes.Part(function_response=GenAiTypes.FunctionResponse(name=func_name, response={"error": f"Invalid arguments for tool '{func_name}': {e}"})))
                         except Exception as e:
                             log.exception(f"Error executing function {func_name}: {e}")
                             api_responses.append(GenAiTypes.Part(function_response=GenAiTypes.FunctionResponse(name=func_name, response={"error": f"Tool '{func_name}' execution failed: {type(e).__name__}"})))
                     else:
                         log.error(f"Function '{func_name}' requested but not available/mapped.")
                         api_responses.append(GenAiTypes.Part(function_response=GenAiTypes.FunctionResponse(name=func_name, response={"error": f"Function '{func_name}' not found."})))

                if not api_responses:
                     log.warning("No valid function calls could be processed. Breaking tool loop.")
                     break

                self._add_to_history('function', api_responses)

                log.info(f"Sending {len(api_responses)} function response(s) back (End Cycle {cycle_count}).")
                try:
                    current_response = self._send_chat_message_with_retry(self.__chat_history)
                    self._add_to_history('model', current_response.candidates[0].content)
                except Exception as e:
                     log.exception(f"Error getting next model response after function calls: {e}")
                     self._handle_chat_error()
                     break # Break loop on error

            if cycle_count >= max_tool_cycles:
                 log.warning(f"Exceeded maximum tool execution cycles ({max_tool_cycles}).")

            log.info("--- Finished Tool Processing Loop ---")
            return current_response


        def _send_chat_message_with_retry(self, history: List[Dict], max_retries=3, delay=5):
            attempt = 0
            last_exception = None
            while attempt < max_retries:
                try:
                    formatted_history = self._prepare_history_for_sdk(history)
                    log.debug(f"Sending history (len={len(formatted_history)}) to model (Attempt {attempt + 1})...")

                    # Start chat with history excluding the last message/parts
                    chat = self.__client.start_chat(history=formatted_history[:-1])
                    last_message_content = formatted_history[-1]['parts'] # Get parts from the last history item

                    response = chat.send_message(
                         last_message_content,
                         generation_config=self.__chat_config,
                         tools=[blog_api_tools]
                    )
                    log.debug(f"Model response received (Attempt {attempt + 1}).")

                    if not response.candidates or not hasattr(response.candidates[0], 'content'):
                         finish_reason = "Unknown"
                         safety_ratings = "N/A"
                         try: # Safely access attributes
                              if response.candidates:
                                   finish_reason = response.candidates[0].finish_reason.name
                                   safety_ratings = [(r.category.name, r.probability.name) for r in response.candidates[0].safety_ratings]
                         except Exception: pass # Ignore errors getting debug info
                         raise ValueError(f"Invalid response structure. Finish Reason: {finish_reason}, Safety: {safety_ratings}")

                    return response

                except Exception as e:
                    last_exception = e
                    attempt += 1
                    log.error(f"Error sending/receiving message (Attempt {attempt}/{max_retries}): {type(e).__name__} - {e}")
                    if attempt >= max_retries: log.critical("Max retries reached."); break
                    log.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)

            raise last_exception or RuntimeError("Unknown error after retries in _send_chat_message_with_retry")


        def _prepare_history_for_sdk(self, history: List[Dict]) -> List[Dict]:
            """Sanitizes history for the Google GenAI SDK."""
            prepared_history = []
            for item in history:
                if not isinstance(item, dict) or 'role' not in item or 'parts' not in item:
                    log.warning(f"Skipping invalid history item (missing role/parts): {item}")
                    continue

                role = item['role']
                parts_raw = item['parts']

                # Ensure 'parts' is a list (or convert Content object)
                if isinstance(parts_raw, GenAiTypes.Content): # <-- Check for Content obj
                    parts_list = list(parts_raw.parts)
                elif not isinstance(parts_raw, list):
                    log.warning(f"History parts for role '{role}' not list/Content ({type(parts_raw)}), converting.")
                    if isinstance(parts_raw, str): parts_list = [GenAiTypes.Part(text=parts_raw)] # Use Part()
                    else: log.error(f"Cannot convert parts for role '{role}'. Skipping item."); continue
                else:
                    parts_list = parts_raw # It's already a list

                # Sanitize individual parts
                sanitized_parts = []
                for part_raw in parts_list:
                    # If already a Part object, keep it
                    if isinstance(part_raw, GenAiTypes.Part):
                        sanitized_parts.append(part_raw)
                    # If it's a dict, try creating a Part (basic validation)
                    elif isinstance(part_raw, dict):
                        # Check for known part structures before creating blindly
                        if 'text' in part_raw:
                             sanitized_parts.append(GenAiTypes.Part(text=str(part_raw['text'])))
                        elif 'function_call' in part_raw:
                             # Assume dict structure is correct for FunctionCall
                             try: sanitized_parts.append(GenAiTypes.Part(function_call=part_raw['function_call']))
                             except Exception as e: log.warning(f"Could not create Part from function_call dict: {e}, Part: {part_raw}")
                        elif 'function_response' in part_raw:
                             # Assume dict structure is correct for FunctionResponse
                             try: sanitized_parts.append(GenAiTypes.Part(function_response=part_raw['function_response']))
                             except Exception as e: log.warning(f"Could not create Part from function_response dict: {e}, Part: {part_raw}")
                        else:
                             log.warning(f"Skipping unrecognized part dictionary structure: {part_raw}")
                    # If it's just a string, wrap it
                    elif isinstance(part_raw, str):
                        sanitized_parts.append(GenAiTypes.Part(text=part_raw))
                    else:
                        log.warning(f"Skipping unrecognized part type ({type(part_raw)}) for role '{role}': {part_raw}")

                if sanitized_parts:
                    prepared_history.append({'role': role, 'parts': sanitized_parts})
                else:
                    log.warning(f"No valid parts for history item role '{role}'. Skipping.")

            return prepared_history


        def _add_to_history(self, role: str, content: Any):
            """Adds content to history, ensuring parts are correctly formatted."""
            parts_to_add: List[GenAiTypes.Part] = []
            if isinstance(content, str):
                parts_to_add = [GenAiTypes.Part(text=content)]
            elif isinstance(content, list) and all(isinstance(p, GenAiTypes.Part) for p in content):
                parts_to_add = content # Already a list of Parts
            elif isinstance(content, GenAiTypes.Content):
                 parts_to_add = list(content.parts) # Extract parts from Content object
            elif isinstance(content, dict) and 'parts' in content and isinstance(content['parts'], list):
                 # Handle case where a history-like dict is passed (e.g., from model response)
                 # Make sure internal parts are actual Part objects if possible
                 raw_parts = content['parts']
                 converted_parts = []
                 for p in raw_parts:
                      if isinstance(p, GenAiTypes.Part): converted_parts.append(p)
                      elif isinstance(p, dict) and 'text' in p: converted_parts.append(GenAiTypes.Part(text=str(p['text'])))
                      # Add more checks for function_call/response dicts if needed
                      else: log.warning(f"Could not convert part {p} to Part object in _add_to_history."); converted_parts.append(GenAiTypes.Part(text=str(p))) # Fallback
                 parts_to_add = converted_parts
            else:
                 log.warning(f"Unexpected content type ({type(content)}) for role '{role}' in _add_to_history. Converting to string.")
                 parts_to_add = [GenAiTypes.Part(text=str(content))]

            if not parts_to_add:
                 log.warning(f"Attempted to add empty parts to history for role '{role}'. Skipping.")
                 return

            self.__chat_history.append({'role': role, 'parts': parts_to_add})
            log.debug(f"Added to history: Role='{role}', Parts Count={len(parts_to_add)}")


        def _extract_text_from_response(self, response: GenAiTypes.GenerateContentResponse) -> str:
            """Safely extracts text from the model's response candidate."""
            try:
                if hasattr(response, 'text'): return response.text.strip() # Check direct attribute first
                all_text = []
                # Check candidates list structure
                if response.candidates and len(response.candidates) > 0:
                     candidate = response.candidates[0]
                     # Check content structure
                     if hasattr(candidate, 'content') and candidate.content and hasattr(candidate.content, 'parts'):
                          for part in candidate.content.parts:
                              # Check part structure
                              if hasattr(part, 'text') and isinstance(part.text, str):
                                   all_text.append(part.text)
                return "\n".join(all_text).strip()
            except Exception as e: # Catch broader exceptions during attribute access
                log.error(f"Could not extract text from response: {e}. Response: {response}", exc_info=True)
                return ""


        def _handle_chat_error(self):
            """Handles errors during chat interaction by trimming history."""
            log.error("Attempting simple history recovery after chat error.")
            if len(self.__chat_history) >= 2:
                # More robust check: ensure last two items are user/model or function/model
                last_role = self.__chat_history[-1].get('role')
                second_last_role = self.__chat_history[-2].get('role')
                if (second_last_role == 'user' and last_role == 'model') or \
                   (second_last_role == 'function' and last_role == 'model'):
                    log.warning("Removing the last exchange (user/func -> model) from history.")
                    self.__chat_history.pop() # Remove model response
                    self.__chat_history.pop() # Remove user/function input
                else:
                    log.warning(f"History end roles '{second_last_role}' -> '{last_role}' not standard exchange. Removing just last item.")
                    self.__chat_history.pop()
            elif len(self.__chat_history) > 1: # Keep initial system prompt if possible
                 log.warning("History has only system prompt + one item after error. Removing last item.")
                 self.__chat_history.pop()
            else: log.error("Chat history too short or structure unrecognizable. Cannot trim.")

""")

# Indentation fixed for api_desc.py (Should be okay)
api_desc_py_content = dedent(r"""
    from google.generativeai import types as GenAiTypes

    list_posts_function = GenAiTypes.FunctionDeclaration(
        name="list_posts",
        description="Retrieves a paginated list of blog posts from the API. Does not require login.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Maximum number of posts to return (e.g., 5, 10). Defaults to API default."),
                "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Number of posts to skip for pagination (e.g., 0, 10, 20). Defaults to 0.")
            },
            required=[]
        )
    )

    list_users_function = GenAiTypes.FunctionDeclaration(
        name="list_users",
        description="Retrieves a paginated list of registered users from the API. Requires admin privileges (implicitly uses an available logged-in admin token if possible).",
         parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Maximum number of users to return. Defaults to API default."),
                "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Number of users to skip for pagination. Defaults to 0.")
            },
            required=[]
        )
    )

    register_function = GenAiTypes.FunctionDeclaration(
        name="register",
        description="Registers a new user account on the platform.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "username": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The desired username (must be unique)."),
                "email": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The user's email address (must be unique)."),
                "password": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The desired password for the account.")
            },
            required=["username", "email", "password"]
        )
    )

    user_login_function = GenAiTypes.FunctionDeclaration(
        name="user_login",
        description="Logs in a previously registered user to obtain an authentication token for subsequent actions. Returns user ID and token on success.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "username": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The username of the user trying to log in."),
                "password": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The password for the user.")
            },
            required=["username", "password"]
        )
    )

    user_logout_function = GenAiTypes.FunctionDeclaration(
        name="user_logout",
        description="Logs out the specified user by invalidating their current session token.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the user to log out. This user must currently be logged in according to the agent's state.")
            },
            required=["user_id"]
        )
    )

    is_user_logged_in_function = GenAiTypes.FunctionDeclaration(
        name="is_user_logged_in",
        description="Checks the agent's internal state to see if a user is currently considered logged in (i.e., has an active token stored). Returns {'is_logged_in': boolean}.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the user whose login status needs to be checked.")
            },
            required=["user_id"]
        )
    )

    user_create_post_function = GenAiTypes.FunctionDeclaration(
        name="user_create_post",
        description="Creates a new blog post. Requires the user to be logged in.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the logged-in user creating the post."),
                "title": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The title of the blog post."),
                "content": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The main content of the blog post, Markdown format is supported."),
                "category": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. The name of the category for the post. Category should ideally exist."),
                "tags_str": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. A comma-separated string of tags (e.g., 'python,ai,tutorial'). No spaces between tags and comma."),
                 "slug": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. A URL-friendly identifier."),
                "image_path": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Local file path to a featured image. Agent cannot use this."),
                "is_published": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Set to false for draft. Defaults to true."),
                "featured": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Set to true for featured. Defaults to false.")
            },
            required=["user_id", "title", "content"]
        )
    )

    user_post_comment_function = GenAiTypes.FunctionDeclaration(
        name="user_post_comment",
        description="Adds a new top-level comment to a specific post. Requires the user to be logged in.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the logged-in user posting the comment."),
                "post_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the post being commented on."),
                "content": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The text content of the comment.")
            },
            required=["user_id", "post_id", "content"]
        )
    )

    user_reply_comment_function = GenAiTypes.FunctionDeclaration(
        name="user_reply_comment",
        description="Adds a reply to an existing comment. Requires the user to be logged in.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the logged-in user posting the reply."),
                "post_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the post containing the comment thread."),
                "parent_comment_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the comment being replied to."),
                "content": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The text content of the reply.")
            },
            required=["user_id", "post_id", "parent_comment_id", "content"]
        )
    )

    user_like_post_function = GenAiTypes.FunctionDeclaration(
        name="user_like_post",
        description="Toggles (likes or unlikes) a specific post. Requires the user to be logged in.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the logged-in user performing the like/unlike action."),
                "post_slug": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The URL slug identifier of the post to like/unlike.")
            },
            required=["user_id", "post_slug"]
        )
    )

    get_post_details_function = GenAiTypes.FunctionDeclaration(
        name="get_post_details",
        description="Retrieves the full details for a single post using its unique slug. Does not require login.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "post_slug": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The URL slug identifier of the post to retrieve.")
            },
            required=["post_slug"]
        )
    )

    get_post_comments_function = GenAiTypes.FunctionDeclaration(
        name="get_post_comments",
        description="Retrieves all comments associated with a specific post using its ID. Does not require login.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "post_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the post whose comments are to be retrieved.")
            },
            required=["post_id"]
        )
    )

    list_categories_function = GenAiTypes.FunctionDeclaration(
        name="list_categories",
        description="Retrieves a list of available blog categories. Does not require login.",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Maximum number of categories to return."),
                "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Number of categories to skip for pagination.")
            },
            required=[]
        )
    )

    user_create_category_function = GenAiTypes.FunctionDeclaration(
        name="user_create_category",
        description="Creates a new blog category. Requires the user to be logged in and have admin privileges (enforced by the API).",
        parameters=GenAiTypes.Schema(
            type=GenAiTypes.Type.OBJECT,
            properties={
                "user_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the logged-in admin user creating the category."),
                "category_name": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The desired name for the new category.")
            },
            required=["user_id", "category_name"]
        )
    )

    blog_api_tools = GenAiTypes.Tool(
        function_declarations=[
            list_posts_function, list_users_function, register_function,
            user_login_function, user_logout_function, is_user_logged_in_function,
            user_create_post_function, user_post_comment_function, user_reply_comment_function,
            user_like_post_function, get_post_details_function, get_post_comments_function,
            list_categories_function, user_create_category_function,
        ]
    )
""")

# Indentation fixed for runner.py (Should be okay)
runner_py_content = dedent(r"""
    import os
    import random
    import time
    import threading
    import logging
    import datetime
    from queue import Queue, Empty
    from dotenv import load_dotenv

    from api import BlogApi, UserCredentials
    from agent import QuillpadAgent

    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash-latest")
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPRATURE", "0.8"))
    AGENT_LOG_FILE = "agent_activity.log"
    PRINT_LOG_TO_CONSOLE = True
    LOG_LEVEL_STR = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

    MIN_ACTIVE_SECONDS = 300
    MAX_ACTIVE_SECONDS = 600
    MIN_IDLE_SECONDS = 900
    MAX_IDLE_SECONDS = 3600
    ACTIONS_PER_BURST_MIN = 8
    ACTIONS_PER_BURST_MAX = 20
    DELAY_BETWEEN_ACTIONS_AVG = 15

    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger("SystemRunner")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.INFO)

    class SystemRunner:
        def __init__(self, min_active: int, max_active: int,
                     min_idle: int, max_idle: int):
            self.min_active = min_active
            self.max_active = max_active
            self.min_idle = min_idle
            self.max_idle = max_idle
            self.running = False
            self._main_thread: Optional[threading.Thread] = None
            self._stop_event = threading.Event()

            if not API_KEY: raise ValueError("API_KEY environment variable not set.")
            if not ADMIN_PASSWORD: log.warning("ADMIN_PASSWORD not set. Using default.")

            self.__blog_api = BlogApi(base_url=BASE_URL)
            self.__admin_credentials = UserCredentials(
                username=ADMIN_USERNAME, password=ADMIN_PASSWORD, email=ADMIN_EMAIL
            )
            self.__agent = QuillpadAgent(
                blog_instance=self.__blog_api, api_key=API_KEY, model_id=MODEL_NAME,
                admin_credentials=self.__admin_credentials, model_temperature=MODEL_TEMPERATURE,
                log_file=AGENT_LOG_FILE, print_log=PRINT_LOG_TO_CONSOLE
            )

        def start(self):
            if self.running: log.warning("Runner already running."); return
            log.info("Starting system runner...")
            self.running = True
            self._stop_event.clear()
            self._main_thread = threading.Thread(target=self._loop, daemon=True, name="SimulationLoop")
            self._main_thread.start()
            log.info("System runner thread started.")

        def stop(self):
            if not self.running and not self._stop_event.is_set(): return
            if self._stop_event.is_set(): log.info("Stop already requested."); return
            log.info("Requesting system runner stop...")
            self._stop_event.set()
            if self._main_thread and self._main_thread.is_alive():
                log.debug("Waiting for simulation loop thread to join...")
                self._main_thread.join(timeout=10)
                if self._main_thread.is_alive(): log.warning("Simulation loop thread did not exit gracefully.")
                else: log.info("Simulation loop thread joined.")
            self.running = False
            log.info("System runner stop process complete.")

        def _loop(self):
            log.info("Simulation loop starting.")
            while not self._stop_event.is_set():
                active_duration = random.randint(self.min_active, self.max_active)
                log.info(f"Starting active period ({active_duration} seconds)")
                start_active_time = time.monotonic()
                actions_in_burst = random.randint(ACTIONS_PER_BURST_MIN, ACTIONS_PER_BURST_MAX)
                log.info(f"Planning {actions_in_burst} actions.")

                for i in range(actions_in_burst):
                    if self._stop_event.is_set(): log.info("Stop signal during active burst."); break
                    log.info(f"--- Triggering Agent Action {i+1}/{actions_in_burst} ---")
                    try: self.__agent.trigger_action("Simulate the next logical user action on the blog.")
                    except Exception as e: log.exception(f"Error during agent trigger_action: {e}"); time.sleep(5)
                    if self._stop_event.is_set(): break

                    delay = random.expovariate(1.0 / DELAY_BETWEEN_ACTIONS_AVG)
                    elapsed_time = time.monotonic() - start_active_time
                    remaining_time = active_duration - elapsed_time
                    actual_delay = min(delay, max(0, remaining_time - 0.5))
                    log.debug(f"Action {i+1}/{actions_in_burst} processed. Wait {actual_delay:.2f}s...")
                    interrupted = self._stop_event.wait(timeout=actual_delay)
                    if interrupted: log.info("Stop signal during active delay."); break
                    if time.monotonic() - start_active_time >= active_duration: log.info("Active duration reached."); break

                if self._stop_event.is_set(): break
                idle_duration = random.randint(self.min_idle, self.max_idle)
                log.info(f"Entering idle period ({idle_duration} seconds)")
                interrupted = self._stop_event.wait(timeout=idle_duration)
                if interrupted: log.info("Stop signal during idle period."); break

            log.info("Simulation loop finished.")
            self.running = False

    if __name__ == "__main__":
        print("--- QuillPad Agent Simulation Runner ---")
        try:
            log_dir = os.path.dirname(AGENT_LOG_FILE)
            if log_dir and not os.path.exists(log_dir): os.makedirs(log_dir)
            with open(AGENT_LOG_FILE, 'w', encoding='utf-8') as f:
                f.write(f"--- Simulation Log Started: {datetime.datetime.now().isoformat()} ---\n")
            log.info(f"Initialized log file: {AGENT_LOG_FILE}")
        except IOError as e:
             log.error(f"Could not initialize log file {AGENT_LOG_FILE}: {e}")
             print(f"ERROR: Could not write log file {AGENT_LOG_FILE}.")

        try:
            runner = SystemRunner( MIN_ACTIVE_SECONDS, MAX_ACTIVE_SECONDS, MIN_IDLE_SECONDS, MAX_IDLE_SECONDS )
            runner.start()
        except ValueError as e: print(f"ERROR: Config error - {e}"); log.critical(f"Config error: {e}"); exit(1)
        except Exception as e: print(f"ERROR: Failed init - {e}"); log.critical(f"Init error: {e}", exc_info=True); exit(1)

        try:
            while runner.running: time.sleep(1)
            log.info("Runner not running. Main thread exit.")
        except KeyboardInterrupt: print("\nCtrl+C received."); log.info("KeyboardInterrupt.")
        except Exception as e: log.exception(f"Main loop error: {e}")
        finally:
            log.info("Initiating shutdown...")
            if 'runner' in locals() and runner: runner.stop()
            log.info("Shutdown complete.")
            print("Agent stopped.")
""")

requirements_txt_content = dedent("""
    google-generativeai>=0.5.0
    requests>=2.25.0
    python-dotenv>=0.15.0
""")

# --- Script to Write Files ---

file_map = {
    ".env": env_content,
    "api.py": api_py_content,
    "agent.py": agent_py_content,
    "api_desc.py": api_desc_py_content,
    "runner.py": runner_py_content,
    "requirements.txt": requirements_txt_content,
    "agent_activity.log": f"--- Log Initialized: {datetime.datetime.now().isoformat()} ---\n",
}

print("--- Writing Project Files (Syntax/Indent Corrected) ---")

for file_path, content in file_map.items():
    try:
        ensure_dir(file_path)
        # Write content directly after dedent, ensure newline
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")
        print(f"[OK] Wrote {file_path}")
    except IOError as e:
        print(f"[ERROR] Writing {file_path}: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error writing {file_path}: {e}")

print("\n--- Setup Instructions ---")
print("1. Review and update `.env`:")
print("   - Replace `YOUR_GOOGLE_API_KEY_HERE` with your actual Google GenAI API key.")
print("   - Verify `BASE_URL` points to your running QuillPad backend API.")
print("   - Check `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`.")
print("2. Install dependencies:")
print("   pip install -r requirements.txt")
print("3. Ensure Backend Running:")
print(f"   Make sure your QuillPad backend is running and accessible at the BASE_URL ({os.getenv('BASE_URL', 'Not Set')}).")
print("4. Run the Simulation:")
print("   python runner.py")
print("5. Monitor Logs:")
print("   Check the console output and the `agent_activity.log` file.")
print("6. Stop Simulation:")
print("   Press Ctrl+C in the terminal where `runner.py` is running.")
print("--- Script Finished ---")