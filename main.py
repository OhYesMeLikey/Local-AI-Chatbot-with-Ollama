from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from sensitive_data_parser import SensitiveDataContextParser


# Load your context document
with open('context.md', 'r') as f:
    context_text = f.read()

# Parse it
parser = SensitiveDataContextParser(context_text)

# Use the structured data
categories = parser.parsed_data['sensitive_categories']
masking_examples = parser.parsed_data['masking_examples']

# Build prompt for your DeepSeek model
prompt_template = parser.build_prompt_template()


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
    context = prompt_template
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