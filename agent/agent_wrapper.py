import os

from langchain_core.runnables import RunnableSerializable
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, PrivateAttr
from openai import OpenAI

# Custom wrapper to make GitHub OpenAI model usable with LangChain
class GitHubChatLLM(RunnableSerializable, BaseModel):
    model: str = "openai/gpt-4.1"
    temperature: float = 0.3
    max_tokens: int = 1024

    # Use PrivateAttr for objects that shouldn't be serialized
    _client: OpenAI = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=os.environ["GITHUB_TOKEN"]
        )

    def invoke(self, input, config=None, **kwargs):
        messages = []

        if isinstance(input, dict) and "messages" in input:
            for msg in input["messages"]:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    messages.append({"role": "system", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})
        else:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": str(input)}
            ]

        response = self._client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return AIMessage(content=response.choices[0].message.content)

