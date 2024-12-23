import os
from flask import Flask
from dotenv import load_dotenv


#######################
#                     #
#      Load app       #
#                     #
#######################
load_dotenv()
app = Flask(__name__)

#######################
#                     #
#   Register routes   #
#                     #
#######################
import src.routes

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=False,
        port=os.environ.get('FLASK_RUN_PORT', 8080)
    )
