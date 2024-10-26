# Import necessary libraries for Streamlit, requests, and the Groq API
import os
import streamlit as st
import requests
import random
import time
import numpy as np
from groq import Groq
from dotenv import load_dotenv

# Load environment variables, especially for GROQ_API_KEY
load_dotenv()

# Initialize Groq client with API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Function to generate words and hints based on the topic using Groq
def get_topic_words_and_hints(topic, count):
    """
    Generates a set of words and hints based on the topic provided.
    :param topic: Topic to generate words about
    :param count: Number of words required
    :return: Dictionary of words with hints
    """
    # Request generation from Groq with a specific topic and count of words
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate {count} unique five-letter words related to {topic} along with hints.",
            }
        ],
        model="llama3-8b-8192",
    )
    
    # Parse the response and separate words from hints
    words_and_hints = chat_completion.choices[0].message.content.splitlines()
    words_dict = {}
    for line in words_and_hints:
        if ':' in line:
            word, hint = line.split(":")
            words_dict[word.strip()] = hint.strip()
    return words_dict

# Function to create crossword grid and fit words with overlap
def create_crossword_grid(words):
    """
    Create a basic crossword grid and places words.
    :param words: List of words to place on the grid
    :return: 2D list representing the grid
    """
    grid_size = max(len(word) for word in words) + 5  # Define grid size
    grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Arrange words on grid with overlap logic
    for word in words:
        placed = False
        attempts = 0
        while not placed and attempts < 10:
            row, col = random.randint(0, grid_size-5), random.randint(0, grid_size-5)
            if all(grid[row][col + i] in ["", word[i]] for i in range(len(word))):
                for i, char in enumerate(word):
                    grid[row][col + i] = char
                placed = True
            attempts += 1
    return grid

# Display the generated crossword grid on Streamlit
def display_crossword_grid(grid):
    """
    Display the crossword grid on Streamlit.
    :param grid: The 2D crossword grid with words
    """
    for row in grid:
        st.write(" ".join([cell if cell else "_" for cell in row]))

# Initialize Streamlit app with title and topic input
st.title("Crossword Puzzle Game")

# Input field for topic and dropdown for word count
topic = st.text_input("Enter a topic (e.g., 'Movies', 'Science', etc.):")
word_count = st.selectbox("Select number of words:", list(range(5, 16)))
difficulty = st.selectbox("Select Difficulty Level:", ["Easy", "Medium", "Hard"])

# Start game button to generate crossword puzzle with topic and word count
if st.button("Generate Crossword"):
    if topic:
        # Fetch words and hints from Groq based on the topic and word count
        words_dict = get_topic_words_and_hints(topic, word_count)
        st.session_state["words"] = list(words_dict.keys())
        st.session_state["hints"] = list(words_dict.values())
        st.session_state["grid"] = create_crossword_grid(st.session_state["words"])

# Timer for gameplay
if "start_time" not in st.session_state:
    st.session_state["start_time"] = None
if st.button("Start Timer"):
    st.session_state["start_time"] = time.time()

# Timer display and elapsed time calculation
if st.session_state["start_time"]:
    elapsed_time = time.time() - st.session_state["start_time"]
    st.write(f"Elapsed Time: {elapsed_time:.2f} seconds")

# Display hints and input fields for each word
if "words" in st.session_state:
    display_crossword_grid(st.session_state["grid"])
    st.write("Hints:")
    user_answers = []
    
    # Loop through hints and get input for each word
    for i, hint in enumerate(st.session_state["hints"]):
        st.write(f"{i+1}. {hint}")
        user_answer = st.text_input(f"Enter word {i+1}:", key=f"user_answer_{i}")
        user_answers.append(user_answer)
    
    # Checking answers for correctness
    correct_answers = sum(1 for i in range(len(st.session_state["words"]))
                          if user_answers[i].strip().lower() == st.session_state["words"][i].strip().lower())
    st.write(f"Correct Answers: {correct_answers}/{word_count}")

    # Scoring system based on correct answers
    score = correct_answers * 10  # Points per correct answer
    st.write(f"Score: {score}")

# Option to reset game
if st.button("Reset Game"):
    st.session_state.clear()
