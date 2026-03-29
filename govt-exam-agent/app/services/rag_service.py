from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class RAGService:
    def __init__(self):
        # Store FAISS vectorstore for each session
        self.session_vectorstores = {}
        # Embeddings model - Lazy load (only when needed)
        self.embeddings = None

    def _get_embeddings(self):
        """Lazy load embeddings only when needed"""
        if self.embeddings is None:
            print("⏳ Loading embeddings model (first time only)...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Embeddings model loaded successfully")
        return self.embeddings

    def load_document(self, session_id, file_path):
        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,   # increased to capture full project info
            chunk_overlap=100
        )
        chunks = splitter.split_documents(documents)

        # Create FAISS vectorstore for this session
        self.session_vectorstores[session_id] = FAISS.from_documents(
            chunks,
            self._get_embeddings()
        )

    def retrieve(self, query, session_id):
        vector_store = self.session_vectorstores.get(session_id)
        if not vector_store:
            return []

        # Search top 5 relevant chunks
        docs = vector_store.similarity_search(query, k=5)
        return [doc.page_content for doc in docs]