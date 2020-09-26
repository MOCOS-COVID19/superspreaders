import streamlit as st
from src.webscrapping import downloader
from src.ner import processor


proc = processor.ArticleProcessor()

st.title('Superspreaders of COVID-19 in Poland')

if __name__ == '__main__':
    input = st.empty()
    url = input.text_input('URL:')

    st.write(url)
    article = downloader.fetch_with_newspaper(url)

    st.header('Title')
    st.write(article.title)

    st.subheader('Published')
    st.write(article.publish_date)

    st.subheader('Meta description')
    st.write(article.meta_description)

    st.subheader('Text')
    st.write(article.text)

    st.markdown('---')
    st.subheader('Found information')
    if article is not None:
        information = proc.run([article.title, article.meta_description, article.text])
        st.write(information)



