from base64 import b64decode
from github import Github
from github import InputGitTreeElement
from github.GithubException import UnknownObjectException

from os import path
import settings
from time import strftime
from pprint import pprint
import logging


def get(repo_path, file_name):
    g = Github(settings.RAYTER_GITHUB_TOKEN)
    repo = g.get_repo(repo_path)
    try:
        file = repo.get_contents(file_name)
        content = file.content
        return b64decode(content)
    except UnknownObjectException as e:
        logging.error(e)
        return None


def update(repo_path, file_name, content, message):
    g = Github(settings.RAYTER_GITHUB_TOKEN)
    repo = g.get_repo(repo_path)
    master_ref = repo.get_git_ref("heads/master")
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    element_list = list()
    element = InputGitTreeElement(file_name, "100644", "blob", content)
    element_list.append(element)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(message, tree, [parent])
    master_ref.edit(commit.sha)


def update_game(file_name, content, message):
    repo_path = settings.RAYTER_GAMES_REPO
    return update(repo_path, file_name, content, message)


def get_game(file_name):
    repo_path = settings.RAYTER_GAMES_REPO
    return get(repo_path, file_name)


def update_metadata(file_name, content, message):
    repo_path = settings.RAYTER_METADATA_REPO
    return update(repo_path, file_name, content, message)


def get_metadata(file_name):
    repo_path = settings.RAYTER_METADATA_REPO
    return get(repo_path, file_name)
