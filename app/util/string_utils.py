"""Utility class for string operations"""

def escape_linefeed(content: str)->str:
    """Replace linefeed characters with the escape sequence"""
    return content.replace("\n", "\\n")


def trunc_right(content: str, length :int= 100)->str:
    """Limit the string length to the specified number of characters"""
    if len(content) > length:
        return content[:length] + "..."
    return content


def trunc_left(content: str, length :int= 100)->str:
    """Limit the string length to the specified number of characters"""
    if len(content) > length:
        return content[length:] + "..."
    return content


def trunc_middle(content: str, length :int= 100)->str:
    """Limit the string length to the specified number of characters"""
    if content is None:
        return None
    if len(content) > length:
        return content[:length//2]+"\n...(truncated)...\n"+content[-length//2:]
    return content
