import streamlit as st
import requests
# import docx  # python-docx

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize session state variables
if "url_inputs" not in st.session_state:
    st.session_state.url_inputs = [""] * 1
if "ready_for_qa" not in st.session_state:
    st.session_state.ready_for_qa = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "qa_input" not in st.session_state:
    st.session_state.qa_input = ""
if "rerun_done" not in st.session_state:
    st.session_state.rerun_done = False

# Function to process user query
def process_query():
    user_query = st.session_state.qa_input.strip()
    if user_query:
        st.session_state.chat_history.append(("user", user_query))
        try:
            # resp = requests.post(f"{BACKEND_URL}/ask/", json={"question": user_query})
            history_text = [msg for role, msg in st.session_state.chat_history if role == "user"]
            resp = requests.post(
                f"{BACKEND_URL}/ask/",
                json={
                    "question": user_query,
                    "chat_history": history_text  # send chat history
                }
            )
            if resp.status_code == 200:
                answer = resp.json().get("answer")
                st.session_state.chat_history.append(("assistant", answer))
            else:
                st.error("Failed to get answer from backend.")
        except requests.exceptions.RequestException:
            st.error("Connection error: Could not reach backend.")
        # Clear the input field
        st.session_state.qa_input = ""

# UI: Article URL Count 
st.title("🧠 Article Analyzer")
st.sidebar.markdown(
    """
    <div style='text-align: center; font-weight: 800; font-size: 25px;'>
        Provide <span style='color: blue;'>Articles</span> and 
        <span style='background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); 
                     -webkit-background-clip: text; 
                     color: transparent;'>Analyse</span>
    </div>
    <hr style='border: 2px solid #ccc; margin-top: 8px; margin-bottom: 16px;'>
    """,
    unsafe_allow_html=True
)

# ⏹️ Sidebar toggle
# st.sidebar.title("Select an Input Method:")
input_mode = st.sidebar.radio("**Choose an option**", ["URL", "File", "YouTube", "Audio"])
# ⏹️ Main area dynamically changes based on sidebar selection
if input_mode == "URL":
    with st.container(border=True):
        st.sidebar.title("📄 Process Article from URL")
        num_urls = st.sidebar.number_input("**How many articles you want to analyze** (_max 5_)?", min_value=1, max_value=5, value=1)
        # Sync URL Input List Length
        if len(st.session_state.url_inputs) != num_urls and not st.session_state.rerun_done:
            current_inputs = st.session_state.url_inputs
            st.session_state.url_inputs = current_inputs[:num_urls] + [""] * (num_urls - len(current_inputs))
            st.rerun()  # Ensures correct number of input boxes
        if len(st.session_state.url_inputs) == num_urls:
            st.session_state.rerun_done = False

        # URL Input Section
        for i in range(num_urls):
            st.session_state.url_inputs[i] = st.sidebar.text_input(f"Article {i+1}", key=f"url_input_{i}")

        if st.sidebar.button("🔎 **Process Articles** 🔗"):
            urls = [url for url in st.session_state.url_inputs if url.strip()!=""]
            if urls:
                with st.spinner("Processing URLs..."):
                    response = requests.post(f"{BACKEND_URL}/process-urls/", json={"urls": urls})
                    if response.status_code == 200:
                        st.session_state.ready_for_qa = True
                        st.session_state.chat_history = []
                        st.success("URLs processed and embedded.")
                    else:
                        st.error("Failed to process URLs.")
                # st.success("URL Processing Completed")
                st.json(response.json())
            else:
                st.warning("Please enter at least one valid URL.")

elif input_mode == "File":
    st.sidebar.title("📄 Process Uploaded Article")
    with st.sidebar.container():
        uploaded_file = st.sidebar.file_uploader("**Choose a file**", type=["txt", "pdf", "docx", "csv","xls", "xlsx"])
        procss_button = st.sidebar.button("📁📝 **Upload and Process** 🧠")
        if uploaded_file and procss_button:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            with st.spinner("Processing file..."):
                response = requests.post(f"{BACKEND_URL}/process-file/", files=files)
                if response.status_code == 200:
                    st.success("File processed and embedded.")
                    st.session_state.ready_for_qa = True
                    st.session_state.chat_history = []
                else:
                    st.error("Failed to process uploaded.")
                # st.success("File Processing Completed")
                st.json(response.json())

elif input_mode == 'YouTube':
    st.sidebar.title("📺 Process YT URL")
    with st.sidebar.container():
        yt_url = st.sidebar.text_input("**Enter YouTube URL:**")
        procss_button = st.sidebar.button("📹🔊 **Process YT Link** 🛠️")
        if yt_url and procss_button:
            response = requests.post(f"{BACKEND_URL}/process-yt/", json={"yt_url": yt_url})
            if response.status_code == 200:
                st.success("YT Link processed and embedded.")
                st.session_state.ready_for_qa = True
                st.session_state.chat_history = []
            else:
                st.error("Failed to process YT Link.")
            st.json(response.json())

elif input_mode == "Audio":
    st.sidebar.title("🎙️ Process Uploaded Audio")
    with st.sidebar.container():
        audio_file = st.sidebar.file_uploader("Upload audio file", type=["mp3", "wav", "m4a"])
        procss_button = st.sidebar.button("📼 Upload & Process Audio 🚀")
        if audio_file and procss_button:
            files = {"file": audio_file}
            with st.spinner("Processing audio..."):
                response = requests.post(f"{BACKEND_URL}/process-audio/", files=files)
                if response.status_code == 200:
                    st.success("Audio Processed & Embedded.")
                    st.session_state.ready_for_qa = True
                    st.session_state.chat_history = []
                else:
                    st.error("Failed to process uploaded file.")
                # st.success("File Processing Completed")
                st.json(response.json())

# Sidebar: Clear Chat and Reset Buttons 
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.qa_input = ""  # Clear input box
with col2:
    if st.button("🔄 Reset"):
        try:
            response = requests.post(f"{BACKEND_URL}/reset/")
            if response.status_code == 200:
                st.success("System reset. Please reprocess articles.") 
                st.session_state.ready_for_qa = False
                st.session_state.chat_history = []
                if st.session_state.url_inputs:
                    st.session_state.url_inputs = [""]  # Reset URLs too
                st.session_state.qa_input = ""  # Reset input box
            else:
                st.error("Reset failed.")
        except requests.exceptions.RequestException:
            st.error("Connection error: Could not reach backend.")


# Chat Section
with st.container(height =700,border=True):
    st.write("📜 **Chat History** 🕘")
    if st.session_state.get("ready_for_qa"):
        st.subheader("💬 Ask Questions")
        # Display chat history
        for speaker, msg in st.session_state.chat_history:
            if speaker == "user":
                st.markdown(f"**You:** {msg}")
            else:
                st.markdown(f"**Assistant:**\n\n {msg}")
        # Question input 
        with st.form(key='qa_form',clear_on_submit=True):
            user_query=st.text_input( "Type your question:",key="qa_input",placeholder="Ask something about the articles...")
            st.form_submit_button('Ask',on_click=process_query)





    
    # user_query = st.text_input("Type your question:", value=st.session_state.qa_input, placeholder="Ask something about the articles...")
    # st.session_state.qa_input = user_query
    # send_disabled = not user_query.strip()

    # if st.button("Send", disabled=send_disabled):
    #     st.session_state.chat_history.append(("user", user_query))
    #     st.session_state.qa_input = ""
    #     with st.spinner("Getting answer..."):
    #         try:
    #             resp = requests.post(f"{BACKEND_URL}/ask/", json={"question": user_query})
    #             if resp.status_code == 200:
    #                 answer = resp.json()["answer"]
    #                 st.session_state.chat_history.append(("assistant", answer))
    #             else:
    #                 st.error("Failed to get answer from backend.")
    #         except requests.exceptions.RequestException:
    #             st.error("Connection error: Could not reach backend.")
    #     st.session_state.qa_input = ""

# def process_query(user_query):
#     if not user_query.strip():
#         return

#     st.session_state.chat_history.append(("user", user_query))
#     try:
#         with st.spinner("Getting answer..."):
#             resp = requests.post(f"{BACKEND_URL}/ask/", json={"question": user_query})
#             if resp.status_code == 200:
#                 answer = resp.json()["answer"]
#                 st.session_state.chat_history.append(("assistant", answer))
#             else:
#                 st.error("Failed to get answer from backend.")
#     except requests.exceptions.RequestException:
#         st.error("Connection error: Could not reach backend.")
#     # Clear input after query
#     st.session_state.qa_input = ""


# import streamlit as st
# import requests

# # Backend URLs
# BACKEND_URL = "http://localhost:8000"

# # UI: Article URL Count 
# st.title("🧠 Article Analyzer")
# st.sidebar.title("Choose how many articles you want to analyze (max 5)")
# num_urls =  st.sidebar.number_input("How many articles?", min_value=1, max_value=5, value=1)

# # Session State Initialization 
# if "url_inputs" not in st.session_state:
#     st.session_state.url_inputs = [""] * num_urls
# if "ready_for_qa" not in st.session_state:
#     st.session_state.ready_for_qa = False
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
# if 'qa_input' not in st.session_state:
#     st.session_state.qa_input = ""

# # Sync URL Input List Length
# if len(st.session_state.url_inputs) != num_urls:
#     current_inputs = st.session_state.url_inputs
#     st.session_state.url_inputs = current_inputs[:num_urls] + [""] * (num_urls - len(current_inputs))
#     st.rerun()  # Ensures correct number of input boxes

# # URL Input Section 
# # st.sidebar.text_input("Paste Article URLs")
# for i in range(num_urls):
#     st.session_state.url_inputs[i] = st.sidebar.text_input(f"Article {i+1}",key=f"url_input_{i}")

# # Process Articles Button
# if st.sidebar.button("Process Articles"):
#     urls = [u for u in st.session_state.url_inputs if u.strip() != ""]
#     if urls:
#         with st.spinner("Processing articles and embedding..."):
#             try:
#                 response = requests.post(f"{BACKEND_URL}/process-urls/", json={"urls": urls})
#                 if response.status_code == 200:
#                     st.success("Articles processed and embedded.")
#                     st.session_state.ready_for_qa = True
#                     st.session_state.chat_history = []
#                 else:
#                     st.error("Failed to process URLs.")
#             except requests.exceptions.RequestException:
#                 st.error("Connection error: Could not reach backend.")
#     else:
#         st.warning("Please enter at least one valid URL.")

# # Sidebar: Clear Chat Button
# if st.sidebar.button("🧹 Clear Chat"):
#     st.session_state.chat_history = []
#     st.session_state.qa_input = ""  # Clear input box

# # Sidebar: Reset Button 
# if st.sidebar.button("🔄 Reset"):
#     try:
#         response = requests.post(f"{BACKEND_URL}/reset/")
#         if response.status_code == 200:
#             st.success("System reset. Please reprocess articles.")
#             st.session_state.ready_for_qa = False
#             st.session_state.chat_history = []
#             st.session_state.url_inputs = [""] * num_urls  # Reset URLs too
#             st.session_state.qa_input = ""
#         else:
#             st.error("Reset failed.")
#     except requests.exceptions.RequestException:
#         st.error("Connection error: Could not reach backend.")

# # Chat Section 
# if st.session_state.get("ready_for_qa"):
#     st.subheader("💬 Ask Questions")

#     # Display chat history
#     for speaker, msg in st.session_state.chat_history:
#         if speaker == "user":
#             st.markdown(f"**You:** {msg}")
#         else:
#             st.markdown(f"**Assistant:** {msg}")

#     # Question input and send button
#     with st.form(key="qa_form", clear_on_submit=True, enter_to_submit=False):
#         user_query = st.text_input("Type your question:", value=st.session_state.qa_input, placeholder="Ask something about the articles...")
#         submit = st.form_submit_button("Send")

#         if submit and user_query.strip():
#             st.session_state.chat_history.append(("user", user_query))
#             with st.spinner("Getting answer..."):
#                 try:
#                     resp = requests.post(f"{BACKEND_URL}/ask/", json={"question": user_query})
#                     if resp.status_code == 200:
#                         answer = resp.json()["answer"]
#                         st.session_state.chat_history.append(("assistant", answer))
#                     else:
#                         st.error("Failed to get answer from backend.")
#                 except requests.exceptions.RequestException:
#                     st.error("Connection error: Could not reach backend.")

