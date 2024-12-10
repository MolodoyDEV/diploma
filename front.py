from flask import render_template, request

from app import create_app, auth
from app.core import predict

app = create_app()


@app.get('/')
@auth.login_required
def root_route():
    return render_template('index.html')


@app.route('/test/', methods=['GET', 'POST'])
@auth.login_required
def test_route():
    result = ""
    message = ""

    def template():
        return render_template('test.html', result=result, message=message)

    if request.method == 'GET':
        return template()

    elif request.method == 'POST':
        message = request.form['message']

        try:
            result_dict = predict(message)
        except ValueError:
            result = 'Невалидное сообщение!'

        else:
            for k, v in result_dict.items():
                result += f'{k}: {v:.2f}\n'

    return template()


if __name__ == '__main__':
    app.run()
