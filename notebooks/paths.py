import sys
import dotenv

env = dotenv.find_dotenv(".env")
dotenv.load_dotenv(env)

sys.path.insert(0, dotenv.get_key("CODE_DIRECTORY"))
