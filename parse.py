import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import quote

class NTGSPIparser:
    def __init__(self):
        self.cache = "./NTGSPI_cache.json"

    def sync(self):
        data = {}

        data["shedule"] = self.__getShedule()
        data["numbers"] = self.__getNumbers()
        data["templates"] = self.__getDocTemplates()

        with open(self.cache, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def getFacultetList(self, real=False):
        data = self.shedule(real)

        l = []
        for f in data:
            l.append(f["facultet"])

        return l

    def getFacultetGroups(self, facultet, real=False):
        data = self.shedule(real)

        names = []
        for f in data:
            if f["facultet"] == facultet:
                for s in f["shedule"]:
                    names.append(s["group"])

                break

        return names

    def getContactsDepartment(self, real=False):
        data = self.numbers(real)

        titles = []
        for d in data:
            titles.append(d["title"])

        return titles
    
    def getTemplatesTitles(self, real=False):
        data = self.templates(real)

        titles = []
        for d in data:
            titles.append(d["title"])

        return titles


    def shedule(self, real=False):
        return self.__getData("shedule", real)
    def numbers(self, real=False):
        return self.__getData("numbers", real)
    def templates(self, real=False):
        return self.__getData("templates", real)
    
    def __getData(self, name, real=False):
        if real:
            if name == "shedule": return self.__getShedule()
            if name == "numbers": return self.__getNumbers()
            if name == "templates": return self.__getDocTemplates()
        else:
            try:
                with open(self.cache, "r") as f:
                    data = json.load(f)
                    return data[name]
            except Exception:
                return False

    def __getShedule(self):
        url = "https://www.ntspi.ru/student/rasp/"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, features="html.parser")

        table = soup \
            .find("h2", string="Расписание занятий") \
            .find_next_sibling("table")

        shedule = []

        isFirst = True
        base = "https://www.ntspi.ru"
        for i, tr in enumerate(table.find_all("tr")):
            if isFirst:
                isFirst = False  
                for td in tr.find_all("td"):
                    shedule.append({
                        "facultet": td.text,
                        "shedule": []
                    })
                continue

            for j, td in enumerate(tr.find_all("td")):
                elemA = td.find_all("a")

                for a in elemA:
                    shedule[j]["shedule"].append({
                        "group": a.text.strip(),
                        "link": quote(base + a["href"])
                    })

        return shedule

    def __getDocTemplates(self):
        url = "https://www.ntspi.ru/student/docs"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, features="html.parser")

        parent = soup \
            .find("h2", text="Образцы документов") \
            .parent

        toFind = ["Образцы заявлений для студентов СПО", "Образцы заявлений для студентов ВО"]
        active = 0
        templates = []
        base = "https://www.ntspi.ru/"
        for children in parent.children:
            if children.text.strip() in toFind:
                templates.append({
                    "title": children.text.strip(),
                    "docs": []
                })
                active = len(templates) - 1
                continue
            
            if children.name == "a":
                l = children["href"].replace("../../", "")

                # self.__getShortUrl(base + quote(l))
                templates[active]["docs"].append({
                    "name": children.text.strip(),
                    "link": base + quote(l)
                })

        return templates

    def __getNumbers(self):
        url = "https://www.ntspi.ru/sveden/struct"

        response = requests.get(url)

        soup = BeautifulSoup(response.text, features="html.parser")

        numbers = []

        for div in soup.find_all("div", {"class": "vikon-row"}):
            title = div.find("h4").text.strip()
            table = div.find("table")

            numbers.append({
                "title": title,
                "subs": []
            })

            for i, tr in enumerate(table.find_all("tr")):
                if i == 0: continue

                td = tr.find_all("td")

                site = "-"
                if td[5].find("a"):
                    site = td[5].find("a")["href"]

                numbers[-1]["subs"].append({
                    "name": td[1].text.strip(),
                    "head": td[2].text.strip(),
                    "phone": td[8].text.strip(),
                    "mail": td[6].text.strip(),
                    "site": quote(site),
                })

        return numbers
