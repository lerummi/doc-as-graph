import os
import sys
import dotenv

env = dotenv.find_dotenv(".env")
dotenv.load_dotenv(env)

code_path = os.path.join(
    os.path.split(env)[0],
    dotenv.get_key(env, "CODE_DIRECTORY")
)

sys.path.insert(0, code_path)
