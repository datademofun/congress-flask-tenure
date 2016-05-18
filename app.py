from flask import render_template, Flask
import foo


app = Flask(__name__)
legislators = foo.get_legislators()
committees = foo.get_committees()


@app.route('/')
def homepage():
    oldest_legislators = sorted(legislators, key=lambda x: x['years_served'], reverse=True)
    top_committees = [c for c in committees if not c['parent_id']]
    html = render_template('homepage.html',
                           legislators=oldest_legislators,
                           committees=top_committees)
    return html

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)




# from datafoo import congress

# app = Flask(__name__)


# congressmembers = congress.get_legislators()
# @app.route('/')
# def homepage():
#     oldtoyoung = sorted(congressmembers, key=lambda x: x['bio']['birthday'])
#     html = render_template('homepage.html', legislators=oldtoyoung)
#     return html
