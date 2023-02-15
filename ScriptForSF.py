import pysmashgg
from datetime import datetime
from time import mktime, sleep

smash = pysmashgg.SmashGG('1d8515d23c643ea751677ce298f62d0c')
bad_substrings = ['volleyball', 'doubles', 'dubs', 'amateur', 'redemption', 'ammy']

def tournamentsFromPrevDay(day: int, month: int, year: int):
    start = mktime(datetime(year, month, day, 14).timetuple())
    end = mktime(datetime(year, month, day+1, 14).timetuple())

    tournaments = []

    i = 1
    done = False
    print("Getting tournaments\n")
    while(not done):
        temp_tournaments =  smash.tournament_show_event_by_game_size_dated(6, 1, int(start), int(end), i)
        if (temp_tournaments == []):
            done = True
        elif temp_tournaments is None:
            done = True
        else:
            i += 1
            tournaments += temp_tournaments

    new_tournaments = []
    for t in tournaments:
        if any(x in t['eventName'].lower() for x in bad_substrings):
            continue
        else:
            new_tournaments.append(t)
    
    new_tournaments = sorted(new_tournaments, key=lambda d: d['numEntrants'], reverse=True)
    print("Tournaments got\n")
    return new_tournaments

def resultsFromPrevDay(tournaments):
    results = []
    i = 0
    print("Iterating through tournaments\n")
    for t in tournaments:
        i += 1
        if i % 6 == 0:
            print("Sleeping")
            sleep(15)

        print("Tourney #" + str(i))
        try:
            temp_results = smash.event_show_lightweight_results(t['eventId'], 1)
            cur_result = {
                "tournamentName": t['tournamentName'],
                "online": t['online'],
                "eventName": t['eventName'],
                "eventId": t['eventId'],
                "numEntrants": t['numEntrants'],
                "winner": temp_results[0]
            }
            results.append(cur_result)
        except (TypeError, IndexError) as e:
            print("Error with " + str(t['tournamentName']) +" probably doubles or unfilled bracket")

    print("\nDone with iterating through tournaments\n")
    return results

def craftTweet(results):
    outfile = open("LastNightInMelee.txt", "w+", encoding='utf-8')
    i = 0
    print("Creating tweets\n")
    for r in results:
        
        i += 1
        if i % 6 == 0:
            print("\nSleeping\n")
            sleep(15)
        
        try:
            sets = smash.event_show_entrant_sets(r["eventId"], r["winner"]["name"])
            # print(json.dumps(sets, indent=4))
            opponents = ["NOT_FOUND", "NOT_FOUND"]
            losers_run = False
            for s in sets:
                if s['setRound'] == "Losers Final":
                    losers_run = True
            for s in sets:
                winner = s['winnerName'].split('|')[-1].strip()
                loser = s['loserName'].split('|')[-1].strip()

                if opponents[0] != "NOT_FOUND" and opponents[1] != "NOT_FOUND":
                    break

                if s['setRound'] == "Grand Final":
                    if winner.lower() == r["winner"]["name"].lower():
                        opponents[0] = loser
                    else:
                        opponents[0] = winner

                if s['setRound'] == "Losers Final":
                    if winner.lower() == r["winner"]["name"].lower():
                        opponents[1] = loser
                    else:
                        opponents[1] = winner

                if s['setRound'] == "Winners Final" and not losers_run:
                    if winner.lower() == r["winner"]["name"].lower():
                        if loser != opponents[0]:
                            opponents[1] = loser
                    else:
                        if winner != opponents[0]:
                            opponents[1] = winner
                
                if s['setRound'] == "Winners Semi-Final" and not losers_run:
                    if winner.lower() == r["winner"]["name"].lower():
                        opponents[1] = loser
                    else:
                        opponents[1] = winner
                
        except (TypeError, IndexError) as e:
            print("Error with " + str(r['tournamentName']))
        
        tourney_name = r["tournamentName"].split("#")[0].strip()
        tourney_name = tourney_name.split("(")[0].strip()
        text = r["winner"]["name"] + " won " + tourney_name + " beating " + opponents[0] + " and " + opponents[1]
        print(text)
        outfile.write(text)
        if r['online']:
            outfile.write(" (Online)\n")
        else:
            outfile.write("\n")

    return

def main():
    month = int(input("Type the month number: "))
    day = int(input("Type the day number: "))
    year = int(input("Type the year number: "))
    t = tournamentsFromPrevDay(day, month, year)
    r = resultsFromPrevDay(t)
    craftTweet(r)

if __name__ == "__main__":
    main()