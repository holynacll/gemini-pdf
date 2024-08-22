# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.messages import HumanMessage, SystemMessage

# load_dotenv()

# if __name__ == '__main__':
#     print('Hello Langchain')
#     print(os.environ['GOOGLE_API_KEY'])

#     llm = ChatGoogleGenerativeAI(
#         model="gemini-1.5-pro",
#         temperature=0,
#         max_tokens=None,
#         timeout=None,
#         max_retries=2,
#         # other params...
#     )
#     messages = [
#         SystemMessage(
#             content="You are a helpful assistant that translates English to French. Translate the user sentence."
#         ),
#         HumanMessage(
#             content= "I love programming."
#         )
#     ]
#     ai_msg = llm.invoke(messages)
#     print(ai_msg.content)

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "You are a helpful assistant that translates {input_language} to {output_language}.",
#             ),
#             ("human", "{input}"),
#         ]
#     )

#     # chain = pdf to images | get resulted text from each image to aws ocr |
#     chain = prompt | llm | StrOutputParser()
#     response = chain.invoke(
#         {
#             "input_language": "English",
#             "output_language": "German",
#             "input": "I love programming.",
#         }
#     )

#     print(response)
