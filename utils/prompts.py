

def build_detection_prompt(code: str) -> str:
    return f"""
You are a security auditor. Identify any vulnerabilities in the following Python code.
Include CWE IDs, short descriptions, and the reason each issue is dangerous.

Code:
{code}
"""

def build_fix_prompt(code: str) -> str:
    return f"""
You are a secure code generator. Improve the following code to eliminate vulnerabilities.
Return the fixed code and explain what changes were made.

Code:
{code}
"""