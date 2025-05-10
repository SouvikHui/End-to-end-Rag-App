import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
# from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
load_dotenv()

class ArticleQAEngine:
    def __init__(self, vector_path: str = "faiss_store.pkl"):
        self.vector_path = vector_path
        self.retriever = None
        self.llm = self._load_llm()
        self.prompt = self._build_prompt()
        self.rag_chain = None

    def _load_retriever(self):
        embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5",nomic_api_key=os.getenv("NOMIC_API_KEY"))
        vectordb = FAISS.load_local(
            self.vector_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vectordb.as_retriever()

    def _load_llm(self):
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.9,
            max_retries=2
        )

    def _build_prompt(self):
        system_prompt = """
        You are a helpful assistant for question-answering based on provided article contents.

        Your response must follow this format:

            Relevant:
            <Shortened quoted text from the article>

            Source:
            <URL of the quoted article>

            Explanation:
            <Explanation and additional insights based on the quote>

        Instructions for you:
        - Use only the content between the triple backticks below as context for your answer.
            Context:
                ```
                {context}
                ```
        - If the user asks for an explanation or comprehension, give a clear and simple one that a beginner can understand. Make it rich with
            information present in the context or in the entire article. Make sure to cover the full context or the article, 
            focusing on the 20% of key points that explain 80% of the topic, without missing any important parts. 
        - If no relevant content is found, reply:
            "It is not provided in the article, but I can assist you using my knowledge if you want. Would you like that?" Then in the next run, 
            if the user agrees or responds positively, access the previous chat_hist and provide an answer from your own knowledge:
            - If a known source is available, mention it.
            - Otherwise, say: "This is from my knowledge only. Kindly verify it on the internet."
        """

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

    # def _format_docs(self, docs):
    #     return "\n\n".join(doc.page_content for doc in docs)

    def _format_docs(self,docs:List[Document],**kwargs):
        return '\n\n'.join(f"[Source:{doc.metadata.get('source')}]\n{doc.page_content}" for doc in docs)
    
    def _build_chain(self):
        if self.retriever is None:
            raise ValueError("Retriever is not initialized. Cannot build chain.")
        return (
            {
                "context": self.retriever | RunnableLambda(self._format_docs),
                "input": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def answer_question(self, query: str) -> str:
        if self.rag_chain is None:
            raise ValueError("RAG chain not built. Please process URLs first.")
        return self.rag_chain.invoke(query)
    
    def set_retriever_from_local(self):
        self.retriever = self._load_retriever()
        self.rag_chain = self._build_chain()
