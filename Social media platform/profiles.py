from flask import Flask, flash, request, jsonify
from con import set_connection

app = Flask(__name__)


@app.route('/create', methods=['POST'])
def create_profile():
    # {"name": "bhanu",
    #  "description": "Bhanu profile for instagram"
    #  }
    try:
        name = request.json['name']
        description = request.json['description']
    except KeyError:
        return {"message": "Invalid request format"}, 400

    cur, conn = set_connection()
    if cur and conn:
        try:
            cur.execute("INSERT INTO profiles (name, description) VALUES (%s, %s)", (name, description))
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return {"message": "Failed to create profile"}, 500
        finally:
            cur.close()
            conn.close()
        return {"message": "Profile created successfully"}, 201
    else:
        return {"message": "Failed to create profile"}, 500


# Retrieve a list of all profiles from the database
@app.route('/', methods=['GET'])
def get_profiles():
    cur, conn = set_connection()
    if cur and conn:
        try:
            cur.execute("SELECT * FROM profiles")
            rows = cur.fetchall()
        except Exception as e:
            print(e)
            return {"message": "Failed to get profiles"}, 500
        finally:
            cur.close()
            conn.close()
        return jsonify(rows), 200
    else:
        return {"message": "Failed to get profiles"}, 500


# Create a new post for a profile in the database
@app.route('/<int:profile_id>/create_post', methods=['POST'])
def create_post(profile_id):
    # {
    #     "content": "Weekend vibes"
    # }
    try:
        content = request.json['content']
    except KeyError:
        return {"message": "Invalid request format"}, 400

    cur, conn = set_connection()
    if cur and conn:
        try:
            cur.execute("INSERT INTO posts (profile_id, content) VALUES (%s, %s)", (profile_id, content))
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return {"message": "Failed to create post"}, 500
        finally:
            cur.close()
            conn.close()
        return {"message": "Post created successfully"}, 201
    else:
        return {"message": "Failed to create post"}, 500


# Retrieve a list of all posts for a profile from the database
@app.route('/<int:profile_id>/', methods=['GET'])
def get_posts(profile_id):
    cur, conn = set_connection()
    if cur and conn:
        try:
            cur.execute("SELECT * FROM posts WHERE profile_id = %s", (profile_id,))
            rows = cur.fetchall()
        except Exception as e:
            print(e)
            return {"message": "Failed to get posts"}, 500
        finally:
            cur.close()
            conn.close()
        return jsonify(rows), 200
    else:
        return {"message": "Failed to get posts"}, 500


@app.route('/<int:post_id>/like', methods=['PUT'])
def like_post(post_id):
    try:
        cur, conn = set_connection()
        if cur and conn:
            cur.execute("UPDATE posts SET like_count = like_count + 1 WHERE id = %s", (post_id,))
            conn.commit()
            cur.close()
            conn.close()
            return {"message": "Post liked successfully"}, 200
        else:
            return {"message": "Failed to like post"}, 500
    except Exception as e:
        return {"message": "Error occurred while liking the post", "error": str(e)}, 500


@app.route('/<int:post_id>/comment', methods=['POST'])
def create_comment(post_id):
    try:
        content = request.json.get('content')

        cur, conn = set_connection()  ##creates database connection
        if cur and conn:
            cur.execute("INSERT INTO comments (post_id, content) VALUES (%s, %s)", (post_id, content))   ## inserts the comment into comment table
            conn.commit()   ##commits the changes
            cur.close()
            conn.close()
            return {"message": "Comment created successfully"}, 201
        else:
            return {"message": "Failed to create comment"}, 500
    except Exception as e:
        return {"message": "Error occurred while creating the comment", "error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
