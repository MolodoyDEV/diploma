from flask import render_template

from app import create_app, auth

app = create_app()


@app.get('/')
@auth.login_required
def root_route():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
