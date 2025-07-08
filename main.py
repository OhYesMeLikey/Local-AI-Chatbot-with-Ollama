from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
""" 

model = OllamaLLM(model="deepseek-r1:1.5b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def handle_conversation():
    context = """You are a skilled AI assistant that checks if the user's data is considered sensitive or not. If the data is sensitive, then you will mask it appropriately with the given format. You will also provide the user with a three different examples of how the data can be masked: partial masking and full masking. If the data is not sensitive, then you will simply return the data as it is."""
    print("Welcome to the AI Chatbot to mask sensitive data. What information would you like to check? Type 'exit' to end.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        result = chain.invoke({"context": context, "question": user_input})
        print("AI:", result)
        context += f"\nYou: {user_input}\nAI: {result}\n"
        

if __name__ == "__main__":
    handle_conversation()