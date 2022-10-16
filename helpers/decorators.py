def bold(text: str):
    return f"**{text}**"

def underline(text: str):
    return f"__{text}__"

def italics(text: str):
    return f"*{text}*"

def strikethrough(text: str):
    return f"~~{text}~~"

def code_line(text: str):
    return  f"``{text}``"
    
def code_block(text: str):
    return f"```{text}```"

def quote_block(text: str):
    return f">{text}"

def multiline_quote_block(text: str):
    return f">>>{text}"