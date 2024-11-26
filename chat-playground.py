import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from pinecone import Pinecone


load_dotenv()

def get_answer_from_document(message):
    # Initialize Pinecone
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    # Define the index and namespace
    index_name = "children-courses-org"
    namespace = "children-courses-org"

    # Initialize the embeddings
    model_name = 'multilingual-e5-large'
    embeddings = PineconeEmbeddings(
        model=model_name,
        pinecone_api_key=os.environ.get('PINECONE_API_KEY')
    )

    # Load the existing vector store
    docsearch = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace
    )

    # Initialize the retriever
    retriever = docsearch.as_retriever()

    # Initialize the language model
    llm = ChatOpenAI(
        openai_api_key=os.environ.get('OPENAI_API_KEY'),
        model_name='gpt-4o-mini',
        temperature=0.0
    )

    # Create the retrieval chain
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(
        llm, retrieval_qa_chat_prompt
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    
    answer_with_knowledge = retrieval_chain.invoke({"input": message})

    return answer_with_knowledge['answer']

res = get_answer_from_document('скинь ссылку на письмо домой')
print(res)
