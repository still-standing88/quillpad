from google.genai import types

list_posts_function = types.FunctionDeclaration(
    name="list_posts",
    description="Retrieves a list of blog posts from the API. Can specify the number of posts to retrieve and an offset for pagination.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "limit": {
                "type": "INTEGER",
                "description": "The maximum number of posts to return. Defaults to 10."
            },
            "offset": {
                "type": "INTEGER",
                "description": "The number of posts to skip before starting to collect the result set. Defaults to 0."
            }
        }
    }
)

list_users_function = types.FunctionDeclaration(
    name="list_users",
    description="Retrieves a list of locally stored registered users. Note: This function returns user information including username and email, but not passwords.",
    parameters={
        "type": "OBJECT",
        "properties": {} # No parameters required
    }
)

register_function = types.FunctionDeclaration(
    name="register",
    description="Registers a new user with a username, email, and password via the API.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "username": {
                "type": "STRING",
                "description": "The desired username for the new user."
            },
            "email": {
                "type": "STRING",
                "description": "The email address for the new user."
            },
            "password": {
                "type": "STRING",
                "description": "The password for the new user."
            }
        },
        "required": ["username", "email", "password"]
    }
)

user_login_function = types.FunctionDeclaration(
    name="user_login",
    description="Logs in the user associated with the given user ID. Requires a user with the given ID to be registered locally.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user to log in."
            }
        },
        "required": ["user_id"]
    }
)

user_logout_function = types.FunctionDeclaration(
    name="user_logout",
    description="Logs out the user associated with the given user ID.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user to log out."
            }
        },
        "required": ["user_id"]
    }
)

# New Function Declaration for checking login status
is_user_logged_in_function = types.FunctionDeclaration(
    name="is_user_logged_in",
    description="Checks if the user associated with the given user ID is currently logged in.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user to check the login status for."
            }
        },
        "required": ["user_id"]
    }
)


user_create_post_function = types.FunctionDeclaration(
    name="user_create_post",
    description="Creates a new blog post for a logged-in user. Requires user ID, title, content, and category. Other fields like tags_str are optional.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user creating the post. Must be logged in."
            },
            "title": {
                "type": "STRING",
                "description": "The title of the blog post."
            },
            "content": {
                "type": "STRING",
                "description": "The main content of the blog post (Markdown format recommended)."
            },
            "category": {
                "type": "STRING",
                "description": "The category name the post belongs to (must exist)."
            },
            "tags_str": {
                "type": "STRING",
                "description": "Required: A comma-separated string of tags for the post (e.g., 'python,api,tutorial')."
            },
            "slug": {
                "type": "STRING",
                "description": "A URL-friendly slug for the post. Optional, API might generate if omitted."
            },
            "image_path": {
                "type": "STRING",
                "description": "Optional: The local file path to a featured image for the post."
            },
            "is_published": {
                "type": "BOOLEAN",
                "description": "Whether the post should be published immediately. Defaults to true."
            },
            "featured": {
                "type": "BOOLEAN",
                "description": "Whether the post should be marked as featured. Defaults to false."
            }
        },
        "required": ["user_id", "title", "content", "category"]
    }
)

user_post_comment_function = types.FunctionDeclaration(
    name="user_post_comment",
    description="Posts a new top-level comment on a specific blog post for a logged-in user.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user posting the comment. Must be logged in."
            },
            "post_id": {
                "type": "INTEGER",
                "description": "The ID of the post to comment on."
            },
            "content": {
                "type": "STRING",
                "description": "The content of the comment."
            }
        },
        "required": ["user_id", "post_id", "content"]
    }
)

user_reply_comment_function = types.FunctionDeclaration(
    name="user_reply_comment",
    description="Posts a reply to an existing comment on a blog post for a logged-in user.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user posting the reply. Must be logged in."
            },
            "post_id": {
                "type": "INTEGER",
                "description": "The ID of the post the comment belongs to."
            },
            "parent_comment_id": {
                "type": "INTEGER",
                "description": "The ID of the comment being replied to."
            },
            "content": {
                "type": "STRING",
                "description": "The content of the reply."
            }
        },
        "required": ["user_id", "post_id", "parent_comment_id", "content"]
    }
)

user_like_post_function = types.FunctionDeclaration(
    name="user_like_post",
    description="Toggles the like status (likes or unlikes) for a specific blog post for a logged-in user.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user liking/unliking the post. Must be logged in."
            },
            "post_slug": {
                "type": "STRING",
                "description": "The slug of the post to like/unlike."
            }
        },
        "required": ["user_id", "post_slug"]
    }
)

get_post_details_function = types.FunctionDeclaration(
    name="get_post_details",
    description="Retrieves the full details of a specific blog post using its slug.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "post_slug": {
                "type": "STRING",
                "description": "The slug of the post to retrieve details for."
            }
        },
        "required": ["post_slug"]
    }
)

get_post_comments_function = types.FunctionDeclaration(
    name="get_post_comments",
    description="Retrieves all comments for a specific blog post using its ID.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "post_id": {
                "type": "INTEGER",
                "description": "The ID of the post to retrieve comments for."
            }
        },
        "required": ["post_id"]
    }
)

list_categories_function = types.FunctionDeclaration(
    name="list_categories",
    description="Retrieves a list of all available blog categories from the API.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "limit": {
                "type": "INTEGER",
                "description": "The maximum number of categories to return. Defaults to 1000."
            },
            "offset": {
                "type": "INTEGER",
                "description": "The number of categories to skip. Defaults to 0."
            }
        }
    }
)

user_create_category_function = types.FunctionDeclaration(
    name="user_create_category",
    description="Creates a new blog category. Requires the user to be logged in and have admin privileges (API enforced).",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {
                "type": "INTEGER",
                "description": "The ID of the user creating the category. Must be logged in (and assumed admin)."
            },
            "category_name": {
                "type": "STRING",
                "description": "The name for the new category."
            }
        },
        "required": ["user_id", "category_name"]
    }
)


# Updated Tool definition including all functions
blog_api_tools = types.Tool(
    function_declarations=[
        list_posts_function,
        list_users_function,
        register_function,
        user_login_function,
        user_logout_function,
        is_user_logged_in_function,
        user_create_post_function,
        user_post_comment_function,
        user_reply_comment_function,
        user_like_post_function,
        get_post_details_function,
        get_post_comments_function,
        list_categories_function,
        user_create_category_function,
    ]
)