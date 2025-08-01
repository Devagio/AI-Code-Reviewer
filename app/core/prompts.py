PYTHON_FILE_REVIEW_PROMPT = """
You are a senior Python code reviewer.
Here is the code:

{{ code }}


Analyze this Python file for the three criteria below and output ONLY valid JSON in the following format:
{
  "comments": {"status": "...", "suggestion": "..."},
  "docstrings": {"status": "...", "suggestion": "..."},
  "function_modularity": {"status": "...", "suggestion": "..."}
}

The allowable values in status are `status`: "good" or "needs improvement". `suggestion` should be "NULL" if `status` is "good".

Criteria for judging Comments:
- Check for inline comments explaining why is it commented, not just what.
- Are more than 20 percent of line commented? (estimate based on code structure)
- Are there too many obvious/useless comments?

**Docstrings**:
- Do the public functions and classes generally have a docstring?
- Do the existing docstrings include purpose, parameter types, and return value/type?
- Do they follow Google or NumPy style?

**Function Modularity/Variable Names**:
- Are functions small, single-purpose, and modular?
- Are variable/function/class names clear and meaningful?
- Suggest improvements if any function is too long (>32 lines) or poorly named.


**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
"""



files_identify = """
You are an expert software project analyzer.

Given a list of all files (including paths, file names, and extensions) in a code repository, your task is to identify, as accurately as possible, the main project files for:
- The README (any file that serves as the project overview, regardless of spelling, case, extension, or location)
- The requirements file (any file that lists dependencies, such as requirements.txt, pyproject.toml, or similar, regardless of spelling, case, or extension)
- The license file (any file providing license information, such as LICENSE, LICENSE.txt, or variants, regardless of spelling, case, or extension)

The file names may have unusual spellings, nonstandard extensions, or be placed in subdirectories. Use your best reasoning to select the most likely candidate for each.

List of files:
{{ files }}

Output JSON only. Example:
{
  "readme": "<exact file name or path>",
  "requirements": "<exact file name or path>",
  "license": "<exact file name or path>"
}
If a file is missing, output "NULL" for that field.
**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON. Use null (not 'None' or empty string) if a file is not found.
"""


license_check_prompt = """
You are an expert codebase license auditor.
You will be given the full content of a LICENSE file from a code repository and  Your tasks as follows-
LICENSE file content:
{{ license_content }}

Your tasks:
1. **SPDX Identifier Check**: Determine whether the content contains a valid SPDX license identifier. If yes, "<'valid', 'invalid', or 'unknown'>"
2. **License Name Extraction**: Extract the human-readable name of the license (for example: MIT, Apache License 2.0, GNU GPL, etc.).
3. **Suggestion**: Based on the content and type of project, suggest a potentially better or more common license for this use-case, if any. If the current license is appropriate, state that clearly.
The overall project is intended to be a simple open-source codebase created during an astronomy software workshop.

Output a JSON object with these exact fields and formatting:

{
  "spdx_identifier": "<SPDX identifier string or 'unknown'>",
  "license_name": "<Name of the license or 'unknown'>",
  "overall_suggestion": "<Brief advice or suggestion for the license choice>"
}

**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
"""


readme_check_prompt = """
You are a README file quality evaluator.

You will be given the full content of a README file below and your tasks as follows:
Given the content of a README file:
{{ readme_content }}

Your Tasks:
1. Does it contain a clear project title and describe the project's purpose?
2. Does it provide installation instructions?
3. Does it provide usage examples, preferably with code snippets?
4. Does it list dependencies or requirements?
5. Does it mention a license?
6. Does it include a link to documentation?
7. Is the word count greater than 100?
8. Does it include section headers (e.g., ## Installation, ## Usage)?
9. Give overall suggestions for improvement if needed.

Provide your output as a raw JSON object in the exact format below:

{
  "has_project_title_and_purpose": true/false,
  "has_installation_instructions": true/false,
  "has_usage_examples": true/false,
  "lists_dependencies": true/false,
  "mentions_license": true/false,
  "has_documentation_link": true/false,
  "word_count_over_100": true/false,
  "has_section_headers": true/false,
  "overall_suggestions": "<advice for improvement if needed, otherwise 'None'>"
}

**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
"""


requirements_check_prompt = """
You are a Python requirements file quality checker.

Given the full content of a requirements file (such as requirements.txt or pyproject.toml):

{{ requirements_content }}

Perform the following checks:

1. Does the file list any dependencies? If yes, does it include all the basic/common required packages for a typical Python project? (For example, numpy, requests, pandas, etc.—use your judgment based on the context.)
2. Is the file empty?
3. Are there any clear issues? For example:
   - The file is empty.
   - There are invalid lines or formatting.
   - Versions are unpinned (i.e., packages without ==, >=, <=, or version ranges).
   - All packages are pinned to a single version (==).
4. If the file is pyproject.toml, extract dependencies from the relevant section.
5. Summarize any issues or potential improvements (e.g., recommend using version ranges, fixing formatting).

Output your findings as a raw JSON object in the following format:

{
  "has_basic_requirements": true/false,      // true if all basic/common dependencies are present, else false
  "is_empty": true/false,                    // true if the file is empty, else false
  "issues": "<short description of detected issues, or null if none>"
}

**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
"""



ATOMIC_Commits = """
You are an expert code reviewer.
Check the following git commit message and output ONLY a suggestion (or a compliment if it's already good):
- Vague commit messages should be flagged.
- Good messages should describe the change and its purpose.
- If the message is vague, suggest how to make it more specific.
- If the commit message is quite bad or vague, output a single line suggestion; else output a single line compliment. Do not output anything else.

Commit message:
{{ commit_msg }}

"""


PR_PROMPT = """
You are an expert open-source code reviewer.

For the following data, review these two things separately:
Title: {{ title }}
Description: {{ body }}

1. **PR Title Review**:
- Is the PR title longer than 3 words and clearly descriptive of the changes?
- If not, suggest a better title.

2. **PR Description Review**:
- Does the description clearly state the purpose and what was changed?
- Does it mention screenshots, images, or code snippets if they would help?
- Does it reference an issue (e.g., “Fixes #4”) if relevant?
- Suggest improvements if anything is missing.

Output your review as a JSON object with the following structure, with actionable suggestions:
{
  "title_review": "<feedback or suggestion for the title>",
  "description_review": "<feedback or suggestion for the description>"
}
**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
"""


PACKAGE_PROMPT = """
You are a Python packaging expert.

Given this list of all files and paths in a repository:
{{ files }}

Check only for the following important package-related files (ignore README, LICENSE, and requirements.txt):

- setup.py
- pyproject.toml
- setup.cfg
- .gitignore
- At least one __init__.py (in any directory)

For each, in the output JSON, include:
- "filename": "<actual filename or path if present, else null>"
- "available": true/false
- "useful_for": "<short explanation of why this file is important for a Python package>"

If a file is missing (no variant present), add an entry with "available": false and a brief useful_for reason.
**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
"""



Naturallangprompt ="""
You are a friendly, expert Python code reviewer.

You’ll receive a JSON object called results, containing AI-generated reviews of several Python files. These reviews include information about comments, docstrings, code structure, and overall quality.
Given this JSON with per-file analysis of comments, docstrings, and function modularity for a Python codebase:

{{ results }}
Your job is to:
- Write a clear, friendly summary of the project’s overall code quality. Use everyday language—highlight what’s working and where there’s room to grow. Be supportive and avoid heavy jargon.
- Highlight notable strengths—call out specific good habits or parts of the codebase.
- List the 3 most helpful, actionable improvements for the project. Make your advice concrete and easy to follow, even for beginners.
- Identify any potential bugs or risky patterns that should be addressed.
- Suggest 2-3 “quick wins”—easy changes that would make a noticeable difference.
- Fill in a simple best practice checklist (true/false) for common Python habits.
- Add short file-specific comments if certain files need special attention or stand out.
- Give an overall readability/writing quality score from 1 to 10 (10 = fantastic, open-source-level code; 1 = very hard to read). Briefly explain your score in 1-2 sentences.
- Suggest “next steps” for the author to keep improving after these changes.

Output your response in this JSON format:
{
  "summary": "A friendly, natural-language summary of the project's code quality. Mention what’s good and what can be better.",
  "strengths": [
    "Clear variable names throughout the code.",
    "Consistent use of docstrings for all functions."
  ],
  "top_improvements": [
    "First actionable suggestion, clearly stated.",
    "Second actionable suggestion, clearly stated.",
    "Third actionable suggestion, clearly stated."
  ],
  "potential_issues": [
    "Function X may fail if input is None.",
    "Some variables are used before being defined."
  ],
  "quick_wins": [
    "Add missing docstrings to top-level functions.",
    "Replace magic numbers with named constants."
  ],
  "best_practices": {
    "uses_meaningful_variable_names": true,
    "has_consistent_indentation": false,
    "follows_PEP8_style": true,
    "includes_unit_tests": false
  },
  "file_comments": {
    "main.py": "Nicely structured, but missing some comments.",
    "utils.py": "Good use of helper functions!"
  },
  "readability_score": 7,
  "score_reason": "Short reason for your score, in natural language.",
  "next_steps": "After making these improvements, consider adding more automated tests to your project."
}
**Important:** Output ONLY the raw JSON object above. Do NOT wrap your response in any markdown, code blocks, or backticks. No explanations or comments—just the JSON.
Instructions:
Review all code file analyses in results before writing your response.
Make your advice clear, specific, and supportive for users at any level.
Focus on concrete tips and easy wins—help the author get better with each review!
"""


REVIEW_TABLE_PROMPT = """
You are a friendly, expert Python code reviewer.

You’ll receive a JSON object called results, containing AI-generated reviews of several Python files. These reviews include information about comments, docstrings, code structure, and overall quality.
Given this JSON with per-file analysis of comments, docstrings, and function modularity for a Python codebase:

{{ results }}

Your job is to create a bunch of MarkDown tables to help humans be able to understand this JSON.


Table 1: 
Heading: ### Project Structure
Create a table with three columns (File, File Name, Avaiable) and five rows.
Under 'File', there will be setup.py, pyproject.toml, setup.cfg, .gitignore, init.py)
Under 'File Name' and 'Available' have the corresponding data from the JSON.
In place of None and False, use the cross emoji; and in place of True, use the tick emoji.


Table 2:
Heading: ### LICENSE
Create a table describing the LICENSE. 
In place of None and False, use the cross emoji; and in place of True, use the tick emoji.
You may replace this entire table by a simple sentence if no LICENSE file was found according to the JSON.

Table 3:
Heading: ### README
Create a table describing the README, with two columns: Aim and Status. 
In place of None and False, use the cross emoji; and in place of True, use the tick emoji.
If any suggestion is present for the README, do not include it in the table; instead, simply add a sentence after the table describing the suggestion.
You may replace this entire table by a simple sentence if no README file was found according to the JSON.

Table 4:
Heading: ### requirements.txt
Create a table describing the requirements.txt-type file. 
In place of None and False, use the cross emoji; and in place of True, use the tick emoji.
If any specific issues are present for this file, do not include them in the table; instead simply add them add bullet points right after the table.
You may replace this entire table by a simple sentence if no requirements.txt-type file was found according to the JSON.


Table 5:
Heading: ### .py Files
Create a table whose rows are .py files, and whose columns are file name, comments status, docstring status, and function modularity status.
In place of "needs improvement", use the cross emoji; and in place of "good", use the tick emoji.
Right after the table, output a 2-line summary of all comment suggestions, 2-line docstring suggestions, and 2-line function modularity suggestions, highlighting the important ones.
Separate these suggestions ("**Comment Suggestions:**", "**Docstring Suggestions:**", "**Modularity Suggestions:**") using line-breaks.
You may replace this entire table by a simple sentence if no .py files were found (or way too many .py files were found) according to the JSON.


Table 6:
Heading: ### Commit History
Create a table of all commits, with columns being "Commit ID", "<4 files changed", "<300 lines changed", and "Commit Message Review".
If for a given commit, the number of files changed is less than or equal to 3, then give file change limit a tick, else give it a cross.
If for a given commit, the number of lines changed is less than or equal to 300, then give line change limit a tick, else give it a cross.
Under message review, give a shortened review of the commit message.
You may replace this entire table by a simple sentence if no commits were found according to the JSON.

Table 7:
Heading: ### PR History
Create a table of all PRs, with columns representing the shortened title review, and shortened description review.
You may replace this entire table by a simple sentence if no PRs were found according to the JSON.


**Important:** Output ONLY the MarkDown. Do NOT wrap your response in any code blocks or backticks. No explanations or comments—just the JSON.
"""