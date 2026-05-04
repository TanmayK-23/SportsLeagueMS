#usage: source venv/bin/activate , python app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'slms_secret_key_2026'  # Required for Flask sessions

# 🔗 Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",        # change if needed
    password="",        # add your password
    database="SportsLeagueDB"
)

cursor = db.cursor()

# 🔒 Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# 🌐 Inject is_admin into all templates
@app.context_processor
def inject_admin_status():
    return dict(is_admin=session.get('admin_logged_in', False))

# 🏠 Home Page
@app.route('/')
def home():
    return render_template('home.html', active_page='home')

# 🧾 Player Registration Page (Protected)
@app.route('/player')
@login_required
def player():
    cursor.execute("SELECT country_id, country_name FROM Country")
    countries = cursor.fetchall()
    return render_template('player.html', countries=countries, active_page='player')

# ➕ Insert Player (Protected)
@app.route('/insert_player', methods=['POST'])
@login_required
def insert_player():
    try:
        player_name = request.form['player_name']
        date_of_birth = request.form['date_of_birth']
        position = request.form['position']
        country_id = request.form['country_id']

        sql = """
            INSERT INTO Player (player_name, date_of_birth, position, country_id)
            VALUES (%s, %s, %s, %s)
        """

        values = (player_name, date_of_birth, position, country_id)
        cursor.execute(sql, values)
        db.commit()

        return redirect(url_for('home'))
    except Exception as e:
        return f"Error inserting player: {str(e)}"

@app.route('/view_players')
def view_players():
    try:
        # Cricket players
        cricket_sql = """
        SELECT p.player_id, p.player_name, p.date_of_birth, p.position, c.country_name
        FROM Player p
        JOIN Country c ON p.country_id = c.country_id
        JOIN Web_Positions wp ON p.position = wp.position_name
        WHERE wp.sport_type = 'Cricket'
        """

        # Football players
        football_sql = """
        SELECT p.player_id, p.player_name, p.date_of_birth, p.position, c.country_name
        FROM Player p
        JOIN Country c ON p.country_id = c.country_id
        JOIN Web_Positions wp ON p.position = wp.position_name
        WHERE wp.sport_type = 'Football'
        """

        cursor.execute(cricket_sql)
        cricket_players = cursor.fetchall()

        cursor.execute(football_sql)
        football_players = cursor.fetchall()

        return render_template(
            'view_players.html',
            cricket_players=cricket_players,
            football_players=football_players,
            active_page='players'
        )

    except Exception as e:
        return f"Error fetching players: {str(e)}"

# 🧑‍⚖️ Referees — League Index
@app.route('/referees')
def referees():
    try:
        # Fetch leagues and official counts from DB
        cursor.execute("""
            SELECT l.league_id, l.name, l.sport, l.emoji, l.color, l.type, COUNT(r.referee_id) as official_count
            FROM Web_Referee_Leagues l
            LEFT JOIN Web_Referees r ON l.league_id = r.league_id
            GROUP BY l.league_id, l.name, l.sport, l.emoji, l.color, l.type
            ORDER BY l.name
        """)
        leagues_raw = cursor.fetchall()
        leagues = [
            {'id': row[0], 'name': row[1], 'sport': row[2], 'emoji': row[3], 
             'color': row[4], 'type': row[5], 'count': row[6]}
            for row in leagues_raw
        ]
        return render_template('referees.html', leagues=leagues, active_page='referees')
    except Exception as e:
        return f"Error fetching referee leagues: {str(e)}"

@app.route('/referees/<league_id>')
def referee_league(league_id):
    try:
        # Fetch league info
        cursor.execute("SELECT name, sport, emoji, color, type FROM Web_Referee_Leagues WHERE league_id = %s", (league_id,))
        l_info = cursor.fetchone()
        if not l_info:
            return "League not found", 404

        # Fetch officials for this league
        cursor.execute("SELECT name, level, country, role FROM Web_Referees WHERE league_id = %s", (league_id,))
        officials_raw = cursor.fetchall()
        
        league = {
            'name': l_info[0],
            'sport': l_info[1],
            'emoji': l_info[2],
            'color': l_info[3],
            'type': l_info[4],
            'officials': [
                {'name': r[0], 'level': r[1], 'country': r[2], 'role': r[3]} 
                for r in officials_raw
            ]
        }
        return render_template('referee_league.html', league=league, league_id=league_id, active_page='referees')
    except Exception as e:
        return f"Error fetching officials: {str(e)}"

# 🏆 Tournaments Page
@app.route('/tournaments')
def tournaments():
    try:
        sql = "SELECT tournament_id, tournament_name, level, organizer FROM Web_Tournaments ORDER BY tournament_name"
        cursor.execute(sql)
        tourneys = cursor.fetchall()
        return render_template('tournaments.html', tournaments=tourneys, active_page='tournaments')
    except Exception as e:
        return f"Error fetching tournaments: {str(e)}"

# 📅 Matches Page
@app.route('/matches')
def matches():
    try:
        from datetime import date
        from collections import OrderedDict
        today = date.today()

        sql = """
        SELECT m.match_id, m.match_date, m.venue, m.tournament_id, t.tournament_name, m.home_team, m.away_team, m.home_score, m.away_score, m.home_scorers, m.away_scorers
        FROM Web_Matches m
        LEFT JOIN Web_Tournaments t ON m.tournament_id = t.tournament_id
        ORDER BY t.tournament_name, m.match_date DESC
        """
        cursor.execute(sql)
        raw_matches = cursor.fetchall()

        # Group by tournament
        league_map = OrderedDict()
        for row in raw_matches:
            tname = row[4] or 'Unknown'
            if tname not in league_map:
                league_map[tname] = {'name': tname, 'tournament_id': row[3], 'past': [], 'upcoming': []}
            match_data = {
                'id': row[0],
                'date': row[1],
                'venue': row[2],
                'tournament_name': tname,
                'teams': [
                    {'name': row[5], 'score': row[7] if row[7] is not None else 0, 'scorers': row[9]},
                    {'name': row[6], 'score': row[8] if row[8] is not None else 0, 'scorers': row[10]}
                ]
            }
            if row[1] < today:
                league_map[tname]['past'].append(match_data)
            else:
                league_map[tname]['upcoming'].append(match_data)

        # Sort upcoming within each league ascending
        for league in league_map.values():
            league['upcoming'].sort(key=lambda x: x['date'])

        leagues = list(league_map.values())
        total = sum(len(l['past']) + len(l['upcoming']) for l in leagues)
        return render_template('matches.html', leagues=leagues, total=total, active_page='matches')
    except Exception as e:
        return f"Error fetching matches: {str(e)}"

# 🏆 Tournament Detail Page
@app.route('/tournaments/<int:id>')
def tournament_detail(id):
    try:
        from datetime import date
        today = date.today()

        # Fetch Tournament Info
        cursor.execute("SELECT tournament_id, tournament_name, level, organizer FROM Web_Tournaments WHERE tournament_id = %s", (id,))
        tourney = cursor.fetchone()
        if not tourney:
            return "Tournament not found", 404

        # Fetch Matches and Teams
        sql = """
        SELECT match_id, match_date, venue, home_team, away_team, home_score, away_score, home_scorers, away_scorers
        FROM Web_Matches
        WHERE tournament_id = %s
        ORDER BY match_date DESC, match_id DESC
        """
        cursor.execute(sql, (id,))
        raw_matches = cursor.fetchall()

        past_matches = []
        upcoming_matches = []
        for row in raw_matches:
            match_data = {
                'id': row[0],
                'date': row[1],
                'venue': row[2],
                'teams': [
                    {'name': row[3], 'score': row[5] if row[5] is not None else 0, 'scorers': row[7]},
                    {'name': row[4], 'score': row[6] if row[6] is not None else 0, 'scorers': row[8]}
                ]
            }
            if row[1] < today:
                past_matches.append(match_data)
            else:
                upcoming_matches.append(match_data)
        
        # Sort upcoming matches ascending (soonest first)
        upcoming_matches.sort(key=lambda x: x['date'])

        return render_template('tournament_detail.html', tournament=tourney, past_matches=past_matches, upcoming_matches=upcoming_matches, active_page='tournaments')
    except Exception as e:
        return f"Error fetching tournament details: {str(e)}"

# 📅 Match Detail Page
@app.route('/matches/<int:id>')
def match_detail(id):
    try:
        # Fetch Match Info and Teams
        sql = """
        SELECT m.match_id, m.match_date, m.venue, t.tournament_name, m.referee, m.home_team, m.home_score, m.away_team, m.away_score, m.home_scorers, m.away_scorers
        FROM Web_Matches m
        LEFT JOIN Web_Tournaments t ON m.tournament_id = t.tournament_id
        WHERE m.match_id = %s
        """
        cursor.execute(sql, (id,))
        raw_match = cursor.fetchone()
        
        if not raw_match:
            return "Match not found", 404

        # Organize Match Data
        match_info = {
            'id': raw_match[0],
            'date': raw_match[1],
            'venue': raw_match[2],
            'tournament': raw_match[3],
            'referee': raw_match[4],
            'teams': [
                {'name': raw_match[5], 'score': raw_match[6] if raw_match[6] is not None else 0, 'scorers': raw_match[9]},
                {'name': raw_match[7], 'score': raw_match[8] if raw_match[8] is not None else 0, 'scorers': raw_match[10]}
            ]
        }

        # Fetch Match Events (for timeline if any)
        event_sql = """
        SELECT event_id, player_name, event_type, minute
        FROM Match_Event
        WHERE match_id = %s
        ORDER BY minute ASC
        """
        cursor.execute(event_sql, (id,))
        events = cursor.fetchall()

        return render_template('match_detail.html', match=match_info, events=events, active_page='matches')
    except Exception as e:
        return f"Error fetching match details: {str(e)}"

# 🛡️ Teams Directory Page
@app.route('/teams')
def teams():
    try:
        # Fetch all teams and their coaches
        cursor.execute("SELECT team_name, coach_name FROM Web_Coaches ORDER BY team_name")
        teams_data = cursor.fetchall()
        return render_template('teams.html', teams=teams_data, active_page='teams')
    except Exception as e:
        return f"Error fetching teams: {str(e)}"

# 🛡️ Team Detail Page
@app.route('/teams/<team_name>')
def team_detail(team_name):
    try:
        # Fetch Team Info (From Web Tables or general)
        cursor.execute("SELECT coach_name FROM Web_Coaches WHERE team_name = %s", (team_name,))
        coach = cursor.fetchone()
        
        # Fetch Players
        cursor.execute("SELECT player_name, position FROM Web_Players WHERE team_name = %s ORDER BY position, player_name", (team_name,))
        players = cursor.fetchall()

        if not coach and not players:
            return "Team not found", 404

        team_info = {
            'name': team_name,
            'coach': coach[0] if coach else "TBD",
            'players': players
        }

        return render_template('team_detail.html', team=team_info, active_page='')
    except Exception as e:
        return f"Error fetching team details: {str(e)}"

# 🔐 Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        try:
            cursor.execute("SELECT password_hash FROM Admin_Users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                session['admin_logged_in'] = True
                session['admin_username'] = username
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid username or password.'
        except Exception as e:
            error = f'Login error: {str(e)}'

    return render_template('admin_login.html', error=error)

# 🔐 Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', active_page='admin')

# 🔐 Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('home'))

# 🚀 Run App
if __name__ == '__main__':
    app.run(debug=True)