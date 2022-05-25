import json
from dbHandler import DBhandler
from sql_queries import SQL

class Router:
    def __init__(self, db_file:str) -> None:
        self.dbh = DBhandler(db_file, False)

    def pwd(self, telegram_id:int, mode:str="number") -> object:
        out = {"type": "path"}

        answer, _ = self.dbh.sql(SQL.SELECTUserPath(telegram_id))
        pointId = int(answer[0][0].split("/")[-1])

        if pointId >= 9999:
            return {
                "type": "service",
                "action": "calcPath",
                "full_path": answer[0][0]
            }

        if mode == "number":
            out["full_path"] = answer[0][0]
        else:
            accords = self.dbh.sql(SQL.SELECTTitlesOf(answer[0][0].split("/")))
            out["full_path"] = "/".join(accords[0])

        out["point"] = self.dbh.getPoint(pointId)
        out["childs"] = self.dbh.getChildOf(pointId)

        return out

    def cd(self, telegram_id:int, forward_point_id:int):
        answer, _ = self.dbh.sql(SQL.SELECTUserPath(telegram_id))
        newPath = answer[0][0].split("/")

        if newPath[-1] != str(forward_point_id):
            newPath.append(str(forward_point_id))

        self.dbh.sql(SQL.UPDATEUserPath(telegram_id, "/".join(newPath)))

    def back(self, telegram_id:int):
        answer, _ = self.dbh.sql(SQL.SELECTUserPath(telegram_id))
        newPath = answer[0][0].split("/")

        if len(newPath) > 1:
            newPath.pop()

        self.dbh.sql(SQL.UPDATEUserPath(telegram_id, "/".join(newPath)))
    
    def home(self, telegram_id:int):
        self.dbh.sql(SQL.UPDATEUserPath(telegram_id, "1"))

    def touch(self, telegram_id:int, data:object):
        answer, _ = self.dbh.sql(SQL.SELECTUser(telegram_id))

        if answer[0][2] == "": 
            storage = {}
        else:
            storage = json.loads(answer[0][2].replace("''", "\""))

        for key in data:
            storage[key] = data[key]

        self.dbh.sql(
            SQL.UPDATEUserStorage(telegram_id, json.dumps(storage).replace("\"", "''")))