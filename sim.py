from mysql.connector import MySQLConnection
import mysql.connector
from multiprocessing import Process
import time
import typing
import random

host = "localhost"
user = "bball"
password = "bball"

total_teams = 30
players_per_team = 15
total_games_per_season = 72
total_seconds_per_quarter = 600
total_seconds_per_posession = 30
total_quarters_per_game = 4
total_games_per_tick = 4

low_wait_seconds = 10
high_wait_seconds = 30

db = mysql.connector.connect(
    host=host, user=user, password=password, database="bball", port=23306
)


def get_new_game_teams(db: MySQLConnection) -> (int, int):
    a = random.randint(1, 30)
    b = random.randint(1, 30)

    print(f"Looking for active games between {(a, b)}")

    if a == b:
        print("Random generated same teams, trying again...")
        get_new_game_teams(db)

    sql = """
        SELECT 
            COUNT(*) active_games 
        FROM 
            GAME 
        WHERE 
            is_active = 1
        AND (away_team_id = %s OR home_team_id = %s)
        ;"""

    cur = db.cursor()
    cur.execute(sql, ([a, a]))
    result = cur.fetchall()
    count_a = int(result[0][0])

    print(f"Total active games for team A: {count_a}")

    cur = db.cursor()
    cur.execute(sql, ([b, b]))
    result = cur.fetchall()
    count_b = int(result[0][0])

    print(f"Total active games for team B: {count_b}")

    if count_a > 0 or count_b > 0:
        print("One of the teams is playing right now, trying again...")
        get_new_game_teams(db)
    elif a == b:
        print("Same teams found, trying again...")
        get_new_game_teams(db)
    else:
        data = (a, b)
        print(f"Returning game {data}")
        return data


def create_game(db: MySQLConnection):
    print("Creating game...")
    teams = get_new_game_teams(db)
    if teams is None:
        return
    print(f"Teams: {teams}")
    away_team_id = teams[0]
    home_team_id = teams[1]

    sql = """
    INSERT INTO GAME 
    (
        away_team_id,
        home_team_id,
        quarter,
        clock_in_seconds,
        current_possession_team_id,
        away_team_score,
        home_team_score,
        is_active
    )
    VALUES
    (
        %s,
        %s,
        1,
        %s,
        %s,
        0,
        0,
        1
    )
    """

    cur = db.cursor()
    data: tuple = (away_team_id, home_team_id, total_seconds_per_quarter, away_team_id)
    cur.execute(sql, data)
    db.commit()
    print(f"Game created between {teams}")
    return


def get_total_active_games(db: MySQLConnection) -> int:
    sql = "SELECT COUNT(*) active_games FROM GAME WHERE is_active = 1;"
    cur = db.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    return int(result[0][0])


def evaluate_active_game_count(db: MySQLConnection):
    active_game_count = get_total_active_games(db)
    print(f"Total active games: {active_game_count}")
    if active_game_count < total_games_per_tick:
        games_to_create = total_games_per_tick - active_game_count
        print(f"Games to create this tick: {games_to_create}")
        create_game(db)
        evaluate_active_game_count(db)

    else:
        print(f"Active game threshold met: {active_game_count}")
        return


def sim_games(db: MySQLConnection):
    print("Sim active games...")
    sql = "SELECT id FROM GAME WHERE is_active = 1;"
    cur = db.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    for row in result:
        game_id = row[0]
        print(f"Got active game: {game_id}")
        sim_game(db, game_id)


def sim_game(db: MySQLConnection, game_id: int):
    print(f"Sim game_id: {game_id}")

    sql = "SELECT quarter FROM GAME WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, ([game_id]))
    result = cur.fetchall()
    quarter = result[0][0]
    print(f"Quarter: {quarter}")

    sql = "SELECT clock_in_seconds FROM GAME WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, ([game_id]))
    result = cur.fetchall()
    clock_in_seconds = result[0][0]
    print(f"Clock: {clock_in_seconds}")

    if quarter == 4 and clock_in_seconds == 0:
        print(f"Game Id: {game_id} has ended")
        sql = "UPDATE GAME SET is_active = 0 WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, ([game_id]))
        db.commit()
        return

    if quarter < 4 and clock_in_seconds == 0:
        print(f"Game Id: {game_id} quarter {quarter} has ended")
        next_quarter = quarter + 1
        sql = "UPDATE GAME SET quarter = %s WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, (next_quarter, game_id))
        db.commit()

        sql = "UPDATE GAME SET clock_in_seconds = %s WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, (total_seconds_per_quarter, game_id))
        db.commit()
        return

    sql = "SELECT away_team_id FROM GAME WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, ([game_id]))
    result = cur.fetchall()
    away_team_id = result[0][0]
    print(f"Away Team: {away_team_id}")

    sql = "SELECT home_team_id FROM GAME WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, ([game_id]))
    result = cur.fetchall()
    home_team_id = result[0][0]
    print(f"Home Team: {home_team_id}")

    sql = "SELECT current_possession_team_id FROM GAME WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, ([game_id]))
    result = cur.fetchall()
    current_possession_team_id = result[0][0]
    print(f"Who has the ball: {current_possession_team_id}")

    should_score = bool(random.getrandbits(1))
    print(f"Sim says team should core on this posession: {should_score}")

    if should_score:
        sql = "SELECT away_team_score FROM GAME WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, ([game_id]))
        result = cur.fetchall()
        away_team_score = result[0][0]
        print(f"Away Team Score: {away_team_score}")

        sql = "SELECT home_team_score FROM GAME WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, ([game_id]))
        result = cur.fetchall()
        home_team_score = result[0][0]
        print(f"Home Team Score: {home_team_score}")

        sql = "SELECT id FROM PLAYER WHERE team_id = %s"
        cur = db.cursor()
        cur.execute(sql, ([current_possession_team_id]))
        result = cur.fetchall()
        total_players = len(result)
        print(f"Total Players: {total_players}")
        random_player_index = random.randint(0, total_players)
        print(f"Random Player Index: {random_player_index}")
        player_id = result[random_player_index - 1][0]
        print(f"Player to score: {player_id}")

        random_points = random.randint(1, 3)
        print(f"Points: {random_points}")

        if current_possession_team_id == home_team_id:
            print(f"Home Team Scored {random_points} points!")
            new_home_team_score = home_team_score + random_points
            sql = "UPDATE GAME SET home_team_score = %s WHERE id = %s"
            cur = db.cursor()
            cur.execute(sql, (new_home_team_score, game_id))
            db.commit()
        else:
            print(f"Away Team Scored {random_points} points!")
            new_away_team_score = away_team_score + random_points
            sql = "UPDATE GAME SET away_team_score = %s WHERE id = %s"
            cur = db.cursor()
            cur.execute(sql, (new_away_team_score, game_id))
            db.commit()

        sql = """
            INSERT INTO GAME_LOG (player_id, game_id, quarter, clock_in_seconds, points)
            VALUES (%s, %s, %s, %s, %s)
        """

        cur = db.cursor()
        cur.execute(sql, (player_id, game_id, quarter, clock_in_seconds, random_points))
        db.commit()

    # end posession of the ball
    new_clock_in_seconds = clock_in_seconds - total_seconds_per_posession
    print(f"Game Id: {game_id} clock is now: {new_clock_in_seconds}")
    sql = "UPDATE GAME SET clock_in_seconds = %s WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, (new_clock_in_seconds, game_id))
    db.commit()

    if away_team_id == current_possession_team_id:
        sql = "UPDATE GAME SET current_possession_team_id = %s WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, (home_team_id, game_id))
        print(f"Game Id: Posession now by team: {home_team_id}")
        db.commit()
    else:
        sql = "UPDATE GAME SET current_possession_team_id = %s WHERE id = %s"
        cur = db.cursor()
        cur.execute(sql, (away_team_id, game_id))
        print(f"Game Id: Posession now by team: {away_team_id}")
        db.commit()

    db.commit()
    print("Game State:")

    sql = "SELECT * FROM GAME WHERE id = %s"
    cur = db.cursor()
    cur.execute(sql, ([game_id]))
    result = cur.fetchall()
    print(result)

    print("Game sim finished...")
    return


def evaluate_if_season_ended(db: MySQLConnection) -> bool:
    sql = "SELECT COUNT(*) FROM GAME WHERE is_active = 0"
    cur = db.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    game_count = result[0][0]
    if game_count == total_games_per_season:
        return True
    else:
        return False


def tick(db: MySQLConnection):
    print("Tick...")
    if not evaluate_if_season_ended(db):
        evaluate_active_game_count(db)
        sim_games(db)
    else:
        print("Season has ended...")


while True:
    tick(db)
    time.sleep(random.randint(low_wait_seconds, high_wait_seconds))
