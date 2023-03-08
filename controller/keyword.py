from flask import *
from model.redis_db import Redis


# 建立 Flask Blueprint
keyword= Blueprint("keyword", __name__)


@keyword.route("/api/keywords", methods=["GET"])
def search_keyword():
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({
                    "data": None         
                }),200

    word = "{}*".format(keyword)
    results = Redis.connect_to_redis().keys(word)
    results = [r.decode('utf-8') for r in results]
    
    if not results:
        return jsonify({
                    "data": None         
                }),200
    
    return jsonify({
            "ok": True, 
            "data": results         
        }),200