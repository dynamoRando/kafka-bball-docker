import mysql.connector
import randomname
import names 

host = "localhost"
user = "bball"
password = "bball"

total_teams = 30
players_per_team = 15
total_games_per_season = 72
total_seconds_per_quarter = 600
total_quarters_per_game = 4

db = mysql.connector.connect(
  host=host,
  user=user,
  password=password,
  port=23306
)

def init_database(db):
    # cur = db.cursor()
    # cur.execute("DROP DATABASE IF EXISTS bball_sim;")
    # db.commit()
    # cur.execute("CREATE DATABASE IF NOT EXISTS bball_sim;")

    db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database="bball",
    port=23306
    )

    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS TEAM 
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name varchar(50) NOT NULL);
                """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS PLAYER
                (id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                team_id INT UNSIGNED NOT NULL,
                name VARCHAR(50) NOT NULL,
                FOREIGN KEY (team_id) REFERENCES TEAM(id)
                );
                """)

    for n in range(total_teams):
        name = randomname.get_name(noun=('apex_predators')).replace("-", " ").title()
        team_name = []
        team_name.append(name)
        print(name)
        sql = "INSERT INTO TEAM (name) VALUES (%s)"
        cur.execute(sql, (team_name))
        db.commit()

    for n in range(total_teams):
        for m in range(players_per_team):
            name = names.get_full_name()
            sql = "INSERT INTO PLAYER (team_id, name) VALUES (%s, %s)"
            cur.execute(sql, (n + 1, name))
            db.commit()

    sql = """
    CREATE TABLE IF NOT EXISTS GAME 
    (
      id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      away_team_id INT UNSIGNED NOT NULL,
      home_team_id INT UNSIGNED NOT NULL,
      quarter INT UNSIGNED NOT NULL,
      clock_in_seconds INT UNSIGNED NOT NULL,
      current_possession_team_id INT UNSIGNED NOT NULL,
      away_team_score INT UNSIGNED NOT NULL,
      home_team_score INT UNSIGNED NOT NULL,
      is_active TINYINT NOT NULL,
      FOREIGN KEY (away_team_id) REFERENCES TEAM(id),
      FOREIGN KEY (home_team_id) REFERENCES TEAM(id)
    );
    """
    cur.execute(sql)

    sql = """
   CREATE TABLE IF NOT EXISTS GAME_LOG 
   (
     id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
     player_id INT UNSIGNED NOT NULL,
     game_id INT UNSIGNED NOT NULL,
     quarter INT UNSIGNED NOT NULL,
     clock_in_seconds INT UNSIGNED NOT NULL,
     points INT UNSIGNED NOT NULL,
     FOREIGN KEY (game_id) REFERENCES GAME(id),
     FOREIGN KEY (player_id) REFERENCES PLAYER(id)
   );
    """
    cur.execute(sql)

init_database(db)