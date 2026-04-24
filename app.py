#usage: source venv/bin/activate , pyhton app.py
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# 🔗 Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",        # change if needed
    password="",        # add your password
    database="SportsLeagueDB"
)

cursor = db.cursor()

# 🏠 Home Page
@app.route('/')
def home():
    return render_template('home.html', active_page='home')

# 🧾 Player Registration Page
@app.route('/player')
def player():
    cursor.execute("SELECT country_id, country_name FROM Country")
    countries = cursor.fetchall()
    return render_template('player.html', countries=countries, active_page='player')

# ➕ Insert Player
@app.route('/insert_player', methods=['POST'])
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
        WHERE p.position IN ('WK-Batsman', 'Bowler', 'Batsman', 'All-rounder')
        """

        # Football players
        football_sql = """
        SELECT p.player_id, p.player_name, p.date_of_birth, p.position, c.country_name
        FROM Player p
        JOIN Country c ON p.country_id = c.country_id
        WHERE p.position IN (
            'Goalkeeper',
            'Center-back',
            'Full-back',
            'Midfielder',
            'Striker',
            'Winger'
        )
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

# 🚀 Run App
if __name__ == '__main__':
    app.run(debug=True)