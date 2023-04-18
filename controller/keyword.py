from flask import *
from model.db import Redis


# 建立 Flask Blueprint
keyword= Blueprint("keyword", __name__)


@keyword.route("/api/keywords", methods=["GET"])
def search_keyword():
    bookId = request.args.get("bookId")
    keyword = request.args.get("keyword")
    print(keyword)
    if not keyword:
        return jsonify({
                    "data": None         
                }),200

    results = []
    for keywords, cursor in Redis.connect_to_redis().zscan_iter(f"bookId{bookId}", match=f"*{keyword}*"):
        results.append(keywords.decode('utf-8'))
    print(results)
    if not results:
        return jsonify({
                    "data": None         
                }),200
    
    return jsonify({
            "ok": True, 
            "data": results         
        }),200