import subprocess
import json
import requests
import os
import re

HOME = os.environ['HOME']

def cleanNoteData():
    data = subprocess.run(f"exiftool -FileName -Directory -FileModifyDate {HOME}/Documents/Vimwiki/*/*.*", shell=True, capture_output=True, text=True)\
        .stdout\
        .strip("\n")
    data = re.split(r'\n=|\n\s', data)
    del data[-1]
    note_arr = []

    for item in data:
        note_obj = {}
        for line in item.strip().split("\n"):
            if line.startswith("="):
                continue
            [key, value] = line.split(":", 1)
            if "name" in key.lower():
                note_obj["name"] = value.split(".")[0].strip()
                continue
            if key.startswith("Directory"):
                category = value.split("/")[5].strip()
                note_obj["category"] = category
                continue
            if "modification" in key.lower():
                note_obj["dateAdded"] = value.strip().split()[0]
                continue

        note_arr.append(note_obj)

    return note_arr

def cleanBookData():
    data = subprocess.run(f"exiftool -BookName -Author -ISBN -FileModifyDate {HOME}/Documents/Books/*/kindle/*.*", shell=True, capture_output=True, text=True)\
        .stdout\
        .strip("\n")
    data = re.split(r'\n=|\n\s', data)
    del data[-1]
    book_arr = []

    for item in data:
        book_obj = {}
        for line in item.strip().split("\n"):
            if line.startswith("="):
                category = line.split("/")[5].strip()
                book_obj["category"] = category
                continue

            [key, value] = line.split(":", 1)
            if key.startswith("Book"):
                book_obj["name"] = value.strip()
                continue
            if "modification" in key.lower():
                book_obj["dateAdded"] = value.strip().split()[0]
                continue
            book_obj[key.strip().lower()] = value.strip()

        book_arr.append(book_obj)

    return book_arr

def get_olid_with_isbn(book_arr):
    for book in book_arr:
        if "isbn" in book:
            url = f"https://openlibrary.org/isbn/{book['isbn']}.json"
            r = requests.get(url)
            if r.status_code == 200 and "covers" in r.json():
                print(f"========== getting OLID with ISBN for {book['name']} ==========")
                olid = r.json()["key"].split("/")[-1]
                book["olid"] = olid
                continue
            print(f"========== no cover found for {book['name']} ==========")
        get_isbn(book)

def get_isbn(book):
    print(f"========== searching for {book['name']} ==========")
    url = f"https://openlibrary.org/search.json?q={book['name']}"
    r = requests.get(url).json()
    if r["numFound"]:
        for doc in r["docs"]:
            cover_found = False
            if ((book["name"] in doc["title"]) or (doc["title"] in book["name"])):
                for seed in doc["seed"]:
                    if(seed.startswith("/books")):
                        bookUrl = f"https://openlibrary.org{seed}.json"
                        bookReq = requests.get(bookUrl).json()
                        if ("covers" in bookReq) and (bookReq["title"] in book["name"]):
                            print(f"========== getting OLID for {book['name']} ==========")
                            if not "isbn" in book:
                                print(f"========== assigning ISBN for {book['name']} ==========")
                                book["isbn"] = bookReq["isbn_13"][0]
                            olid = bookReq["key"].split("/")[-1]
                            book["olid"] = olid
                            cover_found = True
                            break
            if cover_found:
                break

def writeData(title, data_arr):
    json_object = json.dumps(data_arr,indent=4)
    with open(f"{title}Data.json", "w") as outfile:
        print(f"========== writing {title} data to file ==========")
        outfile.write(json_object)

def main():
    book_arr = cleanBookData()
    get_olid_with_isbn(book_arr)
    writeData("book", book_arr)
    note_arr = cleanNoteData()
    writeData("note", note_arr)

main()
