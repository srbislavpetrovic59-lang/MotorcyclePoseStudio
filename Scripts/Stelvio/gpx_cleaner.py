def remove_immediate_backtracks(points):
    """
    Uklanja uzastopne duplikate i neposredne
    povratne petlje A -> B -> A.

    Ne menja originalnu listu.
    """
    cleaned = []

    for point in points:
        if cleaned and point == cleaned[-1]:
            continue

        if len(cleaned) >= 2 and point == cleaned[-2]:
            cleaned.pop()
            continue

        cleaned.append(point)

    return cleaned