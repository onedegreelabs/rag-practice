import os
import json
from tqdm import tqdm
from typing import List
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


class RAG:
    def __init__(self):
        self.pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        self.pc_idx = self.pc.Index(os.environ.get("PINECONE_INDEX_NAME"))

        # Create the index if it does not exist
        if os.environ.get("PINECONE_INDEX_NAME") not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=os.environ.get("PINECONE_INDEX_NAME"),
                dimension=1536,
                metric="cosine", 
                spec=ServerlessSpec(
                    cloud="aws", 
                    region="us-east-1"
                ) 
            )

        # Initialize a LangChain object for chatting with the LLM
        # without knowledge from Pinecone.
        self.llm = ChatOpenAI(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            model_name=os.environ.get("OPENAI_CHAT_MODEL"),
            temperature=0.0,
        )

        # Initialize a LangChain object for retrieving information from Pinecone.
        self.knowledge = PineconeVectorStore.from_existing_index(
            index_name=os.environ.get("PINECONE_INDEX_NAME"),
            namespace=os.environ.get("PINECONE_NAMESPACE"),
            embedding=OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
        )

        # Define output parser
        output_parser = JsonOutputParser(pydantic_object=ProfileListParser)
        format_instructions = output_parser.get_format_instructions()

        # Initialize a LangChain object for chatting with the LLM
        # with knowledge from Pinecone. 
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.knowledge.as_retriever(search_type="mmr", search_kwargs={'k': 10, 'lambda_mult': 1.0}),
            chain_type_kwargs={"prompt": PromptTemplate(
                input_variables=["context", "question"],
                template="""
                - Your role is to identify individuals who meet the specified criteria and provide answers accordingly. \n
                - Exclude all external knowledge you possess. \n
                - When answering, return an dictionary with IDs of people. If none are found, return an empty dictionary.
                - Do not respond in code block format. \n
                - {format_instructions} \n
                {context}
                question: {question}
                """,
                partial_variables={"format_instructions": format_instructions},
            )},
        )

    def _dict_to_text(self, data):
        text_lines = [f"{key}: {value}" for key, value in data.items()]
        return ", ".join(text_lines)
    
    # Upload profiles to Pinecone
    def upsert(self, profiles):

        for profile in tqdm(profiles):
            text_representation = self._dict_to_text(profile)
            
            embeddings = OpenAIEmbeddings(
                model=os.environ.get("OPENAI_EMBEDDING_MODEL"),  
                openai_api_key=os.environ.get("OPENAI_API_KEY")  
            ).embed_query(text_representation)

            profile["text"] = text_representation
            self.pc_idx.upsert(
                vectors=[
                    {
                        "id": profile["id"], 
                        "values": embeddings, 
                        "metadata": profile
                    }
                ],
                namespace=os.environ.get("PINECONE_NAMESPACE")
            )

    # Generate answers to queries using the LLM
    def retrieve(self, query):
        try:
            retrieved = self.qa.invoke(query)['result']
            return json.loads(retrieved)
        except ValueError as e:
            print(e)

class ProfileParser(BaseModel):
    id: int = Field(description="ID of profile")

class ProfileListParser(BaseModel):
    results: List[ProfileParser] = Field(description="List of profiles")
