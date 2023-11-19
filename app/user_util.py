#!/usr/bin/env python3

import argparse
import getpass
import yaml
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import Flask
import os


# User class
class User(UserMixin):
	def __init__(self, username, password_hash):
		self.username = username
		self.id = self.username
		self.password_hash = password_hash

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	@staticmethod
	def create(username, password):
		password_hash = generate_password_hash(password)
		return User(username, password_hash)


# UserStorage class
class UserStorage:
	_this_dir = os.path.dirname(os.path.abspath(__file__))
	_default_config = os.path.join(_this_dir, 'user_db_config.yaml')
	def __init__(self, cfg=None):
		if isinstance(cfg, Flask):
			self.config_yaml = cfg.config['USER_DB_CONFIG']
		else:
			self.config_yaml = cfg
		if cfg is None:
			self.config_yaml = self._default_config
		with open(self.config_yaml, 'r') as f:
			self.config = yaml.safe_load(f) or {'file': 'users.yaml'}
		self.yaml_file = self.config['file'].replace("{{thisdir}}", self._this_dir)
		self.users = self.load_users()

	def load_users(self):
		try:
			with open(self.yaml_file, 'r') as file:
				users_data = yaml.safe_load(file) or {}
				return {username: User(username, data['password_hash'])
						for username, data in users_data.items()}
		except FileNotFoundError:
			return {}

	def save_users(self):
		with open(self.yaml_file, 'w') as file:
			users_data = {user.id: {'password_hash': user.password_hash}
						  for user in self.users.values()}
			yaml.dump(users_data, file)

	def add_user(self, username, password):
		user = User.create(username, password)
		self.users[username] = user
		self.save_users()

	def get_user(self, user_id):
		return self.users.get(user_id)

	def check_user(self, username, password):
		user = self.users.get(username)
		if user and check_password_hash(user.password_hash, password):
			return True
		return False

	def delete_user(self, username):
		if username in self.users:
			del self.users[username]
			self.save_users()
			return True
		return False

	def update_password(self, username, new_password):
		if username in self.users:
			self.users[username].password_hash = generate_password_hash(new_password)
			self.save_users()
			return True
		return False

# Command line arguments handling
def parse_args():
	parser = argparse.ArgumentParser(description="Manage users.")
	parser.add_argument('--add', help="Add a new user", action="store_true")
	parser.add_argument('--check', help="Check if a user exists", action="store_true")
	parser.add_argument('--delete', help="Delete a user", action="store_true")
	parser.add_argument('--change-password', help="Change a user's password", action="store_true")
	parser.add_argument('username', nargs='?', help="Username for the user")
	return parser.parse_args()

# Main function
def main():
	args = parse_args()
	storage = UserStorage()

	if args.add:
		if args.username is None:
			print("Please specify a username to add.")
			return
		password = getpass.getpass("Enter new password for {}: ".format(args.username))
		storage.add_user(args.username, password)
		print(f"User '{args.username}' added successfully.")

	elif args.check:
		if args.username is None:
			print("Please specify a username to check.")
			return
		password = getpass.getpass(f"Enter password for {args.username}: ")
		user_exists = storage.check_user(args.username, password)
		if user_exists:
			print(f"User '{args.username}' exists and password is correct.")
		else:
			print(f"User '{args.username}' does not exist or password is incorrect.")

	elif args.delete:
		if args.username is None:
			print("Please specify a username to delete.")
			return
		deleted = storage.delete_user(args.username)
		if deleted:
			print(f"User '{args.username}' deleted successfully.")
		else:
			print(f"User '{args.username}' not found.")

	elif args.change_password:
		if args.username is None:
			print("Please specify a username to change the password.")
			return
		new_password = getpass.getpass(f"Enter new password for {args.username}: ")
		password_changed = storage.update_password(args.username, new_password)
		if password_changed:
			print(f"Password for '{args.username}' changed successfully.")
		else:
			print(f"User '{args.username}' not found.")

	else:
		print("No action specified. Use --add, --check, --delete, or --change-password.")

if __name__ == "__main__":
	main()
