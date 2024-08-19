
import streamlit as st
from google.generativeai import configure, GenerativeModel
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup

# Streamlit page configuration
st.set_page_config(page_title="HuggingFace and Langchain Integration", page_icon="📝")

# Function to extract transcript from YouTube
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript = None
        try:
            # Attempt to get English transcript
            transcript = transcript_list.find_transcript(['en']).fetch()
        except:
            try:
                # Fall back to Hindi if English is not available
                transcript = transcript_list.find_transcript(['hi']).fetch()
                st.warning("Using Hindi (auto-generated) transcript as English was not available.")
            except:
                st.error("No suitable transcript found.")
                return None

        transcript_text = " ".join([i["text"] for i in transcript])
        return transcript_text
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

# Function to extract text from a website
def extract_website_text(website_url):
    try:
        response = requests.get(website_url)
        response.raise_for_status()  # Check if request was successful
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        return content
    except Exception as e:
        st.error(f"Error fetching website content: {e}")
        return None

# Function to generate summary using Google Gemini API
def generate_summary(content_text, prompt, api_key):
    try:
        configure(api_key=api_key)
        model = GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + content_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit user interface
st.title("HuggingFace and Langchain Integration")

# API Key input
# api_key = st.text_input("Enter your Google API Key:", type="password")
api_key = st.text_input("Enter your HF token:", type="password")

# Option to choose between YouTube and Website
option = st.selectbox("Choose content type:", ["YouTube Video", "Website"])

if option == "YouTube Video":
    youtube_link = st.text_input("Enter YouTube Video Link:")
    if youtube_link:
        video_id = youtube_link.split("v=")[1].split("&")[0]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

        if st.button("Get Detailed Notes"):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video and providing the important summary in points within 250 words. Please provide the summary of the text given here: """
                summary = generate_summary(transcript_text, prompt, api_key)
                if summary:
                    st.markdown("## Detailed Notes:")
                    st.write(summary)

elif option == "Website":
    website_link = st.text_input("Enter Website URL:")
    if website_link:
        if st.button("Get Detailed Notes"):
            content_text = extract_website_text(website_link)
            if content_text:
                prompt = """You are a website summarizer. You will be taking the content of the website and summarizing the entire content and providing the important summary in points within 250 words. Please provide the summary of the content given here: """
                summary = generate_summary(content_text, prompt, api_key)
                if summary:
                    st.markdown("## Detailed Notes:")
                    st.write(summary)

# Additional styling
st.markdown("""
    <style>
    .stTextInput input {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .stImage {
        border: 2px solid #4CAF50;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
