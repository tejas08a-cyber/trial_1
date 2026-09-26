import json
import streamlit as st
from google import genai


# -----------------------------
# LOAD RECIPES
# -----------------------------

with open("recipes.json", "r", encoding="utf-8") as file:
    recipes = json.load(file)


# -----------------------------
# CONNECT TO GEMINI
# -----------------------------

client = genai.Client()


# -----------------------------
# FIND RELEVANT RECIPES
# -----------------------------

def find_relevant_recipes(question):

    question = question.lower()
    matches = []

    for recipe in recipes:

        recipe_text = json.dumps(recipe).lower()

        words = question.split()

        for word in words:

            if len(word) >= 4 and word in recipe_text:
                matches.append(recipe)
                break

    return matches


# -----------------------------
# ASK GEMINI
# -----------------------------

def ask_ai(question):

    matching_recipes = find_relevant_recipes(question)

    if not matching_recipes:
        return "I don't have that information in your recipe book."

    recipe_context = json.dumps(
        matching_recipes,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are Mom's Recipe Assistant.

Answer the user's question using ONLY the recipe information
provided below.

VERY IMPORTANT:

- Never invent ingredients.
- Never invent quantities.
- Never change quantities.
- Never convert units unless explicitly asked.
- If the recipe says "2 tsp", answer "2 tsp".
- If the recipe says "30 g", answer "30 g".
- If the requested information is not present, say:
  "I don't have that information in your recipe book."
- Keep answers short and easy to understand.

RECIPE INFORMATION:

{recipe_context}

USER QUESTION:

{question}
"""

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    return interaction.output_text


# -----------------------------
# WEBSITE
# -----------------------------

st.set_page_config(
    page_title="Mom's Recipe AI",
    page_icon="🍳",
    layout="centered"
)

st.title("🍳 Mom's Recipe AI")

st.write(
    "Ask me anything about the recipes in your recipe book."
)


# -----------------------------
# CHAT HISTORY
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# -----------------------------
# CHAT INPUT
# -----------------------------

question = st.chat_input(
    "Ask about a recipe..."
)


if question:

    # Show user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)


    # Get AI answer
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_ai(question)

        st.write(answer)


    # Save AI message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
