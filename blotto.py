from itertools import product
from functools import reduce
import nashpy as nash
import numpy as np
import operator


#Generates a list of possible actions for a given number of resources
def list_actions(res):
    temp = list(product(range(0,res+1), repeat = 3))
    return [item for item in temp if reduce(operator.add, item) == res]

#Prints an array's contents with no extra symbols for readability
def print_list(arr):
    for row in arr:
        print(*row)

#Takes in a list of actions and payoff matrix for each player and removes all dominated strategies
def remove_dominated(row_list,col_list,row_payoff,col_payoff):

    has_dominated = 1 #Makes loop run at least onece

    #Copies row/column chooser action lists to be modified 
    temp_row_list = row_list.copy()
    temp_col_list = col_list.copy()

    #Loop runs until there are no more dominated strategies detected
    while has_dominated:
        has_dominated = 0

        #Returns list of indecies to remove and the adjusted payoff matrices with either dominated rows or columns removed (not both)
        row_strats,temp_row_payoff = remove_dominated_rows(row_payoff)
        col_strats,temp_col_payoff = remove_dominated_rows(np.array(col_payoff).T.tolist()) #Transposes matrix so the same function can be used

        #List of return variables
        new_row_list = []
        new_col_list = []
        row_payoff = []
        col_payoff = []

        #Indicates if any dominated strategies were found
        has_dominated = len(row_strats) > 0 or len(col_strats) > 0 

        #Remove dominated rows and deletes those rows from the column chooser's payoff matrix
        for i in range(len(temp_row_list)):
            if i not in row_strats:
                new_row_list.append(temp_row_list[i])
                col_payoff.append(temp_col_payoff[i])
        temp_row_list = new_row_list.copy()

        #Remove dominated columns and deletes those columns from the row chooser's payoff matrix
        for i in range(len(temp_col_list)):
            if i not in col_strats:
                new_col_list.append(temp_col_list[i])
                row_payoff.append(temp_row_payoff[i])
        temp_col_list = new_col_list.copy()

        #Transposes the row payoff matrix to its original orientation (since remove_dominated_rows returns a transposed version of the matrix to make the previous steps easier)
        row_payoff = np.array(row_payoff).T.tolist() 

    #Return results
    return new_row_list,new_col_list,row_payoff,col_payoff

#Takes a payoff matrix and returns list of indecies to remove and the adjusted payoff matrices with either dominated rows or columns removed (not both)
def remove_dominated_rows(payoff):

    #Holds the list of indecies for the dominated rows
    list_dominated = [] 

    #Iterates through each set of rows to see if all values in one row is equal to or greater than the corresponding values in another row
    for row1 in range(len(payoff)-1):
        for row2 in range(row1+1,len(payoff)):
            if row1 not in list_dominated and row2 not in list_dominated: #Doesn't check rows that are already confirmed to be dominated strategies
                
                #Marks row1 as either dominant or dominated to check whether row1 or row2 are dominated strategies
                is_dominated = 1
                is_dominant = 1
                for i in range(len(payoff[row1])):
                    if payoff[row1][i] < payoff[row2][i]:
                        is_dominant = 0
                    elif payoff[row1][i] > payoff[row2][i]:
                        is_dominated = 0

                #If both rows contain the same values then it will not be considered dominated
                if is_dominant and not is_dominated:
                    list_dominated.append(row2)
                elif is_dominated and not is_dominant:
                    list_dominated.append(row1)
    
    #Generates a new payoff matrix with the dominated rows removed
    result = []
    for i in range(len(payoff)):
        if i not in list_dominated:
            result.append(payoff[i])
    
    return list_dominated,np.array(result).T.tolist() #Transposes output to make removing dominated columns easier

if __name__ == '__main__':

    max_res = 10 #Maximum resources tested
    iterations = 1000 #Number of rounds per game of ficticious play
    num_games = 1000 #Number of games played
    rand_seed = 0

    exp_a = [[0]*(max_res) for num in range(max_res)]
    exp_d = [[0]*(max_res) for num in range(max_res)]
   
    for a_res in range(1,max_res+1): 
        for d_res in range(1,max_res+1):

            a_list = list_actions(a_res) #column chooser
            d_list = list_actions(d_res) #row chooser

            #Generate blank payoff matrices
            a_payoff = [[0]*len(a_list) for i in range(len(d_list))] #column chooser
            d_payoff = [[0]*len(a_list) for i in range(len(d_list))] #row chooser
            
            #Calculates the payoff of each player for each combination of actions
            for i in range(len(a_list)):
                a = a_list[i]
                for j in range(len(d_list)):
                    d = d_list[j]
                    for n in range(3): #iterates through each node
                        #Center node is worth twice the outer nodes
                        p = 1 + 1 * int(n == 1)
                        #No points gained for "disabled" nodes or when a[n] == d[n]
                        if a[n] > d[n]:
                            a_payoff[j][i] += p #Attacker gain
                            d_payoff[j][i] -= p #Defender loss
                        elif (a[n] < d[n]) or (a[n] == 0):
                            d_payoff[j][i] += p #Defender gain

            #Removing dominated strategies
            new_d_list,new_a_list,new_d_payoff,new_a_payoff = remove_dominated(d_list,a_list,d_payoff,a_payoff)
            
            #Generate the game using the new payoff matrices to reduce calculation time
            print("Simulating games with",d_res,"defender resources and",a_res,"attacker resources")
            game = nash.Game(new_d_payoff, new_a_payoff)
            play_results = []
            
            #Generate results for each game being played
            for i in range(num_games):
                np.random.seed(rand_seed) #Generate a different seed for each game
                rand_seed = rand_seed + 1
                play_counts = game.fictitious_play(iterations=iterations)
                count = 1

                #Only record the totals after the last round
                for row, column in play_counts:
                    if count == iterations:
                        play_results.append([row,column]) 
                    count = count + 1

            #Sum up the number of rounds that each strategy was used
            sum_strats_d = [[0]*len(new_d_list)]
            sum_strats_a = [[0]*len(new_a_list)]
            for i in play_results:
                sum_strats_d = sum_strats_d + i[0]
                sum_strats_a = sum_strats_a + i[1]
            
            rounds = num_games * iterations #Caluclate total rounds

            #Calculate the usage rates for each strategy
            avg_strats_d = [x / rounds for x in sum_strats_d]
            avg_strats_a = [x / rounds for x in sum_strats_a]

            #Truncate the results to 2 decimal places
            avg_strats_d_trunc = [np.round(x,2) for x in avg_strats_d]
            avg_strats_a_trunc = [np.round(x,2) for x in avg_strats_a]

            #Caluclating expected payoff for each player
            exp_a_sum = 0.0
            exp_d_sum = 0.0
            for i in range(len(avg_strats_d[0])):
                for j in range(len(avg_strats_a[0])):
                    freq = avg_strats_d[0][i] * avg_strats_a[0][j]
                    exp_a_sum = exp_a_sum + float(new_a_payoff[i][j]) * freq
                    exp_d_sum = exp_d_sum + float(new_d_payoff[i][j]) * freq

            #Save expected payoffs for output
            exp_a[d_res-1][a_res-1] = round(exp_a_sum,2)
            exp_d[d_res-1][a_res-1] = round(exp_d_sum,2)

    #Print results
    print("\nExpected payoffs:")
    
    print("Defender Expected Payoff:")
    print_list(exp_d)
    print("Attacker Expected Payoff:")
    print_list(exp_a)

    #Save results to a csv for further analysis
    np.savetxt('defenderpayoff.csv',exp_d, fmt = '%.2f', delimiter=",")
    np.savetxt('attackerpayoff.csv',exp_a, fmt = '%.2f', delimiter=",")  
