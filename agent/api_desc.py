# File: api_desc.py

from google.genai import types as GenAiTypes

# --- Tool Function Declarations for BlogApi ---

# == Content Retrieval (Public) ==

get_posts_function = GenAiTypes.FunctionDeclaration(
    name="get_posts",
    description="Retrieves a paginated list of blog posts. Can filter by various criteria. Does not require login.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Max posts per page."),
            "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Posts to skip for pagination."),
            "category": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Filter by category ID."),
            "author_username": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Filter by author's username."),
            "tags": GenAiTypes.Schema(type=GenAiTypes.Type.ARRAY, items=GenAiTypes.Schema(type=GenAiTypes.Type.STRING), description="Optional. Filter by posts containing ALL specified tag names."), # Updated type, adjusted description for likely GET param handling
            "is_published": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Filter by published status."),
            "featured": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Filter for featured posts."),
            "created_after": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Filter posts created after this ISO date string."),
            "created_before": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Filter posts created before this ISO date string."),
            "search": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Search term for post title or content."),
            "ordering": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Field to order by (e.g., 'created_at', '-view_count').")
        },
        required=[]
    )
)

get_post_function = GenAiTypes.FunctionDeclaration(
    name="get_post",
    description="Retrieves the full details for a single post using its unique slug. Does not require login.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "slug": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The URL slug identifier of the post to retrieve.")
        },
        required=["slug"]
    )
)

get_comments_by_post_function = GenAiTypes.FunctionDeclaration(
    name="get_comments_by_post",
    description="Retrieves comments associated with a specific post using its ID. Supports pagination. Does not require login.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "post_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="The ID of the post whose comments are to be retrieved."),
            "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Max comments per page."),
            "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Comments to skip for pagination.")
        },
        required=["post_id"]
    )
)

get_categories_function = GenAiTypes.FunctionDeclaration(
    name="get_categories",
    description="Retrieves a list of available blog categories. Supports pagination. Does not require login.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Maximum number of categories to return."),
            "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Number of categories to skip for pagination.")
        },
        required=[]
    )
)

get_tags_function = GenAiTypes.FunctionDeclaration(
    name="get_tags",
    description="Retrieves a list of available blog tags. Supports pagination. Does not require login.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Maximum number of tags to return."),
            "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Number of tags to skip for pagination.")
        },
        required=[]
    )
)

# == User Authentication & Session ==

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

login_function = GenAiTypes.FunctionDeclaration(
    name="login",
    description="Logs in a previously registered user. Stores the authentication token internally within the API client instance upon success. Returns API response including user ID, token, username, role.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "username": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The username of the user trying to log in."),
            "password": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The password for the user.")
        },
        required=["username", "password"]
    )
)

logout_function = GenAiTypes.FunctionDeclaration(
    name="logout",
    description="Logs out the currently authenticated user by clearing the internally stored token within the API client instance and attempting to call the API's logout endpoint (which may fail with 404).", # Updated description for potential failure
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={},
        required=[]
    )
)


change_password_function = GenAiTypes.FunctionDeclaration(
    name="change_password",
    description="Changes the password for the currently logged-in user (using the internally stored token). Automatically logs the user out (clears the internal token) upon success.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "current_password": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The user's current password."),
            "new_password": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The desired new password.")
        },
        required=["current_password", "new_password"]
    )
)


# == Authenticated User Actions ==

create_post_function = GenAiTypes.FunctionDeclaration(
    name="create_post",
    description="Creates a new blog post. Requires the user to be logged in (uses internally stored token). Tags must be provided as a list of strings.", # Updated description
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "title": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The title of the blog post."),
            "content": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The main content of the post."),
            "category": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. Name of an existing category."),
            "tags": GenAiTypes.Schema(type=GenAiTypes.Type.ARRAY, items=GenAiTypes.Schema(type=GenAiTypes.Type.STRING), description="Required. A list of tag strings (e.g., ['python', 'api'])."), # Updated type and description
            "is_published": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Defaults to true."),
            "featured": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Defaults to false.")
        },
        required=["title", "content", "tags"] # Added tags to required
    )
)

create_comment_function = GenAiTypes.FunctionDeclaration(
    name="create_comment",
    description="Adds a new comment or replies to an existing comment on a post. Requires the user to be logged in (uses internally stored token). Provide parent_id to reply.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "post_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="ID of the post to comment on."),
            "content": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="The comment text."),
            "parent_id": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. ID of the comment being replied to. If omitted, creates a top-level comment.")
        },
        required=["post_id", "content"]
    )
)

like_post_function = GenAiTypes.FunctionDeclaration(
    name="like_post",
    description="Toggles (likes or unlikes) a specific post. Requires the user to be logged in (uses internally stored token).",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "slug": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Slug of the post.")
        },
        required=["slug"]
    )
)

get_profile_function = GenAiTypes.FunctionDeclaration(
    name="get_profile",
    description="Retrieves the profile details (bio, avatar URL, etc.) for the currently logged-in user (uses internally stored token).",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={},
        required=[]
    )
)

update_profile_function = GenAiTypes.FunctionDeclaration(
    name="update_profile",
    description="Updates the profile bio for the currently logged-in user (uses internally stored token). Avatar update is not supported via this agent.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "bio": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. The new bio text.")
        },
        required=[]
    )
)

# == Admin Actions ==

get_users_function = GenAiTypes.FunctionDeclaration(
    name="get_users",
    description="Retrieves a paginated list of ALL registered users. Requires ADMIN privileges for the currently logged-in user (uses internally stored token).",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "limit": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Max users per page."),
            "offset": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="Optional. Starting offset.")
        },
        required=[]
    )
)

create_category_function = GenAiTypes.FunctionDeclaration(
    name="create_category",
    description="Creates a new category. Requires ADMIN privileges for the currently logged-in user (uses internally stored token).",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "name": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Name for the new category.")
        },
        required=["name"]
    )
)

update_user_function = GenAiTypes.FunctionDeclaration(
    name="update_user",
    description="Updates specified account fields for a target user (username, email, role, status). Requires ADMIN privileges for the currently logged-in user (uses internally stored token). Use update_profile for the user's own bio/avatar.",
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "user_id_to_update": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="ID of the user account being updated."),
            "username": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. New unique username."),
            "email": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. New unique email."),
            "role": GenAiTypes.Schema(type=GenAiTypes.Type.STRING, description="Optional. New role ('admin', 'editor', 'author', 'reader')."),
            "is_staff": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Staff status (grants admin access)."),
            "is_active": GenAiTypes.Schema(type=GenAiTypes.Type.BOOLEAN, description="Optional. Active status (allows login).")
        },
        required=["user_id_to_update"]
    )
)

delete_user_function = GenAiTypes.FunctionDeclaration(
    name="delete_user",
    description="Attempts to delete a specified user account. Requires ADMIN privileges for the currently logged-in user (uses internally stored token). This may fail if the backend endpoint is not configured for DELETE.", # Updated description
    parameters=GenAiTypes.Schema(
        type=GenAiTypes.Type.OBJECT,
        properties={
            "user_id_to_delete": GenAiTypes.Schema(type=GenAiTypes.Type.INTEGER, description="ID of the user account to be deleted.")
        },
        required=["user_id_to_delete"]
    )
)


# --- Tool Definition (List of all function declarations) ---
blog_api_tools = GenAiTypes.Tool(
    function_declarations=[
        # Public Read
        get_posts_function,
        get_post_function,
        get_comments_by_post_function,
        get_categories_function,
        get_tags_function,
        # User Auth/Action
        register_function,
        login_function,
        logout_function,
        change_password_function,
        create_post_function,
        create_comment_function,
        like_post_function,
        get_profile_function,
        update_profile_function,
        # Admin Actions
        get_users_function,
        create_category_function,
        update_user_function,
        delete_user_function,
    ]
)