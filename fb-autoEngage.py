#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
import requests
from facepy import GraphAPI
import configparser
import json
import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit

config_file = 'fb_config.ini'
comments_file = 'comments.json'


class MainWindow(QMainWindow):
    def __init__(self, sections):
        super().__init__()

        self.setWindowTitle("Facebook Post Upload")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        access_token_label = QLineEdit()
        access_token_label.setPlaceholderText("Access Token")
        layout.addWidget(access_token_label)
        self.access_token_label = access_token_label

        post_ids_label = QLineEdit()
        post_ids_label.setPlaceholderText("Post IDs (comma-separated)")
        layout.addWidget(post_ids_label)
        self.post_ids_label = post_ids_label

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.handle_submit)
        layout.addWidget(submit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.sections = sections
        self.post_ids = []

    def handle_submit(self):
        access_token = self.access_token_label.text()
        post_ids_input = self.post_ids_label.text()
        post_ids = [post_id.strip() for post_id in post_ids_input.split(",")]

        print(f"Access Token: {access_token}")
        print(f"Post IDs: {post_ids}")

        def post_likes(access_token_entry, post_ids, sections):
            access_token = access_token_entry.strip()

            fb = FbPageAPI(access_token)
            for index, section in enumerate(sections):
                page_info = config_section_map(section)
                # get page token
                page_access_token = fb.get_page_access_token(_page_id=page_info['page_id'])
                fb.get_likes_on_posts(access_token=page_access_token, post_ids=post_ids)

        def share_post(access_token_entry, post_ids, sections):
            access_token = access_token_entry.strip()

            fb = FbPageAPI(access_token)
            for index, section in enumerate(sections):
                page_info = config_section_map(section)
                # get page token
                page_access_token = fb.get_page_access_token(_page_id=page_info['page_id'])
                fb.share_posts(access_token=page_access_token, post_ids=post_ids)

        def post_comments(access_token_entry, post_ids, sections):
            access_token = access_token_entry.strip()

            fb = FbPageAPI(access_token)
            file = open(comments_file)
            comments = json.load(file)['comments']
            for index, section in enumerate(sections):
                page_info = config_section_map(section)
                # get page token
                page_access_token = fb.get_page_access_token(_page_id=page_info['page_id'])
                fb.get_comments_on_posts(access_token=page_access_token, post_ids=post_ids, comments=comments)

        post_likes(access_token,post_ids,self.sections)
        post_comments(access_token,post_ids,self.sections)
        share_post(access_token,post_ids,self.sections)

class FbPageAPI:
    def __init__(self, _access_token, limit=250):
        self.access_token = _access_token
        self.graph = GraphAPI(self.access_token)
        self.accounts = self._get_accounts(limit)

    def _get_accounts(self, limit=250):
        self.accounts = self.graph.get('me/accounts?limit=' + str(limit))
        return self.accounts['data']

    def get_accounts(self):
        return self.accounts['data']

    def get_page_access_token(self, _page_id):
        """
            :param _page_id:
            :return: page_specific_token
        """
        for data in self.accounts:
            if _page_id == data['id']:
                _page_access_token = data['access_token']
                # print('access_token: ', _page_access_token)
                print('')
                print('Page id: ', data['id'])
                print('Page Name: ', data['name'])
                return _page_access_token
        else:
            return None

    @staticmethod
    def get_comments_on_posts(access_token, post_ids, comments):
        for post_id in post_ids:
            url = f"https://graph.facebook.com/v12.0/{post_id}/comments"
            params = {
                "access_token": access_token,
                "message": random.choice(comments)
            }
            response = requests.post(url, params=params)
            if response.status_code == 200:
                print(f"Successfully commented on post {post_id}")
            else:
                print(f"Failed to comment on post {post_id}. Error: {response.text}")

    @staticmethod
    def get_likes_on_posts(access_token, post_ids):
        for post_id in post_ids:
            url = f"https://graph.facebook.com/v12.0/{post_id}/likes"
            params = {
                "access_token": access_token,
            }
            response = requests.post(url, params=params)
            if response.status_code == 200:
                print(f"Successfully liked post {post_id}")
            else:
                print(f"Failed to like post {post_id}. Error: {response.text}")

    @staticmethod
    def share_posts(access_token, post_ids):
        for post_id in post_ids:
            endpoint = f'/me/feed'
            # Create the post data
            data = {
                'link': f'https://www.facebook.com/{post_id}'
            }
            # Make the POST request to share the post
            url = f'https://graph.facebook.com/v13.0{endpoint}?access_token={access_token}'
            response = requests.post(url, data=data)
            # Check the response
            if response.status_code == 200:
                print('Post shared successfully!')
            else:
                print('Error sharing post:', response.json())

if __name__ == '__main__':
    config = configparser.ConfigParser()

    config.read(config_file)
    # get sections
    sections = config.sections()
    print('Config sections - ', sections)

    def config_section_map(_section):
        dict1 = {}
        options = config.options(_section)
        for option in options:
            try:
                dict1[option] = config.get(_section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    app = QApplication(sys.argv)
    window = MainWindow(sections)
    window.show()
    sys.exit(app.exec_())