from typing import List, Dict, Optional
import json
from jinja2 import Template
import os
from collections import OrderedDict
from .prompts import files_identify, license_check_prompt, readme_check_prompt, requirements_check_prompt,PACKAGE_PROMPT
from app.api.ai_review import ask_chatgpt
from app.core.utils import is_in_root
from app.api.github import get_file_content

class AIMetadataFileFinder:

    @classmethod
    def find_metadata_files(cls, all_files: List[str]) -> Dict[str, Optional[str]]:
        prompt = Template(files_identify).render(files=all_files)
        ai_response = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
        try:
            result = json.loads(ai_response)
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI output: {ai_response}") from e
        return result

    @classmethod
    def check_license_file(cls, license_filename: str, user: str, repo: str, branch: str,token=None) -> dict:
        license_content = get_file_content(user, repo, license_filename, branch,token=token)
        prompt = Template(license_check_prompt).render(license_content=license_content)
        license_response = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
        try:
            license_result = json.loads(license_response)
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI output: {license_response}") from e
        return license_result

    @classmethod
    def check_readme_file(cls, readme_filename: str, user: str, repo: str, branch: str,token=None) -> dict:
        readme_content = get_file_content(user, repo, readme_filename, branch,token=token)
        prompt = Template(readme_check_prompt).render(readme_content=readme_content)
        readme_response = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
        try:
            readme_result = json.loads(readme_response)
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI output: {readme_response}") from e
        return readme_result
    

    @classmethod
    def check_requirements_file(cls, requirements_filename: str, user: str, repo: str, branch: str,token=None) -> dict:
        requirements_content = get_file_content(user, repo, requirements_filename, branch,token=token)
        prompt = Template(requirements_check_prompt).render(requirements_content=requirements_content)
        requirements_response = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
        try:
            requirements_result = json.loads(requirements_response)
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI output: {requirements_response}") from e
        return requirements_result
   
    @classmethod
    def check_other_package_files_with_ai(cls,all_files: List[str]):
        prompt = Template(PACKAGE_PROMPT).render(files=all_files)
        response = ask_chatgpt(prompt, model="gpt-4.1-nano-2025-04-14")
        return json.loads(response)


    @classmethod
    def run_full_metadata_check(cls, all_files: List[str], user: str, repo: str, branch: str, token=None) -> List[OrderedDict]:
        meta_files = cls.find_metadata_files(all_files)
        license_filename = meta_files.get('license')
        readme_filename = meta_files.get('readme')
        requirements_filename = meta_files.get('requirements')

        results = []
        response= cls.check_other_package_files_with_ai(all_files)
        results.append(response)

        # LICENSE
        if license_filename is None:
            results.append({
                "file_type": "license",
                "result": "No such file found"
            })
        else:
            license_in_root = is_in_root(all_files, license_filename)
            license_result = cls.check_license_file(license_filename, user, repo, branch,token=token)
            license_output = OrderedDict()
            license_output["file"] = license_filename
            license_output["in_root"] = license_in_root
            license_output["spdx_identifier"] = license_result.get("spdx_identifier") if license_result else None
            license_output["license_name"] = license_result.get("license_name") if license_result else None
            license_output["overall_suggestion"] = license_result.get("overall_suggestion") if license_result else None
            results.append(license_output)

        # README
        if readme_filename is None:
            results.append({
                "file_type": "readme",
                "result": "No such file found"
            })
        else:
            readme_in_root = is_in_root(all_files, readme_filename)
            readme_result = cls.check_readme_file(readme_filename, user, repo, branch, token=token)
            readme_output = OrderedDict()
            readme_output["file"] = readme_filename
            readme_output["in_root"] = readme_in_root
            readme_output["has_project_title_and_purpose"] = readme_result.get("has_project_title_and_purpose") if readme_result else None
            readme_output["has_installation_instructions"] = readme_result.get("has_installation_instructions") if readme_result else None
            readme_output["has_usage_examples"] = readme_result.get("has_usage_examples") if readme_result else None
            readme_output["lists_dependencies"] = readme_result.get("lists_dependencies") if readme_result else None
            readme_output["mentions_license"] = readme_result.get("mentions_license") if readme_result else None
            readme_output["has_documentation_link"] = readme_result.get("has_documentation_link") if readme_result else None
            readme_output["word_count_over_100"] = readme_result.get("word_count_over_100") if readme_result else None
            readme_output["has_section_headers"] = readme_result.get("has_section_headers") if readme_result else None
            readme_output["overall_suggestions"] = readme_result.get("overall_suggestions") if readme_result else None
            results.append(readme_output)

        # REQUIREMENTS
        if requirements_filename is None:
            results.append({
                "file_type": "requirements",
                "result": "No such file found"
            })
        else:
            requirements_in_root = is_in_root(all_files, requirements_filename)
            requirements_result = cls.check_requirements_file(requirements_filename, user, repo, branch,token=token)
            requirements_output = OrderedDict()
            requirements_output["file"] = requirements_filename
            requirements_output["in_root"] = requirements_in_root
            requirements_output["has_basic_requirements"] = requirements_result.get("has_basic_requirements") if requirements_result else None
            requirements_output["is_empty"] = requirements_result.get("is_empty") if requirements_result else None
            requirements_output["issues"] = requirements_result.get("issues") if requirements_result else None
            results.append(requirements_output)

        return results



