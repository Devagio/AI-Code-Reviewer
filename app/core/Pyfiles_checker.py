from collections import OrderedDict
import json
from jinja2 import Template
from typing import List
from app.core.prompts import PYTHON_FILE_REVIEW_PROMPT
from app.api.github import get_file_content
from app.api.ai_review import ask_chatgpt

class PyCodeReviewer:
    @staticmethod
    def review_files(py_files: List[str], user: str,repo: str, branch: str, max_files=30, token=None) -> List[OrderedDict]:
        results = []
        if len(py_files) > max_files: return results

        for file_path in py_files:
            code = get_file_content(user, repo, file_path, branch,token=token)
            if not code or len(code.strip()) < 10:
                continue
            print(f"Reviewing {file_path} ...")
            prompt = Template(PYTHON_FILE_REVIEW_PROMPT).render(code=code)
            try:
                ai_json_str = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
                ai_json = json.loads(ai_json_str)
                output_json = OrderedDict()
                output_json["file"] = file_path
                output_json["comments"] = ai_json.get("comments", {})
                output_json["docstrings"] = ai_json.get("docstrings", {})
                output_json["function_modularity"] = ai_json.get("function_modularity", {})
            except Exception as e:
                output_json = OrderedDict()
                output_json["file"] = file_path
                output_json["comments"] = {
                    "status": "error", "suggestion": str(e)
                }
                output_json["docstrings"] = {
                    "overall": {"status": "error", "suggestion": str(e)},
                    "functions": {}
                }
                output_json["function_modularity"] = {
                    "status": "error", "suggestion": str(e)
                }
            results.append(output_json)
        return results
