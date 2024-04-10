"""
    Debug messages used through out proxycrawler
    to help in debugging
"""

def EXCEPTION_RAISED_WHEN_VALIDATING_PROXY(proxy, error) -> str:
    return f"[bold blue][DEBUG][reset] Exception raised when validating proxy:[bold green]{proxy}[bold white]. Error: {error}"
