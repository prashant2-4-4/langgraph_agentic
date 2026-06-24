from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama2")

print(llm.invoke("Explain AI in 1 line").content)