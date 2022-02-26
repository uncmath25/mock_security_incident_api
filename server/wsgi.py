if __name__ == 'wsgi':
    print('UWSGI Server Running App...')
    from main import webserver as application
