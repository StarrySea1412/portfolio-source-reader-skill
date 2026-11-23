"""Synthetic approval counter, revision demo-r3; sequential calls only."""


def approve(accepted, item_id):
    if item_id in accepted:
        return "already_approved"
    accepted.add(item_id)
    return "approved"
