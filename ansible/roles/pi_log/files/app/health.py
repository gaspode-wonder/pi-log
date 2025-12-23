def health_check():
    """
    Simple health check endpoint for tests and monitoring.
    Returns a dict with a static OK status.
    """
    return {"status": "ok"}
