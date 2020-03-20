from trader import create_app

app = create_app(config='config_dev.py')

if __name__ == '__main__':
   app.run(threaded=True)
