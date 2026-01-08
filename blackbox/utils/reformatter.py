from datetime import datetime

def format_date(date_str: str) -> str:
    """
    Convert a date string from 'YYYY-MM-DDTHH:MM:SS.sssZ' format to 'DD-Mon-YYYY'.
    
    Args:
    date_str (str): The date string in the original format.
    
    Returns:
    str: The formatted date string.
    """
    # Step 1: Parse the date string
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Step 2: Format the date object to the desired format
    formatted_date = date_obj.strftime("%d-%b-%Y")
    
    return formatted_date