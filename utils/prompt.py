PROMPT_JOB_DESCRIPTION = """Given job description:
```{job_description}```
Extract requirement in form of json with following description:
is_required_master: True if need master otherwise False
is_required_bachelor: True if need bachelor otherwise False
bachelor_program: list of program required bachelor program
master_program: list of program required master program
tenure: total tenure expected
Only return expected json"""
TEXT_JOB = """Looking for {role} with job description: {description}. required skills: {skills}."""
ADDITIONAL_TENURE_TEXT_JOB = """with tenure {tenure}"""
ADDITIONAL_EDUCATION_TEXT_JOB = """with education background {education}"""
TEXT_CANDIDATE = """Candidate with {years} years of experience as {current_role} at {current_company}. Previously worked as {previous_role}. Skills include {skills}. Education: {education}"""
