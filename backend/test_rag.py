from pathlib import Path
from services.document_processor import DocumentProcessor
from services.rag_engine import RAGEngine

# Create a test document
sample = Path("sample_test.txt")
sample.write_text("""
Artificial Intelligence in Business

AI is transforming how companies operate across every industry.
From automating repetitive tasks to enabling complex decision-making,
the applications are vast and growing rapidly.

Machine Learning Fundamentals

Machine learning allows systems to learn from data without being
explicitly programmed. Supervised learning uses labeled examples,
while unsupervised learning finds hidden patterns in unlabeled data.

Natural Language Processing

NLP enables computers to understand and generate human language.
Modern large language models like GPT and Claude can write, summarize,
translate, and reason across many domains.
""")

# Step 1: Process the document into chunks
print("=== Processing Document ===")
processor = DocumentProcessor()
metadata, chunks = processor.process_file(sample, "sample_test.txt")
print(f"Created {len(chunks)} chunks from {metadata.filename}")

# Step 2: Store chunks in ChromaDB
print("\n=== Storing in Vector DB ===")
rag = RAGEngine()
rag.add_document(chunks, metadata)

# Step 3: Search with a question
print("\n=== Searching ===")
question = "What is machine learning?"
results = rag.search(question, top_k=2)

print(f"Question: {question}")
print(f"Found {len(results)} relevant chunks:\n")
for i, citation in enumerate(results):
    print(f"Result {i+1}:")
    print(f"  File:      {citation.filename}")
    print(f"  Page:      {citation.page_number}")
    print(f"  Score:     {citation.relevence_score}")
    print(f"  Excerpt:   {citation.relevent_excerpt[:100]}...")
    print()