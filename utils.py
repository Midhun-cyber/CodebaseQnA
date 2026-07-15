import os
import shutil
import stat
from git import Repo
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
REPOSITORY_FOLDER = "repository"

SUPPORTED_EXTENSIONS = (
    ".py", ".java", ".cpp", ".c",
    ".js", ".ts", ".html", ".css",
    ".md", ".json", ".xml",
    ".yml", ".yaml", ".txt"
)

def remove_readonly(func, path, _):
    """Remove read-only attribute on Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone_repository(repo_url):
    try:
        # Validate URL
        if not repo_url.startswith("https://github.com/"):
            return False, "Invalid GitHub Repository URL."

        os.makedirs(REPOSITORY_FOLDER, exist_ok=True)
        repo_name = repo_url.rstrip("/").split("/")[-1]
        destination = os.path.join(REPOSITORY_FOLDER, repo_name)

        if os.path.exists(destination):
            return True, "cloned"

        # Delete any old repositories
        for item in os.listdir(REPOSITORY_FOLDER):
            item_path = os.path.join(REPOSITORY_FOLDER, item)

            try:
                shutil.rmtree(item_path, onerror=remove_readonly)
            except Exception:
                pass

        Repo.clone_from(repo_url, destination)

        return True, "available"

    except Exception as e:
        return False, str(e)

def read_repository():
    """
    Reads all supported files from the cloned repository.

    Returns:
        files_data -> List containing filename and content
        total_files -> Number of files read
    """

    files_data = []

    if not os.path.exists(REPOSITORY_FOLDER):
        return files_data, 0

    repositories = [
        folder for folder in os.listdir(REPOSITORY_FOLDER)
        if os.path.isdir(os.path.join(REPOSITORY_FOLDER, folder))
    ]

    if not repositories:
        return files_data, 0

    repo_path = os.path.join(REPOSITORY_FOLDER, repositories[0])
    for root, dirs, files in os.walk(repo_path):


        dirs[:] = [
            d for d in dirs
            if not d.startswith(".")
            and d != "__pycache__"
        ]

        for file in files:

            if file.endswith(SUPPORTED_EXTENSIONS):

                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                except UnicodeDecodeError:

                    try:
                        with open(file_path, "r", encoding="latin-1") as f:
                            content = f.read()

                    except:
                        continue

                files_data.append({
                    "file_name": file,
                    "file_path": file_path,
                    "content": content
                })

    return files_data, len(files_data)
    
def split_documents(files_data):
    """
    Splits repository files into smaller chunks.
    Returns:
        chunks -> List of LangChain Document objects
        total_chunks -> Number of chunks created
    """

    documents = []
    for file in files_data:

        documents.append(
            Document(
                page_content=file["content"],
                metadata={
                    "file_name": file["file_name"],
                    "file_path": file["file_path"]
                }
            )
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Split documents
    chunks = splitter.split_documents(documents)

    return chunks, len(chunks)
    
def create_vector_store(chunks):

    from rag import get_embeddings

    embeddings = get_embeddings()
    if os.path.exists("vector_store"):
        shutil.rmtree("vector_store")

    os.makedirs("vector_store", exist_ok=True)

    vector_db = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    vector_db.save_local("vector_store")

    return vector_db
