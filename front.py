from flask import render_template, request

from app import create_app, auth
from app.core import predict
from app.models import Settings

app = create_app()


@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def root_route():
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
            thresholds = Settings.query.where(
                Settings.name.in_([f'{x}_threshold' for x in result_dict.keys()])
            ).all()
            thresholds = {x.name: x.value for x in thresholds}

            for k, v in result_dict.items():
                is_triggered = v >= float(thresholds[f'{k}_threshold'])
                result += f'{k}: {v:.2f}. Trigger: {is_triggered}\n'

    return template()


if __name__ == '__main__':
    app.run()
