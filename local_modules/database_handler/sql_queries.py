class SQL:
    def CREATETables() -> list:
        return [
            """
                CREATE TABLE IF NOT EXISTS menu(
                    point_id INTEGER PRIMARY KEY,
                    title TEXT,
                    message TEXT,
                    point_type TEXT,
                    point_data TEXT,
                    last_action INTEGER
                )
            """,
            """
                CREATE TABLE IF NOT EXISTS links(
                    parent_id INTEGER,
                    child_id INTEGER
                )
            """,
            """
                CREATE TABLE IF NOT EXISTS users(
                    telegram_id INTEGER,
                    current_path TEXT,
                    storage TEXT
                )
            """
        ]
    
    def DROP() -> list:
        return [
            "DROP TABLE IF EXISTS menu",
            "DROP TABLE IF EXISTS links",
            "DROP TABLE IF EXISTS users"
        ]
    
    # INSERT
    def INSERTMenuTable(title:str, message:str, point_type:str, point_data:str="") -> str:
        return """
            INSERT INTO menu (title, message, point_type, point_data)
            VALUES ("{0}", "{1}", "{2}", "{3}")
        """.format(title, message, point_type, point_data)

    def INSERTLinkTable(parent_id:int, child_id:int) -> str:
        return """
            INSERT INTO links (parent_id, child_id)
            VALUES (%d, %d)
        """ % (parent_id, child_id)

    def INSERTUserTable(telegram_id:int) -> str:
        return """
            INSERT INTO users (telegram_id, current_path, storage)
            VALUES (%d, "1", "")
        """ % telegram_id

    # SELECT
    def SELECTPointsByParent(parent_id:int) -> str:
        return """
            SELECT point_id, title, message, point_type, point_data FROM menu
            WHERE point_id IN (
                SELECT child_id FROM links
                WHERE parent_id=%d
            )
        """ % parent_id

    def SELECTTitlesOf(point_ids:list) -> str:
        return """
            SELECT title FROM menu
            WHERE point_id IN [%s]
        """ % (",".join(point_ids))

    def SELECTUser(telegram_id:int) -> str:
        return """
            SELECT * FROM users
            WHERE telegram_id=%d
        """ % telegram_id

    def SELECTUserPath(telegram_id:int) -> str:
        return """
            SELECT current_path FROM users
            WHERE telegram_id=%d
        """ % telegram_id
    
    def SELECTUserStorage(telegram_id:int) -> str:
        return """
            SELECT storage FROM users
            WHERE telegram_id=%d
        """ % telegram_id

    def SELECTPoint(point_id:int) -> str:
        return """
            SELECT * FROM menu
            WHERE point_id=%d
        """ % point_id

    # UPDATE
    def UPDATEUserPath(telegram_id:int, new_path:str) -> str:
        return """
            UPDATE users
            SET current_path="%s"
            WHERE telegram_id=%d
        """ % (new_path, telegram_id)

    def UPDATEUserStorage(telegram_id:int, storage:str) -> str:
        return """
            UPDATE users
            SET storage="%s"
            WHERE telegram_id=%d
        """ % (storage, telegram_id)