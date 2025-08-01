import re
import os
from typing import List, Dict, Optional
import requests

def parse_github_repo_url(repo_url: str):

    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, repo_url)
    if not match:
        raise ValueError("Invalid Github repo URL format.")
    return match.group(1), match.group(2)


def is_github_token_valid(token: str):
    """
    Checks if a GitHub token is valid by calling the /user endpoint.
    Returns True if valid, else returns False.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    response = requests.get("https://api.github.com/user", headers=headers)
    return response.status_code == 200



def is_in_root(all_files: List[str], filename: Optional[str]) -> bool:
        """Return True if the filename exists at the root (not in a subdirectory)."""
        if not filename:
            return False
        candidates = [f for f in all_files if os.path.basename(f).lower() == filename.lower()]
        return any("/" not in f and "\\" not in f for f in candidates)
    