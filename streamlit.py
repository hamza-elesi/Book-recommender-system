# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np

# Load the data files
books = pd.read_pickle("books.pkl")
pt = pd.read_pickle("pt.pkl")
similarity_scores = pd.read_pickle("similarity_scores.pkl")

def recommend(book_name):
    if book_name not in pt.index:
        return "Book not found in the index. Please provide a valid book name."

    index = np.where(pt.index == book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))
        data.append(item)

    return data

# Streamlit UI
st.title('Book Recommender System')

book_name = st.text_input("Enter a book name")

if st.button('Recommend'):
    recommendations = recommend(book_name)
    if recommendations == "Book not found in the index. Please provide a valid book name.":
        st.error(recommendations)
    else:
        for i, recommendation in enumerate(recommendations, 1):
            st.write(f"{i}. **{recommendation[0]}** by {recommendation[1]}")
            if recommendation[2]:  # Check if image URL is available
                st.image(recommendation[2], width=100)  # Display the book cover image
            else:
                st.write("No image available")