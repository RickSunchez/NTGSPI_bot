import json
import numbers
import sqlite3
from typing import Tuple, Union
from local_modules.path_worker.path_search import pathSearcher
from local_modules.site_parser.NTGSPIparser import Parser

from sql_queries import SQL

# TODO:
# - add check for only one point with no parent
# - add last message hash
# - add update to last timestamp

class DBhandler:
    def __init__(self, db_file:str, renew:bool=False) -> Exception:
        self.bdFile = db_file
        if renew:
            self.drop()
            self.init()
            self.generate()

    def init(self) -> None:
        for query in SQL.CREATETables():
            self.sql(query)
    
    def drop(self):
        for query in SQL.DROP():
            self.sql(query)

    def sql(self, query:str) -> Tuple[list, int]:
        try:
            conn = sqlite3.connect(self.bdFile)
            cursor = conn.cursor()

            if "DROP" in query:
                cursor.execute(query)
                return [], 0
            
            answer = cursor.execute(query).fetchall()
            lastId = cursor \
                .execute("SELECT last_insert_rowid()") \
                .fetchone()[0]

            conn.commit()
            conn.close()

            return answer, lastId
        except Exception as err:
            raise err
    
    # ADD
    def addNewMenuPoint(self, title:str, message:str, parent_id:Union[int, None], point_type:str, point_data:str="") -> int:
        _, lastId = self.sql(SQL.INSERTMenuTable(title, message, point_type, point_data))
    
        if parent_id is not None:
            self.sql(SQL.INSERTLinkTable(parent_id, lastId))
        
        return lastId

    def addNewUser(self, telegram_id:int) -> None:
        answer, _ = self.sql(SQL.SELECTUser(telegram_id))

        if len(answer) == 0:
            self.sql(SQL.INSERTUserTable(telegram_id))
    
    # GET
    def getChildOf(self, parent_id:int) -> object:
        answer, _ = self.sql(SQL.SELECTPointsByParent(parent_id))
        out = {}

        for row in answer:
            out[row[0]] = {
                "title": row[1],
                "message": row[2],
                "data": row[4],
                "type": row[3]
            }
        
        return out

    def getPoint(self, point_id:int) -> object:
        answer, _ = self.sql(SQL.SELECTPoint(point_id))

        return {
            "id": answer[0][0],
            "title": answer[0][1],
            "message": answer[0][2],
            "type": answer[0][2],
            "data": answer[0][3],
        }
    
    def getUserStorage(self, telegram_id:int) -> object:
        answer, _ = self.sql(SQL.SELECTUserStorage(telegram_id))

        return json.loads(answer[0][0].replace("''", "\""))

    def generate(self):
        rootId = self.addNewMenuPoint("root", "Основное меню:", None, "")

        sheduleId = self.addNewMenuPoint(
            title="Расписание", 
            message="Выберите факультет", 
            parent_id=rootId, 
            point_type="callback")
        contactsId = self.addNewMenuPoint(
            title="Контакты", 
            message="???", 
            parent_id=rootId, 
            point_type="callback")
        templatesId = self.addNewMenuPoint(
            title="Шаблоны документов", 
            message="???", 
            parent_id=rootId, 
            point_type="callback")
        navigationId = self.addNewMenuPoint(
            title="Навигация по ФЕМИ", 
            message="Выберите кабинет, который ближе всего к вам:", 
            parent_id=rootId, 
            point_type="callback")

        np = Parser()
        ps = pathSearcher()

        for f in np.getFacultetList():
            fId = self.addNewMenuPoint(
                title=f, 
                message="Выберите группу", 
                parent_id=sheduleId, 
                point_type="callback")

            for g in np.getFacultetGroups(f):
                gId = self.addNewMenuPoint(
                    title=g, 
                    message="Расписание группы %s" % g, 
                    parent_id=fId, 
                    point_type="callback")

                sheduleLink = np.getGroupShedule(g)
                self.addNewMenuPoint(
                    title=g,
                    message="link",
                    parent_id=gId,
                    point_type="link", 
                    point_data=sheduleLink
                )

        for dep in np.numbers():
            depId = self.addNewMenuPoint(
                title=dep["title"],
                message="test",
                parent_id=contactsId,
                point_type="callback"
            )

            for sub in dep["subs"]:
                point_data = "Ответственный: %s\nТелефон: %s\nemail: %s\nСайт: %s\n" % (
                    sub["head"], sub["phone"], sub["mail"], sub["site"]
                )
                subId = self.addNewMenuPoint(
                    title=sub["name"],
                    message="test",
                    parent_id=depId,
                    point_type="callback",
                )

                self.addNewMenuPoint(
                    title=sub["name"],
                    message="test",
                    parent_id=subId,
                    point_type="message",
                    point_data=point_data
                )

        for t in np.getTemplatesTitles():
            tId = self.addNewMenuPoint(
                title=t,
                message="test",
                parent_id=templatesId,
                point_type="callback"
            )

            for doc in np.getTemplateList(t):
                title = doc["name"].replace("образец заявления_", "", 1)
                docId = self.addNewMenuPoint(
                    title=title,
                    message="test",
                    parent_id=tId,
                    point_type="callback",
                )

                self.addNewMenuPoint(
                    title=title,
                    message="test",
                    parent_id=docId,
                    point_type="message",
                    point_data=doc["link"]
                )

        rowSize = 5
        count = 0
        for l in ps.legend:
            if "e" in ps.legend[l]: continue
            row = count // rowSize
            col = count % rowSize
            count += 1

            self.addNewMenuPoint(
                title=ps.legend[l],
                message="test",
                parent_id=navigationId,
                point_type="grid?row=%d&col=%d&map=%s" % (row, col, l)
            )

            # print(ps.legend[l])
