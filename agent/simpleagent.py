from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

load_dotenv()

def get_company_symbol(company: str) -> str:
    """Use this function to get the symbol for a company.

    Args:
        company (str): The name of the company.

    Returns:
        str: The symbol for the company.
    """
    symbols = {
        "Phidata": "MSFT",
        "Infosys": "INFY",
        "Tesla": "TSLA",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Google": "GOOGL",
        "Reliance": "RELIANCE",
    }
    return symbols.get(company, "Unknown")


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True),get_company_symbol],
    show_tool_calls=True,
    markdown_mode=True,
    instructions=['use tables to display the data',
    'if you dont know copmany symbol use this function get_company_symbol else if you have use urself']
)

agent.print_response("Summarize the news for the stock of Apple and compare it with that of Reliane and about there ceo networth")