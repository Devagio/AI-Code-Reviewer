from pydantic import BaseModel, HttpUrl, validator

class RepoReviewRequest(BaseModel):
    repo_url: HttpUrl

    @validator('repo_url')
    def github_url_only(cls, v):
        if "github.com" not in v:
            raise ValueError("URL must be from github.com")
        return v
