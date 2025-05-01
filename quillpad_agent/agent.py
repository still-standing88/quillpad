from typing import Any
from dataclasses import asdict
from google.genai import Client
from google.genai import types
from api import BlogApi, UserInfo
from api_desc import blog_api_tools

import time
import datetime as dt

system_prompt = """
You've been given access to a blogging platform's api with a surtain number of functions that you can use. 
A system process will continuecely send you prompting requests at random intervals, your task is to respond with an action by using one of the provided tools. These actions include:
Registering new users.
logining and loggin out.
Creating posts (markdown content is supported)
Posting comments and responsing to those comments by replying.
Listing users.
Listing posts.

Your task, in addition to responding to the system calls, is to simulate the blog platform with content. Creating posts, and creating users that engage with that content. 
Include discussions in comments about that post topic, Articles, ... etc.
After each tool call, respond with a log message of the action taken, errors if any, and results of that action. 

Create users with convincing names and user information.
If you wish for a specific user to be an author, include a detail for that in the output you send back that would be logged after the function call. By default most newly registered users have the rank of a reader. An administrator will insure that user will be promoted an author. 
You mey list what users are available before creating new users. Offen there are some left over users from other tests for you to use. 
"""

class QuillpadAgent:


    def __init__(self, blog_instance:BlogApi, api_key:str, model_id:str, admin_user:UserInfo, model_temprature:float = 1.0, log_file="log_output.log", print_log:bool = False) -> None:
        self.__log_file = log_file
        self.__print_log = print_log
        self.__blog:BlogApi = blog_instance
        self.__api_function_map = {
        "list_posts": self.__blog.list_posts,
        "list_users": self.__blog.list_users,
        "register": self.__blog.register,
        "user_login": self.__blog.user_login,
        "user_logout": self.__blog.user_logout,
            "is_user_logged_in": self.__blog.is_user_logged_in,
        "user_create_post": self.__blog.user_create_post,
        "user_post_comment": self.__blog.user_post_comment,
        "user_reply_comment": self.__blog.user_reply_comment,
        "user_like_post": self.__blog.user_like_post,
        "get_post_details": self.__blog.get_post_details,
     "get_post_comments": self.__blog.get_post_comments,
     }

        self.__client = Client(api_key=api_key)

        self.__chat_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[blog_api_tools],
            temperature=model_temprature
        )
        self.__chat = self.__client.chats.create(
            model=model_id,
            config=self.__chat_config,
        )

        admin_user_exists = any(user.username == admin_user.username for user in self.__blog.users)
        if not admin_user_exists:
            self.__blog.add_user(admin_user)
        self.send_msg(self.system_message(f"Blog agent system launched.\nAdmin info{str(asdict(admin_user))}\nWhat action to take?"))

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
                    result = self.__api_function_map[func.name](**func.args)
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



