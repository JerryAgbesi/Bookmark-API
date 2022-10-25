from tracemalloc import get_object_traceback
from flask import Flask,Blueprint,request,jsonify
from src.database import db,Bookmark
import validators
from flask_jwt_extended import get_jwt_identity,jwt_required

bookmark = Blueprint("bookmark",__name__,url_prefix="/api/v1/bookmarks")

@bookmark.route("/",methods=["GET","POST"])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    print(current_user)
    if request.method == "POST":
       body = request.get_json().get("body","")
       url = request.get_json().get("url","")
     

       if not validators.url(url):
        return jsonify({"Error":"Enter a valid url"}),400

       if Bookmark.query.filter_by(url=url,user_id=current_user).first():
        return jsonify({
            "Error":"url already exists"
        }),409

       bookmark = Bookmark(body=body,url=url,user_id=current_user)
       print(bookmark.url)
       print(bookmark.user_id)

       db.session.add(bookmark)
       db.session.commit()

       return jsonify({
            "message":"Bookmark created successfully",
            "bookmark":{
                "id":bookmark.id,
                "body": bookmark.body,
                "url":bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at, 
                "updated_at": bookmark.Updated_at, 

            }
        }),201       

    if request.method == "GET":
        page = request.args.get("page",1,type=int)
        per_page = request.args.get("per_page",3,type=int)

        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page,per_page= per_page)

       
        bookmark_list= [{
            
               "id":bookmark.id,
                "body": bookmark.body,
                "url":bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at, 
                "updated_at": bookmark.Updated_at}
                for bookmark in bookmarks]

        meta = {
            "page":bookmarks.page,
            "per_page":bookmarks.per_page,
            "total_count":bookmarks.total,
            "has_next":bookmarks.has_next
        }        

        return jsonify({
            "data": bookmark_list,
            "meta":meta
        }),200      

@bookmark.route("/<int:id>",methods=["GET","PUT","PATCH"])
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    if request.method == "GET":
        bookmark = Bookmark.query.filter_by(id=id,user_id=current_user).first()

        if bookmark:
            return jsonify({
                "data": { 
                "id":bookmark.id,
                    "body": bookmark.body,
                    "url":bookmark.url,
                    "short_url": bookmark.short_url,
                    "visits": bookmark.visits,
                    "created_at": bookmark.created_at, 
                    "updated_at": bookmark.Updated_at}
                
            }),200
        else:
            return jsonify({
                "message": f"Bookmark with id {id} does not exist"
            }),404    

    if request.method == "PUT" or request.method == "PATCH"  :
        bookmark = Bookmark.query.filter_by(id=id,user_id=current_user).first()
        
        body = request.get_json().get("body","")
        url = request.get_json().get("url","")

        if not validators.url(url):
            return jsonify({
                "Error":"Enter a valid url"
            })
        
        
        if bookmark:
           bookmark.body = body
           bookmark.url = url
           db.session.commit()

           return jsonify({
                "data": { 
                    "id":bookmark.id,
                    "body": bookmark.body,
                    "url":bookmark.url,
                    "short_url": bookmark.short_url,
                    "visits": bookmark.visits,
                    "created_at": bookmark.created_at, 
                    "updated_at": bookmark.Updated_at}
                
            }),200
        else:
            return jsonify({
                "message": f"Bookmark with id {id} does not exist"
            }),404    

@bookmark.route("/<int:id>",methods=["DELETE"])
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(id=id,user_id=current_user).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({
            "message":"Bookmark deleted successfully"
        }),204
    else:
        return jsonify({
            "Error":"Bookmark not found"
        }),404  

@bookmark.route("/stats",methods=["GET"])
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
   

    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",5,type=int)
    
    bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page,per_page= per_page)

       
    bookmark_list= [{
                "id":bookmark.id,
                "url":bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,}
                for bookmark in bookmarks]

    meta = {
            "page":bookmarks.page,
            "per_page":bookmarks.per_page,
            "total_count":bookmarks.total,
            "has_next":bookmarks.has_next
        }        

    return jsonify({
            "data": bookmark_list,
            "meta":meta
        }),200









       