from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import traceback

from app.core.utils import parse_github_repo_url, is_github_token_valid
from app.api.github import get_repo_metadata, get_all_files
from app.core.Baseai_checker import AIMetadataFileFinder
from app.core.Pyfiles_checker import PyCodeReviewer
from app.core.naturallang import Naturallangoutput
from app.core.Additionalfunc import Atomic_commits,BranchPRReview
import markdown
import json
app = FastAPI()

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    print("⚡️ / route hit")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/review", response_class=HTMLResponse)
async def review_repo(request: Request, repo_url: str = Form(...), gh_token: str = Form(...)):
    try:
        user, repo = parse_github_repo_url(repo_url)
        user, repo = parse_github_repo_url(repo_url)
        ans = is_github_token_valid(gh_token)
        if not ans:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Invalid or expired GitHub token. Please check and try again."
            })
        meta = get_repo_metadata(user, repo, token=gh_token)
        branch = meta["default_branch"]
        all_files = get_all_files(user, repo, branch, token=gh_token)
        py_files = [f for f in all_files if f.endswith(".py")]

        # Pass gh_token to all functions that require GitHub API access
        meta_results = AIMetadataFileFinder.run_full_metadata_check(all_files, user, repo, branch,token=gh_token)
        py_results = PyCodeReviewer.review_files(py_files, user, repo, branch,token=gh_token)
        commit_results = Atomic_commits.commit_reviewer(user, repo, branch,token=gh_token)
        pr_results = BranchPRReview.review_prs_best_practices(user, repo,token=gh_token)
        all_results = meta_results + py_results + commit_results + pr_results
        # Generate natural-language summary
        summary = Naturallangoutput.output(all_results)
        markdown_summary_raw = Naturallangoutput.markdown_output(all_results)
        markdown_summary = markdown.markdown(markdown_summary_raw, extensions=["tables"])
        
        if isinstance(summary, str):
            try:
                summary = json.loads(summary)
            except Exception:
                summary = {"summary": summary}

        return templates.TemplateResponse("results.html", {
            "request": request,
            "repo_url": repo_url,
            "summary": summary,
            "markdown_summary": markdown_summary,
        })
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
        })
