import os
import sys
from api.setup_path import *
from api.app import app

if __name__ == "__main__":
    app.run(debug=True)
