import requests 
from typing import List, Dict, Optional
from app.api.ai_review import ask_chatgpt
from app.core.prompts import ATOMIC_Commits, PR_PROMPT
from jinja2 import Template
import json

class Atomic_commits:
    @staticmethod
    def get_commits(user: str, repo: str, branch: str, per_page: int = 10, max_commits: int = 50, token: str = None) -> List[Dict]:
        commits_info = []
        url = f"https://api.github.com/repos/{user}/{repo}/commits"
        params = {"sha": branch, "per_page": per_page, "page": 1}
        headers = {"Authorization": f"token {token}"} if token else {}
        fetched = 0
        while True:
            r = requests.get(url, params=params, headers=headers)
            r.raise_for_status()
            commits = r.json()
            if not commits:
                break
            for commit in commits:
                sha = commit["sha"]
                message = commit["commit"]["message"]
                # Get commit details for files/lines changed
                details_url = f"https://api.github.com/repos/{user}/{repo}/commits/{sha}"
                details_r = requests.get(details_url, headers=headers)
                details_r.raise_for_status()
                details = details_r.json()
                files_changed = len(details.get("files", []))
                lines_changed = sum(f.get("additions", 0) + f.get("deletions", 0) for f in details.get("files", []))
                commits_info.append({
                    "commit_id": sha,
                    "files_changed": files_changed,
                    "lines_changed": lines_changed,
                    "commit_message": message
                })
                fetched += 1
                if fetched >= max_commits:
                    return commits_info
            params["page"] += 1
        return commits_info

    @staticmethod
    def commit_reviewer(user: str, repo: str, branch: str, per_page: int = 10, max_commits: int = 50, token: str = None) -> List[Dict]:
        # Fetch commits inside the reviewer
        commits_info = Atomic_commits.get_commits(user, repo, branch, per_page, max_commits, token)
        reviewed = []
        for commit in commits_info:
            msg = commit.get("commit_message", "")
            prompt = Template(ATOMIC_Commits).render(commit_msg=msg)
            try:
                review = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
            except Exception as e:
                review = f"Error in AI review: {e}"

            # Files changed review
            if commit["files_changed"] > 3:
                files_review = "More than 3 files changed. For clarity and easier code review, try to keep each commit to 3 files or less."
            else:
                files_review = "Good job! Number of files changed is within the recommended limit."

            # Review number of lines changed
            if commit["lines_changed"] > 300:
                lines_review = "More than 300 lines changed. For clarity and easier debugging, try to keep commits under 300 lines."
            else:
                lines_review = "Good job! Number of lines changed is within the recommended limit."

            reviewed.append({
                "commit_id": commit["commit_id"],
                "commit_msg_review": review,
                "files_changed_review": files_review,
                "lines_changed_review": lines_review
            })
        return reviewed


class BranchPRReview:
    @staticmethod
    def get_pull_requests(user: str, repo: str, token: str = None) -> List[Dict]:
        url = f"https://api.github.com/repos/{user}/{repo}/pulls?state=all"
        headers = {"Authorization": f"token {token}"} if token else {}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def review_prs_best_practices(user: str, repo: str, token: str = None) -> List[Dict]:
        prs = BranchPRReview.get_pull_requests(user, repo, token)
        results = []

        if not prs:
            results.append({"pr": "No Pull Requests found."})
        elif len(prs) > 20:
            results.append({"pr": "Way too many Pull Requests found. (>20)"})
        else:
            for pr in prs:
                title = pr.get('title', '')
                body = pr.get('body', '') or ''
                prompt = Template(PR_PROMPT).render(title=title, body=body)
                try:
                    ai_json = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
                    try:
                        ai_json = json.loads(ai_json)
                    except Exception as e:
                        ai_json = {
                            "title_review": "AI response was not valid JSON.",
                            "description_review": str(e)
                        }
                except Exception as e:
                    review = {
                        "title_review": "Error in AI review.",
                        "description_review": str(e)
                    }

                results.append({
                    "pr_title": title,
                    "title_review": ai_json.get("title_review", ""),
                    "description_review": ai_json.get("description_review", "")
                })
        return results

