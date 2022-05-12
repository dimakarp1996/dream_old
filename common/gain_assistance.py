import re


DEPRESSION_PATTERN = re.compile(r"\b(suicide|depress|kill myself|die.\b|death)", re.IGNORECASE)

BAD_DAY_PATTERN = re.compile(r"\b(bad day|awful day|hard day)", re.IGNORECASE)

PROBLEMS_PATTERN = re.compile(r"\b(problem. with|trouble. with|feel.*? bad|feel.*? awful|tired|feel.*? sad|i'm sad|i am sad|i'm tired|i am tired)", re.IGNORECASE)
