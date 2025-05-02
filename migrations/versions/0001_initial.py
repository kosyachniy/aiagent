def up(db):
    db["business_priorities"].create_index("created_at")


def down(db):
    db["business_priorities"].drop_index("created_at_1")
