import streamlit as st
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from textwrap import dedent
from stream import StreamToStreamlit
import sys
import os

def main():
    st.sidebar.title('Customization')
    api = st.sidebar.selectbox(
        'Choose an API',
        ['Groq', 'OpenAI', 'Anthropic']
    )

    api_key = st.sidebar.text_input('Enter API Key', 'gsk-')

    temp = st.sidebar.slider("Model Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    if api == 'Groq':
        model = st.sidebar.selectbox(
            'Choose a model',
            ['llama3-70b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
        )
        llm = ChatGroq(temperature=temp, model_name=model, groq_api_key=api_key)
    elif api == 'OpenAI':
        model = st.sidebar.selectbox(
            'Choose a model',
            ['gpt-4-turbo', 'gpt-4-1106-preview', 'gpt-3.5-turbo-0125']
        )
        llm = ChatOpenAI(temperature=temp, openai_api_key=api_key, model_name=model)
    elif api == 'Anthropic':
        model = st.sidebar.selectbox(
            'Choose a model',
            ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
        )
        llm = ChatAnthropic(temperature=temp, anthropic_api_key=api_key, model_name=model)

    st.title('Real-time Price Comparison App')
    st.markdown("Compare product prices across multiple stores in real-time.")

    # Agent Definitions
    search_agent = Agent(
        role="Search Query Optimizer",
        backstory="Expert in optimizing search queries for e-commerce platforms.",
        goal="Improve search queries to find exact product matches across different platforms.",
        allow_delegation=True,
        verbose=True,
        llm=llm
    )

    price_agent = Agent(
        role="Price Analyzer",
        backstory="Specialist in comparing prices and identifying the best deals.",
        goal="Analyze prices from different sources and provide insights on the best options.",
        allow_delegation=True,
        verbose=True,
        llm=llm
    )

    data_agent = Agent(
        role="Data Retrieval Specialist",
        backstory="Expert in retrieving real-time data from various e-commerce platforms and local stores.",
        goal="Efficiently fetch accurate pricing data from multiple sources.",
        allow_delegation=True,
        verbose=True,
        llm=llm
    )

    search_query = st.text_input("Enter product name or SKU")

    if search_query and api_key:
        if st.button("Search"):
            optimize_task = Task(
                description=f"Optimize the search query: '{search_query}' for best results across different e-commerce platforms.",
                expected_output="An optimized search query string.",
                agent=search_agent,
            )

            retrieve_task = Task(
                description="Retrieve price data for the optimized query from Amazon, AliExpress, and Kuwaiti stores.",
                expected_output="A list of product prices from different sources.",
                agent=data_agent,
                context=[optimize_task],
            )

            analyze_task = Task(
                description="Analyze the retrieved price data and provide insights on the best options.",
                expected_output="A summary of price comparisons and recommendations.",
                agent=price_agent,
                context=[retrieve_task],
            )

            crew = Crew(
                agents=[search_agent, data_agent, price_agent],
                tasks=[optimize_task, retrieve_task, analyze_task],
                verbose=2,
                process=Process.sequential,
                manager_llm=llm
            )

            with st.spinner("Searching for the best prices..."):
                original_stdout = sys.stdout
                sys.stdout = StreamToStreamlit(st)

                result = ""
                result_container = st.empty()
                for delta in crew.kickoff():
                    result += delta
                    result_container.markdown(result)

                sys.stdout = original_stdout

            st.success("Search complete!")
            st.write(result)

if __name__ == "__main__":
    main()