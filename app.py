import os
import queue
import threading

import streamlit as st

from embedchain import App
from embedchain.config import BaseLlmConfig
from embedchain.helpers.callbacks import (StreamingStdOutCallbackHandlerYield,
                                          generate)

@st.cache_resource
def finfluencers_ai():
    app = App()
    return app


# Function to read the CSV file row by row
# def read_csv_row_by_row(file_path):
#     with open(file_path, mode="r", newline="", encoding="utf-8") as file:
#         csv_reader = csv.DictReader(file)
#         for row in csv_reader:
#             yield row


@st.cache_resource
def add_data_to_app():
    app = finfluencers_ai()
    # with open("personal_finance.txt", "r") as f:
    #     for row in f.readlines():
    #         print(row)
    #         app.add(row, data_type="youtube_video")

    app.add("@CARachanaRanade", data_type="youtube_channel")
    app.add("@varsitybyzerodha", data_type="youtube_channel")
    app.add("@financewithsharan", data_type="youtube_channel")
    app.add("@AkshatZayn", data_type="youtube_channel")
    app.add("@warikoo", data_type="youtube_channel")
    app.add("@pranjalkamra", data_type="youtube_channel")
    app.add("@nehanagar", data_type="youtube_channel")
    
    # url = "https://gist.githubusercontent.com/deshraj/50b0597157e04829bbbb7bc418be6ccb/raw/95b0f1547028c39691f5c7db04d362baa597f3f4/data.csv"  # noqa:E501
    # response = requests.get(url)
    # csv_file = StringIO(response.text)
    # for row in csv.reader(csv_file):
    #     if row and row[0] != "url":
    #         app.add(row[0], data_type="web_page")
    # finfluencers_youtube_videos = ["pranjalkamraYoutubeVideos.txt"] #, "rajshamaniYoutubeVideos.txt", "zerodhaonlineYoutubeVideos.txt"]
    
    # for filename in finfluencers_youtube_videos:
    #     with open(filename, "r") as f:
    #         for row in f.readlines():
    #             if row and row[0] != "URL":
    #                 app.add(row[0], data_type="youtube")



app = finfluencers_ai()
add_data_to_app()
# app.add("@pranjalkamra", data_type="youtube_channel")


# assistant_avatar_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Sadhguru-Jaggi-Vasudev.jpg/640px-Sadhguru-Jaggi-Vasudev.jpg"  # noqa: E501


st.title("🤑 Finfluencer AI")

styled_caption = '<p style="font-size: 17px; color: #aaa;">🚀 An AI Assistant powered with Finfluencer\'s content!</p>'  # noqa: E501
st.markdown(styled_caption, unsafe_allow_html=True)  # noqa: E501


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
                Hi, I'm Finfluencer AI! As your Finfluencer AI, I'm here for all your personal finance queries related to budgeting, investments, tax planning, or financial literacy in India.
            """,  # noqa: E501
        }
    ]

for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar='🤖' if role == "assistant" else '🧑‍💻'):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything!"):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar='🤖'):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""

        q = queue.Queue()

        def app_response(result):
            config = BaseLlmConfig(stream=True, callbacks=[StreamingStdOutCallbackHandlerYield(q)])
            answer, citations = app.chat(prompt, config=config, citations=True)
            result["answer"] = answer
            result["citations"] = citations

        results = {}
        thread = threading.Thread(target=app_response, args=(results,))
        thread.start()

        for answer_chunk in generate(q):
            full_response += answer_chunk
            msg_placeholder.markdown(full_response)

        thread.join()
        answer, citations = results["answer"], results["citations"]
        if citations:
            full_response += "\n\n**Sources**:\n"
            sources = list(set(map(lambda x: x[1]["url"], citations)))
            for i, source in enumerate(sources):
                full_response += f"{i+1}. {source}\n"

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
