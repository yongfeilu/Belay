from flask import Flask, render_template, request, jsonify
import mysql.connector # pip3 install mysql-connector
import bcrypt
import configparser
import uuid
import string
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

config = configparser.ConfigParser()
config.read('secrets.cfg')
DB_NAME = 'yongfeilu'
DB_USERNAME = config['secrets']['DB_USERNAME']
DB_PASSWORD = config['secrets']['DB_PASSWORD']
PEPPER = config['secrets']['PEPPER']
SENDGRID_API_KEY = config['secrets']['SENDGRID_API_KEY']

emial_tokens = {}

session_tokens = {}
def generate_session_token():
    session_token =  ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    while (session_token in session_tokens.values()):
        session_token =  ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    return session_token


@app.route('/')
@app.route('/login')
@app.route('/signup')
@app.route('/user/<int:user_id>')
@app.route('/foreget-password')
@app.route('/resetpassword')

def index(user_id=None):
    return app.send_static_file('index.html')

# -------------------------------- API ROUTES ----------------------------------


@app.route('/api/signup', methods=['POST'])
def signup ():
    body = request.get_json()
    username = body['username']
    useremail = body['useremail']
    password = body['password'] + PEPPER
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    query = "INSERT into user (username, useremail, password) VALUES (%s, %s, %s)"

    try:
        cursor.execute(query, (username, useremail, hashed))
        connection.commit()
        return {}
    except Exception as e:
        print(e)
        return {"username": username}, 403
    finally:
        cursor.close()
        connection.close()


@app.route('/api/forgetpassword', methods=['POST'])
def forget_password ():
    useremail = request.get_json()['useremail']
    root_url = request.url_root
    token = uuid.uuid4().hex
    magic_link = root_url + 'resetpassword?magic_token=' + token
    message = Mail(
        from_email='yflecon@gmail.com',
        to_emails=useremail,
        subject='Reseting your Belay password',
        html_content='Use this link <strong><a>{}</a></strong> to reset your password!'.format(magic_link)
        )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        emial_tokens[useremail] = token

        return "Link sent to your mailbox!"
    except Exception as e:
        print(str(e))
        return "Failed!"


@app.route('/api/changepassword', methods=['POST'])
def change_password ():
    body = request.get_json()
    useremail = body["useremail"]
    password = body['password'] + PEPPER
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    key = body["key"];
    if useremail not in emial_tokens.keys() or emial_tokens[useremail] != key:
        return {}, 401

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()
    query = "UPDATE user SET password = %s WHERE useremail = %s;"
    try:
        cursor.execute(query, (hashed, useremail))
        connection.commit()
        return {}
    except Exception as e:
        print(e)
        return {}, 403
    finally:
        cursor.close()
        connection.close()



@app.route('/api/login', methods=['POST'])
@app.route('/api/authenticate', methods=['POST'])
def login ():
    body = request.get_json()
    useremail = body['useremail']
    password = body['password']
    auth = body["auth"]
    cur_user_id = body["currentUserId"]

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    query = "SELECT password, username, user_id FROM user WHERE useremail=%s"

    try:
        cursor.execute(query, (useremail,))
        data = cursor.fetchone()
        hashed = data[0]
        username = data[1]
        user_id = data[2]

        if bcrypt.checkpw((password+PEPPER).encode('utf-8'), hashed.encode('utf-8')):
            if auth == "NO":
                token = generate_session_token()
                session_tokens[user_id] = token

                return {"session_token": token , "username": username, "useremail": useremail, "user_id": user_id}
            else:
                if user_id != int(cur_user_id):
                    return {}, 401
                return {"username": username, "useremail": useremail, "user_id": user_id}
        return {}, 401

    except Exception as e:
        print(e)
        return {}, 403
    finally:
        cursor.close()
        connection.close()


@app.route('/api/channels', methods=['GET', 'POST'])
def channels ():

    u_id = request.cookies['cookie'].split("/")[0]
    token = request.cookies['cookie'].split("/")[1]
    if token != session_tokens[int(u_id)]:
        return {}, 401

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    if request.method == "GET":
        query = "SELECT lm.channel_id, lm.user_id, c.channel_name, c.creater_id, c.number_of_messages,\
                    (c.number_of_messages - lm.current_total) AS unread\
                    FROM last_message lm INNER JOIN channel c ON lm.channel_id = c.channel_id;"
        try:
            cursor.execute(query)
            records = cursor.fetchall()
            res = {"channels": []}
            channel_ids = []
            for record in records:
                if record[0] not in channel_ids:
                    channel_ids.append(record[0])

            for channel_id in channel_ids:
                res["channels"].append({"channel_id": channel_id, "count": []})

            for record in records:
                for c in res["channels"]:
                    if c["channel_id"] == record[0]:
                        c["number_of_messages"] = record[4]
                        c["channel_name"] = record[2]
                        c["creater_id"] = record[3]
                        c["count"].append({"user_id": record[1], "unread": record[5]})
            return res
        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()
    else:
        body = request.get_json()
        channel_name = body['channelname']
        creater_id = body['creator_id']
        create_time = body['create_time']

        query = "INSERT INTO channel (channel_name, creater_id, create_time, number_of_messages) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(query, (channel_name, creater_id, create_time, 0))
            connection.commit()

            cursor.execute("INSERT INTO last_message (channel_id, user_id, last_mg_id, current_total)\
                                SELECT  channel_id, user_id, NULL , 0 FROM user, channel \
                                WHERE channel.channel_id = (SELECT max(channel_id) FROM channel)")
            connection.commit()
            return {}

        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()



@app.route('/api/messages', methods=['GET', 'POST'])
def messages ():

    u_id = request.cookies['cookie'].split("/")[0]
    token = request.cookies['cookie'].split("/")[1]
    if token != session_tokens[int(u_id)]:
        return {}, 401


    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    if request.method == "GET":
        query = "SELECT t1.channel_id, t1.mg_id, t1.body, t1.post_time, t1.username, t2.replies, t1.sender_id FROM\
                    (SELECT channel_id, mg_id, body, post_time, username, sender_id FROM channel c\
                        INNER JOIN message m ON c.channel_id = m.room_id\
                        INNER JOIN user u ON m.sender_id = u.user_id\
                        WHERE mg_id NOT IN \
                        (SELECT mg_id FROM message m INNER JOIN reply r ON r.reply_id = m.mg_id)) t1\
                    LEFT JOIN (SELECT original_mg_id, COUNT(*) AS replies FROM reply GROUP BY original_mg_id) t2 \
                    ON t1.mg_id = t2.original_mg_id \
                    ORDER BY t1.post_time ASC;"
        try:
            cursor.execute(query)
            messages = cursor.fetchall()
            messages_by_channel = {}
            messages_by_channel["channels"] = []

            channel_ids = []
            for message in messages:
                if message[0] not in channel_ids:
                    channel_ids.append(message[0])

            for channel_id in channel_ids:
                messages_by_channel["channels"].append({"channel_id": channel_id, "messages": []})

            for message in messages:
                for channel in messages_by_channel["channels"]:
                    if channel["channel_id"] == message[0]:
                        channel["messages"].append({
                            "mg_id": message[1],
                            "body": message[2],
                            "post_time": message[3],
                            "username": message[4],
                            "replies": message[5],
                            "sender_id": message[6]
                            })
            return messages_by_channel
        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()
    else:
        message = request.get_json()
        body = message["body"]
        sender_id = message["sender_id"]
        room_id = message["room_id"]
        post_time = message["post_time"]
        reply = message["reply"]

        query = "INSERT INTO message (body, sender_id, room_id, post_time) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(query, (body, sender_id, room_id, post_time))
            connection.commit()
            if reply == "NO":
                cursor.execute("UPDATE channel SET number_of_messages= channel.number_of_messages + 1 WHERE channel_id = %s;", (room_id,))
                connection.commit()

            cursor.execute("SELECT mg_id FROM message WHERE body = %s AND post_time = %s", (body, post_time))
            mg_id = cursor.fetchone()[0]
            return {"reply_id": mg_id}

        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()



@app.route('/api/replies', methods=['GET', 'POST'])
def replies ():

    u_id = request.cookies['cookie'].split("/")[0]
    token = request.cookies['cookie'].split("/")[1]
    if token != session_tokens[int(u_id)]:
        return {}, 401

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    if request.method == 'POST':
        reply = request.get_json()
        reply_id = reply["reply_id"]
        original_mg_id = reply["original_mg_id"]
        query = "INSERT INTO reply (original_mg_id, reply_id) VALUES (%s, %s)"
        try:
            cursor.execute(query, (original_mg_id, reply_id))
            connection.commit()
            return {}
        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()
    else:
        query = "SELECT reply.original_mg_id, body, post_time, username, mg_id FROM message\
                    INNER JOIN user ON message.sender_id = user.user_id\
                    INNER JOIN reply ON reply.reply_id = message.mg_id\
                    ORDER BY message.post_time ASC"

        try:
            cursor.execute(query)
            records = cursor.fetchall()

            res = {"replies": []}
            mg_ids = []
            for record in records:
                if record[0] not in mg_ids:
                    mg_ids.append(record[0])

            for mg_id in mg_ids:
                cursor.execute("SELECT body, post_time, username FROM message \
                                    INNER JOIN user ON message.sender_id = user.user_id\
                                    WHERE mg_id = %s", (mg_id,))
                current_message = cursor.fetchone()
                res["replies"].append({"original_mg_id": mg_id, 
                                        "current_message": {"body": current_message[0], 
                                                            "post_time": current_message[1],
                                                            "username": current_message[2]},
                                        "messages":[]})
            for record in records:
                for reply in res["replies"]:
                    if record[0] == reply["original_mg_id"]:
                        reply["messages"].append({"body": record[1], "post_time": record[2], "username": record[3], "mg_id": record[4]})
            return res
        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()


@app.route('/api/update', methods=['POST'])
def update ():

    u_id = request.cookies['cookie'].split("/")[0]
    token = request.cookies['cookie'].split("/")[1]
    if token != session_tokens[int(u_id)]:
        return {}, 401

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    data = request.get_json()
    change_item = data["changeItem"]
    new_value = data["newItemValue"]
    user_id = data["user_id"]

    if change_item == "username":
        query = "UPDATE user SET username = %s WHERE user_id = %s;"
    else:
        query = "UPDATE user SET useremail = %s WHERE user_id = %s;"
    
    try:
        cursor.execute(query, (new_value, user_id))
        connection.commit()
        return {}
    except Exception as e:
        print(e)
        return {}, 403
    finally:
        cursor.close()
        connection.close()


@app.route('/api/remove', methods=['DELETE'])
def delete():

    u_id = request.cookies['cookie'].split("/")[0]
    token = request.cookies['cookie'].split("/")[1]
    if token != session_tokens[int(u_id)]:
        return {}, 401

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    data = request.get_json()
    channel_id = data["channel_id"]

    query = "DELETE FROM channel WHERE channel_id = %s;"

    try:
        cursor.execute(query, (channel_id,))
        connection.commit()
        return{}
    except Exception as e:
        print(e)
        return {}, 403
    finally:
        cursor.close()
        connection.close()


@app.route("/api/last_message", methods = ['POST', "GET"])
def track_last_message():

    u_id = request.cookies['cookie'].split("/")[0]
    token = request.cookies['cookie'].split("/")[1]
    if token != session_tokens[int(u_id)]:
        return {}, 401

    connection = mysql.connector.connect(user=DB_USERNAME, database=DB_NAME, password=DB_PASSWORD, auth_plugin='mysql_native_password')
    cursor = connection.cursor()

    if request.method == "POST":
        data = request.get_json()
        channel_id = data["channel_id"]
        user_id = data["user_id"]
        last_mg_id = data["last_mg_id"]
        current_total = data["current_total"]

        query = "SELECT * FROM last_message WHERE channel_id = %s AND user_id = %s"
        try:
            cursor.execute(query, (channel_id, user_id))
            last_message = cursor.fetchone()

            if last_message:
                cursor.execute("UPDATE last_message SET current_total = %s \
                                WHERE user_id = %s AND channel_id = %s;", (current_total, user_id, channel_id))
                connection.commit()
            else:
                cursor.execute("INSERT INTO last_message (channel_id, user_id, last_mg_id, current_total)\
                                VALUES (%s, %s, %s, %s)", (channel_id, user_id, last_mg_id, current_total))
                connection.commit()
            return {}
        except Exception as e:
            print(e)
            return {}, 403
        finally:
            cursor.close()
            connection.close()
