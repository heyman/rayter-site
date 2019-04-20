from github import Github
from github import InputGitTreeElement
from os import path
from settings import RAYTER_GITHUB_TOKEN
from time import strftime


def update(repo_path, file_name, content, commit_message):
    g = Github(RAYTER_GITHUB_TOKEN)
    repo = g.get_repo(repo_path)
    master_ref = repo.get_git_ref("heads/master")
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    element_list = list()
    element = InputGitTreeElement(file_name, "100644", "blob", content)
    element_list.append(element)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)


if __name__ == "__main__":
    noop
#         update("my-test", "/mnt/c/Users/peter/tmp/test.txt", strftime("%H:%M:%S"))
