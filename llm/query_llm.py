from openai import OpenAI
import together
from .base import BaseLLM
import os

class OpenAIQuery(BaseLLM):
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def query(self, context, question):
        prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

class TogetherQuery(BaseLLM):
    def __init__(self, api_key, model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"):
        if not api_key:
            raise ValueError("Together API key not provided")
        os.environ["TOGETHER_API_KEY"] = api_key
        self.model = model

    def query(self, context, question):
        if not context.strip():
            return "No relevant context found to answer the question."

        # Debug: Print context being used
        print(f"Using context: {context}")
            
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based ONLY on the provided context. If the context doesn't contain relevant information to answer the question, say 'I cannot answer this based on the provided context.' Do not use any external knowledge."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}\n\nAnswer based strictly on the above context:"}
        ]
        
        try:
            response = together.Complete.create(
                prompt=messages[1]["content"],
                model=self.model,
                max_tokens=512,
                temperature=0.7
            )
            # Print response for debugging
            print(f"Together API Response: {response}")
            
            # Handle both possible response formats
            if isinstance(response, dict):
                if 'output' in response:
                    return response['output']['choices'][0]['text'].strip()
                return response['choices'][0]['text'].strip()
            
            raise ValueError(f"Unexpected response format: {response}")
            
        except Exception as e:
            raise Exception(f"Together API error: {str(e)}")

def get_llm(provider="together", model=None):
    if provider == "openai":
        return OpenAIQuery(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=model or "gpt-3.5-turbo"
        )
    elif provider == "together":
        return TogetherQuery(
            api_key=os.getenv("TOGETHER_API_KEY"),
            model=model or "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")