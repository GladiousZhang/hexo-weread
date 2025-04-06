import argparse
import json
import logging
import os
import re
import time
import requests
from requests.utils import cookiejar_from_dict
from http.cookies import SimpleCookie
from dotenv import load_dotenv

load_dotenv()

WEREAD_URL = "https://weread.qq.com/"
WEREAD_NOTEBOOKS_URL = "https://i.weread.qq.com/user/notebooks"
WEREAD_BOOKMARKLIST_URL = "https://i.weread.qq.com/book/bookmarklist"
WEREAD_CHAPTER_INFO = "https://i.weread.qq.com/book/chapterInfos"
WEREAD_READ_INFO_URL = "https://i.weread.qq.com/book/readinfo"
WEREAD_REVIEW_LIST_URL = "https://i.weread.qq.com/review/list"
WEREAD_BOOK_INFO = "https://i.weread.qq.com/book/info"


def parse_cookie_string(cookie_string):
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies_dict = {}
    cookiejar = None
    for key, morsel in cookie.items():
        cookies_dict[key] = morsel.value
        cookiejar = cookiejar_from_dict(cookies_dict, cookiejar=None, overwrite=True)
    return cookiejar


def get_bookmark_list(bookId, session):
    """获取我的划线"""
    params = dict(bookId=bookId)
    r = session.get(WEREAD_BOOKMARKLIST_URL, params=params)
    if r.ok:
        updated = r.json().get("updated")
        updated = sorted(
            updated,
            key=lambda x: (x.get("chapterUid", 1), int(x.get("range").split("-")[0])),
        )
        return updated
    return None


def get_read_info(bookId, session):
    params = dict(bookId=bookId, readingDetail=1, readingBookIndex=1, finishedDate=1)
    r = session.get(WEREAD_READ_INFO_URL, params=params)
    if r.ok:
        return r.json()
    return None


def get_bookinfo(bookId, session):
    """获取书的详情"""
    params = dict(bookId=bookId)
    r = session.get(WEREAD_BOOK_INFO, params=params)
    isbn = ""
    if r.ok:
        data = r.json()
        isbn = data["isbn"]
        newRating = data["newRating"] / 1000
        return (isbn, newRating)
    else:
        print(f"get {bookId} book info failed")
        return ("", 0)


def get_review_list(bookId, session):
    """获取笔记"""
    params = dict(bookId=bookId, listType=11, mine=1, syncKey=0)
    r = session.get(WEREAD_REVIEW_LIST_URL, params=params)
    reviews = r.json().get("reviews")
    summary = list(filter(lambda x: x.get("review").get("type") == 4, reviews))
    reviews = list(filter(lambda x: x.get("review").get("type") == 1, reviews))
    reviews = list(map(lambda x: x.get("review"), reviews))
    reviews = list(map(lambda x: {**x, "markText": x.pop("content")}, reviews))
    return summary, reviews


def get_chapter_info(bookId, session):
    """获取章节信息"""
    body = {"bookIds": [bookId], "synckeys": [0], "teenmode": 0}
    r = session.post(WEREAD_CHAPTER_INFO, json=body)
    if (
        r.ok
        and "data" in r.json()
        and len(r.json()["data"]) == 1
        and "updated" in r.json()["data"][0]
    ):
        update = r.json()["data"][0]["updated"]
        return {item["chapterUid"]: item for item in update}
    return None


def get_notebooklist(session):
    """获取笔记本列表"""
    r = session.get(WEREAD_NOTEBOOKS_URL)
    if r.ok:
        data = r.json()
        books = data.get("books")
        books.sort(key=lambda x: x["sort"])
        return books
    else:
        print(r.text)
    return None


def try_get_cloud_cookie(url, id, password):
    if url.endswith("/"):
        url = url[:-1]
    req_url = f"{url}/get/{id}"
    data = {"password": password}
    result = None
    response = requests.post(req_url, data=data)
    if response.status_code == 200:
        data = response.json()
        cookie_data = data.get("cookie_data")
        if cookie_data and "weread.qq.com" in cookie_data:
            cookies = cookie_data["weread.qq.com"]
            cookie_str = "; ".join(
                [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
            )
            result = cookie_str
    return result


def get_cookie():
    cookie = os.getenv("WEREAD_COOKIE")
    if not cookie or not cookie.strip():
        raise Exception("没有找到cookie，请按照文档填写cookie")
    return cookie


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    options = parser.parse_args()
    weread_cookie = get_cookie()
    session = requests.Session()
    session.cookies = parse_cookie_string(weread_cookie)
    session.get(WEREAD_URL)

    books = get_notebooklist(session)
    book_data_list = []

    if books is not None:
        for book in books:
            book_info = book.get("book")
            title = book_info.get("title")
            bookId = book_info.get("bookId")
            author = book_info.get("author")
            categories = book_info.get("categories")
            if categories is not None:
                categories = [x["title"] for x in categories]

            isbn, rating = get_bookinfo(bookId, session)
            chapter = get_chapter_info(bookId, session)
            bookmark_list = get_bookmark_list(bookId, session)
            summary, reviews = get_review_list(bookId, session)
            read_info = get_read_info(bookId, session)

            book_data = {
                "title": title,
                "bookId": bookId,
                "author": author,
                "categories": categories,
                "isbn": isbn,
                "rating": rating,
                "chapter": chapter,
                "bookmark_list": bookmark_list,
                "summary": summary,
                "reviews": reviews,
                "read_info": read_info
            }
            book_data_list.append(book_data)

    # 保存为 JSON 文件
    with open('weread_books.json', 'w', encoding='utf-8') as f:
        json.dump(book_data_list, f, ensure_ascii=False, indent=4)