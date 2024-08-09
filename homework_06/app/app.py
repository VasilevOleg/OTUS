from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    alarm_time = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=True)
    channel = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(20), nullable=False, default='table-default')

    def __repr__(self):
        return f"<Event {self.id} - {self.channel}: {self.description}>"


@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('q', '')
    if search_query:
        events = Event.query.filter(
            (Event.id.ilike(f'%{search_query}%')) |
            (Event.date.ilike(f'%{search_query}%')) |
            (Event.alarm_time.ilike(f'%{search_query}%')) |
            (Event.duration.ilike(f'%{search_query}%')) |
            (Event.channel.ilike(f'%{search_query}%')) |
            (Event.description.ilike(f'%{search_query}%'))
        ).order_by(Event.id.desc()).all()
    else:
        events = Event.query.order_by(Event.id.desc()).all()

    return render_template('index.html', events=events)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/add/', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        duration_value = request.form['duration']
        duration = int(duration_value) if duration_value else None

        new_event = Event(
            date=request.form['date'],
            alarm_time=request.form['alarm_time'],
            duration=duration,
            channel=request.form['channel'],
            description=request.form['description'] if request.form['description'] else None,
            color=request.form['color']
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_event.html')


@app.route('/delete/<int:event_id>/', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()
