import re
import streamlit as st

class StreamToStreamlit:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []        
        self.colors = ['red', 'green', 'blue', 'orange']
        self.color_index = 0

    def write(self, data):
        # Filter out ANSI escape codes
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check for task information
        task_match = re.search(r'(\"task\"\s*:\s*\"(.*?)\"|task\s*:\s*([^\n]*))', cleaned_data, re.IGNORECASE)
        if task_match:
            task_value = task_match.group(2) or task_match.group(3)
            st.info(f":gear: Task: {task_value.strip()}")

        # Apply color coding for different agents and processes
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            self.color_index = (self.color_index + 1) % len(self.colors)
            cleaned_data = cleaned_data.replace(
                "Entering new CrewAgentExecutor chain",
                f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]"
            )

        # Color coding for our specific agents
        agent_colors = {
            "Search Query Optimizer": "blue",
            "Price Analyzer": "green",
            "Data Retrieval Specialist": "orange"
        }

        for agent, color in agent_colors.items():
            if agent in cleaned_data:
                cleaned_data = cleaned_data.replace(agent, f":{color}[{agent}]")

        # Highlight important information
        if "price:" in cleaned_data.lower():
            price_match = re.search(r'price:\s*([\d.]+)', cleaned_data, re.IGNORECASE)
            if price_match:
                price = price_match.group(1)
                cleaned_data = cleaned_data.replace(
                    f"price: {price}",
                    f":green[Price: ${price}]"
                )

        if "best deal" in cleaned_data.lower():
            cleaned_data = re.sub(
                r'(best deal.*)',
                r':star: \1',
                cleaned_data,
                flags=re.IGNORECASE
            )

        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Finished chain.",
                f":{self.colors[self.color_index]}[Finished chain.]"
            )

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
