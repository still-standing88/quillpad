from typing import Any, Dict, List, Optional
from dataclasses import asdict # Kept for initial message if needed, but UserCredentials is gone
from google.genai import Client, types # Use direct import
from api import BlogApi
from api_desc import blog_api_tools # Assuming api_desc.py has ALL function declarations now

import time
import datetime as dt
import logging
import os

log = logging.getLogger("QuillpadAgent") # Use specific logger

# Use the detailed system prompt from previous corrections or your preferred one
system_prompt = """
You're a scifi fan and you like talking about all scifi stuff.
Create a user in the platform(some unique username), use admin user to upgrade it to an admin. Then write a few interesting aritcles using that very use. You can upgrade it to the rank of author and  do that. 
The session is a 1 user sesion only, so you'll have to logout and login if you'd like to perform such actions. Logout mey return 404 which you can ignore.
System will keap sending messages to prompt you for further actions. There are no human interactions in this chat. You're on your own.
"""

class QuillpadAgent:


    def __init__(self, blog_instance:BlogApi, api_key:str, model_id:str, admin_credentials:dict, model_temperature:float = 1.0, log_file="log_output.log", print_log:bool = False) -> None:
        self.__log_file = log_file
        self.__print_log = print_log
        self.__blog:BlogApi = blog_instance
        self.__api_function_map = {
            # Public Read
            "get_posts": self.__blog.get_posts,
            "get_post": self.__blog.get_post,
            "get_comments_by_post": self.__blog.get_comments_by_post,
            "get_categories": self.__blog.get_categories,
            "get_tags": self.__blog.get_tags,
            # User Auth/Action
            "register": self.__blog.register,
            "login": self.__blog.login,
            "logout": self.__blog.logout,
            # "is_user_logged_in": # Handled internally by checking self.__blog.sessions perhaps? Needs Agent logic.
            "change_password": self.__blog.change_password,
            "create_post": self.__blog.create_post,
            "create_comment": self.__blog.create_comment,
            "like_post": self.__blog.like_post,
            "get_profile": self.__blog.get_profile,
            "update_profile": self.__blog.update_profile,
             # Admin Actions
            "get_users": self.__blog.get_users,
            "create_category": self.__blog.create_category,
            "update_user": self.__blog.update_user,
            "delete_user": self.__blog.delete_user,
        }

        self.__client = Client(api_key=api_key)

        self.__chat_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[blog_api_tools],
            temperature=model_temperature
        )
        self.__chat = self.__client.chats.create(
            model=model_id,
            config=self.__chat_config,
        )

        #admin_credentials_exists = any(user.username == admin_credentials.username for user in self.__blog.users)
        #if not admin_credentials_exists:
            #self.__blog.add_user(admin_credentials)
        self.send_msg(self.system_message(f"Blog agent system launched.\nAdmin info{admin_credentials}\nWhat action to take?"))

    def system_message(self, contents:str):
        date = dt.datetime.now()
        return f"Date: {date}\n{contents}"

    def send_msg(self, content:Any):
        msg = self.system_message(content)

        response = self.send_chat_message(msg)
        contents = []

        if response.function_calls:
            for func in response.function_calls:
                if func.name in self.__api_function_map and func.args is not None:
                    result = self.__api_function_map[func.name](**func.args);time.sleep(3)
                    function_response_part = types.Part.from_function_response(
                        name=func.name,
                        response={"result": result}
                    )
                    contents.append(function_response_part)

        if len(contents) >0:
            response = self.send_chat_message(contents)

        try:
            if response.text:
                with open(self.__log_file, 'a') as fp:
                    print(response.text)
                    fp.write(response.text)
        except Exception as e:
            pass

    def send_chat_message(self, contents):
        while(True):
            try:
                response = self.__chat.send_message(contents)
                return response
            except Exception as e:
                time.sleep(5)
                print(f"Error {e}\nRetrying")



