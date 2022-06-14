from flask import Flask, jsonify, render_template, request
import algorithm as A

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        return "Hello"


@app.route("/api/<unique_id>", methods=['GET', 'POST'])
def api(unique_id):
    if request.method == "GET":
        schedule = A.ScheduleAlgo(unique_id=unique_id)
        schedule.terminal_state(schedule.start)
        schedule.solve()
        best_schedules = A.get_best_outcomes(schedule.solution)
        roster = best_schedules[0]['state'][0]
        return roster.to_json()


if __name__ == '__main__':
    app.run(debug=True)
