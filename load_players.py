import csv
import numpy as np
import matplotlib.pyplot as plt
import pylab
def clean_row(row):
	integer_keys = ['selection', 'draft_round', 'draft_year', 'gp', 'minutes', 'pts']
	team_equivalents = {'KCK' : 'SAC', 'NOH':'NOR', 'SEA' : 'OKC', 'VAN':'MEM'}
	if '\xef\xbb\xbfdraft_year' in row:
		row['draft_year'] = row['\xef\xbb\xbfdraft_year']
		del row['\xef\xbb\xbfdraft_year']
	if '' in row:
		del row['']
	for key in row:
		if key in integer_keys:
			row[key] = int(row[key])
		else:
			row[key] = str.upper(row[key]).strip()
		if key == 'team':
			if row[key] in team_equivalents:
				row[key] = team_equivalents[row[key]]
	return row

def load_file(filename):
	database = []
	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',')
		for row in reader:
			row = clean_row(row)
			database.append(row)
	return database

def combine_by_key(database1, database2, key):
	newdict = {}
	for row in database1:
		if key not in row:
			continue
		temp = newdict.get(row[key])
		if temp is None:
			temp = {}
		temp.update(row)
		newdict[row[key]] = temp
	for row in database2:
		if key not in row:
			continue
		temp = newdict.get(row[key])
		if temp == None:
			temp = {}
		else:
			temp.update(row)
		newdict[row[key]] = temp
	return newdict
def get_number_of_teams_in_league(draftdatabase):
	#returns number of teams in the league based on number of picks in the first round
	#starting from 1977
	teamnum = {}
	for row in draftdatabase:
		if int(row['draft_year']) < 1977:
			continue
		if row['draft_round'] == '1' and 'selection' in row:
			teamnum[int(row['draft_year'])] = max(int(row['selection']), teamnum.get(row['draft_year'], 0))
	return teamnum

def get_teams_drafting_never_played(draftfile, firstdraftyear = 1977, lastdraftyear = 2008, rounddrafted = 1):
	teams = {}
	for row in draftfile:
		draftyear = int(row['draft_year'])
		roundd = int(row['draft_round'])
		if draftyear >= firstdraftyear and draftyear <= lastdraftyear and roundd == rounddrafted:
			if row['ilkid'] == 'NULL':
				teams[row['team']] = teams.get(row['team'], 0) + 1
	return teams
def get_X_by_Y(xkey, ykey, database, avg = False):
	dictionary = {}
	count_both = 0;
	for key in database:
		row = database[key]
		if not (xkey in row and ykey in row):
			continue
		if 'draft_year' in row and (row['draft_year'] < 1984 or row['draft_year'] > 2005):
			continue;
		count_both += 1
		temp = dictionary.get(row[ykey], [])
		temp.append(row[xkey])
		dictionary[row[ykey]] = temp
	if avg:
		for key in dictionary:
			dictionary[key] = sum(dictionary[key])/len(dictionary[key])
	return dictionary
def plotBarPlotFromDictionary(D):
	fig = plt.figure()
	Y = D.values()
	X = D.keys()
	X = [x for y, x in sorted(zip(Y, X))]
	Y = sorted(Y)

	width = 2
	ind = np.arange(len(Y))
	plt.bar(ind, Y)
	plt.xticks(ind + width / 2, X)

#	plt.bar(range(len(D)), Y, align='center')
#	plt.xticks(range(len(D)), X)
	fig.autofmt_xdate()
	plt.savefig('foo.png')

draftfile = load_file('draft.csv')
players = load_file('player_career.csv')
combined = combine_by_key(draftfile, players, 'ilkid')
GamesPlayed_by_TeamDrafted = get_X_by_Y('minutes', 'team', combined, avg = True)
print GamesPlayed_by_TeamDrafted
plotBarPlotFromDictionary(GamesPlayed_by_TeamDrafted)
teamnum = get_number_of_teams_in_league(draftfile)
teams_fail_draft = get_teams_drafting_never_played(draftfile)
teams_fail_draft2 = get_teams_drafting_never_played(draftfile, rounddrafted = 2)

#print teams_fail_draft
#print teams_fail_draft2
#print teamnum
