from api import create_app


app = create_app("config.Dev")

if __name__ == "__main__":
    app.run()
