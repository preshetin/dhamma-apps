from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter
import sys

load_dotenv()

#------- Fill this -------
filename = 'dullabha.md'
# index name in pincone
index_name = "dullabha"

namespace = "dullabha"
# ------------------------

with open(filename, 'r', encoding='utf-8') as file:
    markdown_document = file.read()

# print(markdown_document)
# sys.exit()

headers_to_split_on = [
    ("##", "Header 2")
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
)
md_header_splits = markdown_splitter.split_text(markdown_document)

print(md_header_splits)
print("\n")

from langchain_pinecone import PineconeEmbeddings
import os

print('env variables:')
print(os.environ.get('OPENAI_API_KEY'))
print(os.environ.get('PINECONE_API_KEY'))

model_name = 'multilingual-e5-large'
embeddings = PineconeEmbeddings(
    model=model_name,
    pinecone_api_key=os.environ.get('PINECONE_API_KEY')
)

from pinecone import Pinecone, ServerlessSpec
import time

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
region = os.environ.get('PINECONE_REGION') or 'us-east-1'
spec = ServerlessSpec(cloud=cloud, region=region)


if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embeddings.dimension,
        metric="cosine",
        spec=spec
    )
    # Wait for index to be ready
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

# See that it is empty
print("Index before upsert:")
print(pc.Index(index_name).describe_index_stats())
print("\n")


from langchain_pinecone import PineconeVectorStore

# namespace = "wondervector5000"

docsearch = PineconeVectorStore.from_documents(
    documents=md_header_splits,
    index_name=index_name,
    embedding=embeddings,
    namespace=namespace
)

time.sleep(5)

# See how many vectors have been upserted
print("Index after upsert:")
print(pc.Index(index_name).describe_index_stats())
print("\n")
time.sleep(2)



index = pc.Index(index_name)
# namespace = "wondervector5000"

for ids in index.list(namespace=namespace):
    query = index.query(
        id=ids[0], 
        namespace=namespace, 
        top_k=1,
        include_values=True,
        include_metadata=True
    )
    print(query)
    print("\n")



#use the chatbot



# from langchain_openai import ChatOpenAI
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain import hub


# retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
# retriever=docsearch.as_retriever()

# llm = ChatOpenAI(
#     openai_api_key=os.environ.get('OPENAI_API_KEY'),
#     model_name='gpt-4o-mini',
#     temperature=0.0
# )

# combine_docs_chain = create_stuff_documents_chain(
#     llm, retrieval_qa_chat_prompt
# )
# retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)




# query1 = "какое расписание курсов в следующем году?"

# query2 = "пришлтие реквизиты для пожертвований"



# answer1_without_knowledge = llm.invoke(query1)

# print("Query 1:", query1)
# print("\nAnswer without knowledge:\n\n", answer1_without_knowledge.content)
# print("\n")
# time.sleep(2)




# answer1_with_knowledge = retrieval_chain.invoke({"input": query1})

# print("Answer with knowledge:\n\n", answer1_with_knowledge['answer'])
# print("\nContext used:\n\n", answer1_with_knowledge['context'])
# print("\n")
# time.sleep(2)




print('\n\n\n')
print('all goood!!')
print('\n\n\n')