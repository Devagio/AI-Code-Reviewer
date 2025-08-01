import json
from jinja2 import Template
from app.core.prompts import Naturallangprompt, REVIEW_TABLE_PROMPT
import os
from app.api.ai_review import ask_chatgpt 

class Naturallangoutput:

    @staticmethod
    def output(all_results) -> None:
        all_results_json = json.dumps(all_results, indent=2)
        prompt = Template(Naturallangprompt).render(results=all_results_json)
        summary = ask_chatgpt(prompt, model="gpt-4.1-mini-2025-04-14")
        return summary 

    @staticmethod
    def markdown_output(all_results) -> None:
        all_results_json = json.dumps(all_results, indent=2)
        prompt = Template(REVIEW_TABLE_PROMPT).render(results=all_results_json)
        summary = ask_chatgpt(prompt, model="gpt-4.1-2025-04-14")
        return summary 
    
    