from enum import Enum

class ModelName(str, Enum):
    GPT_4_1 = "openai/gpt-4.1"
    GPT_4_1_MINI = "openai/gpt-4.1-mini"
    GPT_4O = "openai/gpt-4o"
    GPT_4O_MINI = "openai/gpt-4o-mini"
