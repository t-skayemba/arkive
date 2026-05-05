from pathlib import Path
from services.document_processor import DocumentProcessor

# Create a sample text file to test with
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

processor = DocumentProcessor()
metadata, chunks = processor.process_file(sample, "sample_test.txt")

print(f"Document ID:   {metadata.document_id}")
print(f"File type:     {metadata.file_type}")
print(f"Total chunks:  {metadata.total_chunks}")
print(f"File size:     {metadata.file_size_kb} KB")
print()
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} (page {chunk.page_number}) ---")
    print(chunk.content[:120] + "..." if len(chunk.content) > 120 else chunk.content)
    print()