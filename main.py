from api import create_app


app = create_app("config.Development")

if __name__ == "__main__":
    app.run()
