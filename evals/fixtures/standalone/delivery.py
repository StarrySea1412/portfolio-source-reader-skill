"""Synthetic delivery semantics for revision r2."""


def submit(document, send):
    """The transport can time out after the remote side accepts a submission."""
    try:
        receipt = send(document)
    except TimeoutError:
        return {"status": "pending_confirmation", "receipt": None}
    return {"status": "submitted", "receipt": receipt}
