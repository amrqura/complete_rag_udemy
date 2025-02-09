from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from sentence_transformers import SentenceTransformer
import re

from utils import call_llm
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.embeddings import HuggingFaceEmbeddings
from docx import Document


__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


class LLAMA_MODEL:

    def __init__(self):
        self.vectorstore_ar = self.get_arabic_vector_store()
        self.vectorstore_en = self.get_english_vector_store()
        self.conversation_history = []

    def custom_arabic_text_splitter_by_heading1(self, docx_path: str):
      doc = Document(docx_path)
      sections = []
      current_section = ""

      for para in doc.paragraphs:
          if para.style.name == 'Heading 1':
              if current_section:
                  sections.append(current_section)
                  current_section = ""
              current_section += para.text + "\n"
          else:
              current_section += para.text + "\n"

      if current_section:
          sections.append(current_section)
      return sections

    def get_arabic_vector_store(self):
        embeddings = HuggingFaceEmbeddings(model_name='UBC-NLP/ARBERT')
        vectorstore_ar = Chroma(persist_directory="ar", embedding_function=embeddings)
        return vectorstore_ar

    def get_english_vector_store(self):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore_en = Chroma(persist_directory="en", embedding_function=embeddings)
        return vectorstore_en

    def ollama_llm(self, question, context, language):
        if language == 'ar':
            system_message = "تصرف كخبير في الموضوع المطروح. أجب عن السؤال باللغة العربية فقط. إذا لم يكن لديك إجابة من المعلومات المقدمة، أخبر المستخدم بذلك. استخدم لغة واضحة ومبسطة. أجب بشكل مباشر ومختصر، وتجنب تضمين سؤال المستخدم في الإجابة."
            prompt = f"""

            السؤال: {question}
            {f"السياق: {context}" if context else ""}
            قدم إجابة واضحة ومباشرة باستخدام المعلومات المتاحة فقط. إذا كان السؤال يتطلب حسابات، قدم الحل خطوة بخطوة. إذا كانت المعطيات غير كافية، اطلب المعلومات الإضافية بوضوح من المستخدم. استخدم اللغة العربية الفصحى والمبسطة دون إدخال حروف أجنبية.
            """
        else:
            system_message = "You are an expert in the given topic. Answer the question in English. If you do not have enough information, let the user know. Use clear and simple language. Provide a direct and concise response, and avoid repeating the user's question in your answer."
            prompt = f"""

            Question: {question}
            {f"Context: {context}" if context else ""}
            Provide a clear and direct response using only the available information. If the question requires calculations, show the solution step-by-step. If the provided data is insufficient, request the necessary additional information from the user.
            """

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        )

        final_prompt = prompt_template.format(input=prompt, chat_history=self.conversation_history)
        response = call_llm(final_prompt)

        self.conversation_history.append(HumanMessage(content=question))
        self.conversation_history.append(AIMessage(content=response))

        return response

    def determine_language(self, text):
        """
        This function determines if the given text is in English or Arabic.

        Args:
            text: A string containing the text.

        Returns:
            A string indicating the language of the text ("en" for English, "ar" for Arabic, or None if the language cannot be determined).
        """
        # Check for Arabic characters using a regular expression
        if re.search(r'[\u0600-\u06FF]', text):
            return "ar"
        # Check for English characters using a regular expression
        elif re.search(r'[a-zA-Z]', text):
            return "en"
        # If no language can be determined, return None
        else:
            return None

    def get_retriever(self, question):
        language = self.determine_language(question)
        if language == 'ar':
            return self.vectorstore_ar.as_retriever(search_kwargs={"k": 3})
        else:
            return self.vectorstore_en.as_retriever(search_kwargs={"k": 3})

    def rag_chain(self, question):
        language = self.determine_language(question)
        retrieved_docs = self.get_retriever(question).invoke(question)
        formatted_context = " ".join(doc.page_content.replace('\n', ' ') for doc in retrieved_docs)
        return self.ollama_llm(question, formatted_context, language)


    def get_important_facts(self, question):
        response = self.rag_chain(question)
        if not response.strip() or response =="":
            return ""
        return response
