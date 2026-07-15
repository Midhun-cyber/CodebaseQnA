import streamlit as st
from typer import style

from utils import (
    clone_repository,
    read_repository,
    split_documents,
    create_vector_store
)
from rag import search_repository
from groqai import ask_llm,generate_readme
# ---------------------- Page Configuration ----------------------
st.set_page_config(
    page_title="CodebaseQ&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
if "total_files" not in st.session_state:
    st.session_state.total_files = 0
if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0
if "language" not in st.session_state:
    st.session_state.language = "-"

st.markdown("""
<style>

/* Remove top padding */
.block-container{
    padding-top:0.5rem;
    padding-bottom:1rem;
}

/* Remove space before first element */
div[data-testid="stVerticalBlock"] > div:first-child{
    margin-top:0rem;
    padding-top:0rem;
}
/* Primary Button */
.stButton > button {
    background-color: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

/* Hover Effect */
.stButton > button:hover {
    background-color: #1D4ED8 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(37, 99, 235, 0.35);
}

/* Click Effect */
.stButton > button:active {
    transform: scale(0.98);
}

</style>
""", unsafe_allow_html=True)
# ---------------------- Sidebar ----------------------
with st.sidebar:
    st.title("CodebaseQ&A")

    st.markdown("---")

    st.subheader("◈ Project")

    st.write("""
AI-powered assistant that understands GitHub repositories
and answers questions using RAG.
""")

    st.markdown("---")

    st.subheader("🛠 Tech Stack")

    st.markdown("""
-  Python
-  Streamlit
-  LangChain
-  Groq
-  FAISS
-  HuggingFace Embeddings
""")

    st.markdown("---")

# ---------------------- Header ----------------------
st.markdown("""
<div style="text-align:center;
    color:#22D3EE;
    font-size:60px;
    font-weight:800;
    margin-top:10px;">
    <h1 style="margin-bottom: 5px;">
        CodebaseQ&A
    </h1>
    <p style="font-size:18px; margin-right:20px; color:gray;">
        AI-Powered GitHub Repository Assistant
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------- Repository + Statistics ----------------------

left, divider, right = st.columns([3, 0.05, 1])


# ===========================================================
# LEFT SIDE
# ===========================================================
with left:

    st.subheader("▣ Repository")

    repo_url = st.text_input(
        "Enter GitHub Repository URL",
        placeholder="https://github.com/username/repository"
    )

    clone_clicked = st.button(
        "➤ Clone Repository",
        use_container_width=True,
        type="primary"
    )

    if clone_clicked:
        if repo_url.strip():

            with st.spinner("Cloning repository..."):

                success, message = clone_repository(repo_url)

            if success:
                # Clear previous repository results
                st.session_state.pop("answer", None)
                st.session_state.pop("docs", None)
                st.session_state.pop("sources", None)
                st.session_state.pop("readme", None)
                progress = st.empty()

                log = ""
                progress.markdown(log, unsafe_allow_html=True)

                # ---------------- Repository ----------------
                if message == "cloned":
                    log += "⏳ Cloning repository...<br>"
                else:
                    log += "⏳ Checking repository...<br>"

                progress.markdown(log, unsafe_allow_html=True)

                if message == "cloned":
                    log = log.replace(
                        "⏳ Cloning repository...<br>",
                        "✔ Repository cloned successfully.<br>"
                    )
                else:
                    log = log.replace(
                        "⏳ Checking repository...<br>",
                        "✔ Repository already available.<br>"
                    )

                progress.markdown(log, unsafe_allow_html=True)

                # ---------------- Read ----------------
                try:

                    log += "⏳ Reading repository files...<br>"
                    progress.markdown(log, unsafe_allow_html=True)

                    files_data, total_files = read_repository()
                    language_extensions = {
                        "py": "Python",
                        "java": "Java",
                        "js": "JavaScript",
                        "ts": "TypeScript",
                        "cpp": "C++",
                        "c": "C",
                        "html": "HTML",
                        "css": "CSS"
                    }

                    extensions = {}

                    for file in files_data:
                        ext = file["file_name"].split(".")[-1].lower()

                        if ext in language_extensions:
                            extensions[ext] = extensions.get(ext, 0) + 1

                    if extensions:
                        dominant_ext = max(extensions, key=extensions.get)
                        st.session_state.language = language_extensions[dominant_ext]
                    else:
                        st.session_state.language = "Unknown"

                    log = log.replace(
                        "⏳ Reading repository files...<br>",
                        "✔ Repository files loaded successfully.<br>"
                    )

                    progress.markdown(log, unsafe_allow_html=True)

                except Exception as e:

                    progress.error(f"❌ Failed to read repository.\n\n{e}")
                    st.stop()

                # ---------------- Split ----------------
                try:

                    log += "⏳ Splitting documents...<br>"
                    progress.markdown(log, unsafe_allow_html=True)

                    chunks, total_chunks = split_documents(files_data)

                    log = log.replace(
                        "⏳ Splitting documents...<br>",
                        "✔ Documents split successfully.<br>"
                    )

                    progress.markdown(log, unsafe_allow_html=True)

                except Exception as e:

                    progress.error(f"❌ Failed to split documents.\n\n{e}")
                    st.stop()

                # ---------------- Embeddings ----------------
                try:
                    with st.spinner("⏳ Creating embeddings..."):
                     create_vector_store(chunks)
                    from rag import get_vector_store
                    get_vector_store.clear()
                    log += "✔ Embeddings & Vector Store created successfully.<br>"

                    progress.markdown(log, unsafe_allow_html=True)

                except Exception as e:

                    progress.error(f"❌ Failed to create embeddings.\n\n{e}")
                    st.stop()

                # ---------------- Finish ----------------
                st.session_state.total_files = total_files
                st.session_state.total_chunks = total_chunks
                st.session_state.status = "Indexed"

                log += "<br><span style='color:#22c55e; font-size:20px; font-weight:bold;'> Repository Indexed Successfully</span><br>"
                log += "<span style='color:#22c55e;font-size:20px; font-weight:bold;'> Repository is ready for AI questions!</span>"
                progress.markdown(log, unsafe_allow_html=True)

            else:
                st.error(message)

        else:

            st.warning("Please enter a GitHub repository URL.")
# ===========================================================
# RIGHT SIDE
# ===========================================================
with right:

    st.subheader("◉ Statistics")

    box_style = """
        border:1px solid #2c3e50;
        border-radius:8px;
        padding:10px;
        margin-bottom:15px;
        text-align:center;
        background-color:#1f3b5b;
        color:white;
        font-size:18px;
        font-weight:bold;
    """

    st.markdown("**◆ Files:**", unsafe_allow_html=True)
    st.markdown(
        f"<div style='{box_style}'>{st.session_state.total_files}</div>",
        unsafe_allow_html=True
    )

    st.markdown("**◆ Chunks:**", unsafe_allow_html=True)
    st.markdown(
        f"<div style='{box_style}'>{st.session_state.total_chunks}</div>",
        unsafe_allow_html=True
    )

    st.markdown("**◆ Language**")
    st.markdown(
        f"<div style='{box_style}'>{st.session_state.language}</div>",
        unsafe_allow_html=True
    )

st.divider()
# ---------------------- Chat ----------------------
st.subheader("➜ Ask Repository")

question = st.text_input(
    "Ask a question",
    placeholder="Example: Where is the login implemented?"
)

if st.button(" Ask AI", use_container_width=True):

    if question.strip():

        try:
            chunks = search_repository(question)

            if not chunks:
                st.warning("No relevant information found.")
            else:
                context = "\n\n".join([doc.page_content for doc in chunks])

                with st.spinner("AI is analyzing the repository..."):
                    answer = ask_llm(question, context)
                st.session_state.answer = answer
                st.session_state.docs = chunks
                st.session_state.sources = list(
                    {
                        doc.metadata["file_name"]
                        for doc in chunks
                    }
                )

        except Exception as e:
            st.error(f"Search failed.\n\n{e}")

    else:
        st.warning("Please enter a question.")

# ---------------------- Response ----------------------
st.subheader("✦ AI Response")

with st.container(border=True):

    if "answer" in st.session_state:
        st.markdown(st.session_state.answer)

        if "sources" in st.session_state:
            st.subheader("◆ Source Files")

            for file in st.session_state.sources:
                st.markdown(f"✅ `{file}`")

        # ---------------------- Relevant Code ----------------------
        if "docs" in st.session_state:
            st.subheader("⌬ Relevant Code")

            shown_files = set()

            docs = sorted(
                st.session_state.docs,
                key=lambda d: d.metadata["file_name"].lower().endswith(".md")
            )

            for doc in docs:

                file = doc.metadata["file_name"]

                if file in shown_files:
                    continue

                shown_files.add(file)

                if file.endswith(".java"):
                    lang = "java"
                elif file.endswith(".py"):
                    lang = "python"
                elif file.endswith(".js"):
                    lang = "javascript"
                elif file.endswith(".cpp"):
                    lang = "cpp"
                elif file.endswith(".html"):
                    lang = "html"
                else:
                    lang = "text"

                with st.expander(f"{file}"):

                    st.code(
                        doc.page_content,
                        language=lang
                    )
    else:
        st.info("Ask a question about the repository.")
st.divider()
# ---------------------- README Generator ----------------------
st.subheader("◆ README Generator")

if st.button("📝 Generate README", use_container_width=True):

    try:
        files_data, _ = read_repository()

        if not files_data:
            st.warning("Please index a repository first.")
        else:

            context = ""

            for file in files_data[:20]:
                context += f"\n\nFile: {file['file_name']}\n"
                context += file["content"][:1500]

            with st.spinner("Generating README..."):
                st.session_state.readme = generate_readme(context)

    except Exception as e:
        st.error(f"Failed to generate README.\n\n{e}")

# Display README
if "readme" in st.session_state:

    st.markdown(st.session_state.readme)

    st.download_button(
        "📥 Download README.md",
        data=st.session_state.readme,
        file_name="README.md",
        mime="text/markdown"
    )

st.divider()

