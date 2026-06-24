"""
TaaS (Taste-as-a-Service) is a Streamlit app that uses the Anthropic API
to generate film recommendations based on a user's aesthetic sensibility,
as expressed through prose. Instead of relying on genre tags or
collaborative filtering, TaaS analyzes how users describe films they love
and infers their underlying taste profile to suggest new films they might
enjoy.
"""

import os
import json
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT, build_user_prompt

# Loads API key from .env into environment
load_dotenv()

# The Anthropic client picks up ANTHROPIC_API_KEY from the environment
client = Anthropic()
MODEL = "claude-sonnet-4-5"

def get_recommendations(film_descriptions: str) -> dict:
    """
    Sends the user's film descriptions to Claude and returns the parsed
    taste profile + recommendations as a dict.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_user_prompt(film_descriptions)},
            # Prefill: forces Claude to continue from "{", making valid JSON output near-guaranteed
            {"role": "assistant", "content": "{"},
        ],
    )

    raw_text = response.content[0].text
    # Because we prefilled with "{", we need to re-add it to the front
    full_json_text = "{" + raw_text

    # Defensive extraction: find the JSON object even if there's trailing content
    start = full_json_text.find("{")
    end = full_json_text.rfind("}") + 1
    json_substring = full_json_text[start:end]

    return json.loads(json_substring)

# Streamlit UI 
st.set_page_config(page_title="TaaS: Taste as a Service", page_icon="🎬")

st.title("TaaS (Taste as a Service)")
st.subheader("Film recommendations grounded in aesthetic, not genre.")

st.markdown(
    """
    Most recommenders match on genre tags or collaborative filtering. TaaS
    reads how you *talk* about films you love, infers the underlying aesthetic
    sensibility, and recommends against that sensibility.
    
    Describe **2–3 films you love** and *why*. The more you
    say about what elements or cinematic styles you actually responded to (pacing, mood, visual feel, emotional
    register), the better the inference.
    """
)

user_input = st.text_area(
    label="Films you love, and why:",
    placeholder=(
        "e.g. 'I love Paris, Texas because of the silences and the way Wenders lets "
        "landscapes carry emotional weight without dialogue. And Lost in Translation, "
        "for the same reason: that ambient loneliness, the texture of a city at night, "
        "characters who don't quite say what they mean...'"
    ),
    height=200,
)

# Initialize session state so results persist across Streamlit's reruns
if "result" not in st.session_state:
    st.session_state.result = None
if "error" not in st.session_state:
    st.session_state.error = None

if st.button("Read my taste", type="primary"):
    if not user_input.strip():
        st.warning("Tell me about at least one film first.")
    else:
        st.session_state.result = None
        st.session_state.error = None
        with st.spinner("Reading your taste..."):
            try:
                st.session_state.result = get_recommendations(user_input)
            except json.JSONDecodeError:
                st.session_state.error = (
                    "The model returned a response I couldn't parse as JSON. "
                    "Try rephrasing your input or running it again."
                )
            except Exception as e:
                st.session_state.error = f"Something went wrong: {e}"

# Render results from session state 
if st.session_state.error:
    st.error(st.session_state.error)
elif st.session_state.result:
    result = st.session_state.result

    st.markdown("### What I'm hearing about your taste")
    st.markdown(f"*{result['taste_profile']}*")

    st.divider()

    st.markdown("### Films you might love")
    for rec in result["recommendations"]:
        st.markdown(f"**{rec['title']}** ({rec['year']}) — dir. {rec['director']}")
        st.markdown(rec["reasoning"])
        st.markdown("")