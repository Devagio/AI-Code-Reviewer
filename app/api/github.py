import requests

def github_headers(token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def get_repo_metadata(user, repo, token=None):
    url = f"https://api.github.com/repos/{user}/{repo}"
    r = requests.get(url, headers=github_headers(token))
    r.raise_for_status()
    data = r.json()
    return {
        "user": data['owner']['login'],
        "repo_name": data['name'],
        "license": data['license']['spdx_id'] if data.get('license') else None,
        "default_branch": data['default_branch'],
        "description": data.get('description', ''),
    }

def get_all_files(user, repo, branch="main", token=None):
    url = f"https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(url, headers=github_headers(token))
    r.raise_for_status()
    tree = r.json()['tree']
    all_files = [item['path'] for item in tree if item['type'] == 'blob']
    return all_files

def get_file_content(user, repo, path, branch="main", token=None):
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
    headers = github_headers(token)
    # For raw.githubusercontent.com, token is NOT used, but for private repos use API endpoint
    if token:
        api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}?ref={branch}"
        r = requests.get(api_url, headers=headers)
        if r.status_code == 200:
            return r.text
    else:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
    return None 


def get_all_python_files(user, repo, branch="main", token=None):
    all_files = get_all_files(user, repo, branch, token)
    py_files = [f for f in all_files if f.endswith(".py")]
    return py_files
