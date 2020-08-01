# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 20:47:11 2020

@author: devli
"""

import time
import random
import pandas as pd
pd.set_option('display.max_rows',None)


class RunTest:

    points_structure = {'R1_no_q':30,'R1_correct':1,'R1_incorrect':-3,'R1_pass':-2,\
                    'R2_no_q':30,'R2_correct':2,'R2_incorrect':-1,'R2_pass':-1,\
                    'R3_no_q':15,'R3_correct':2,'R3_incorrect':-2,'R3_pass':-1}
    
    
    def __init__(self,full_test,rnd):
        self.full_test = full_test
        self.rnd = rnd
    
    
    def run_test(self,full_test,rnd):
        start = Watch.start_stopwatch()
        result = self.test(rnd)
        stop = Watch.stop_stopwatch()
        time_taken = round(stop - start,2)
        if not result:
            return
        elif full_test:
            return result[0], result[1], time_taken, result[2]
        else:
            self.performance_output(result[0],result[1],time_taken, result[2])


    def test(self,rnd):
        q = 1
        points = 0
        history = pd.DataFrame(columns=['Question','Correct Answer','Given Answer'])
        while q <= self.points_structure['R'+str(int(rnd))+'_no_q']:
            question, answer = self.generate_questions(rnd)
            ans = self.answers()
            if ans == 'q':
                return
            elif ans == '':
                points+=self.points_structure['R'+str(rnd)+'_pass']
                history.loc[len(history)] = [question,round(answer,2),ans]
                q+=1
                continue
            elif round(ans,2) == round(float(answer),2):
                points+=self.points_structure['R'+str(rnd)+'_correct']
            else:
                points+=self.points_structure['R'+str(rnd)+'_incorrect']
            history.loc[len(history)] = [question,round(answer,2),round(float(ans),2)]
            q+=1
        return points, str(int(points/(self.points_structure['R'+str(rnd)+'_correct']*\
                            self.points_structure['R'+str(rnd)+'_no_q'])*100))+'%',history


    def entire_test(self):
        start = Watch.start_stopwatch()

        result_r1 = self.run_test(True,1)
        if not result_r1:
            return
        result_r2 = self.run_test(True,2)
        if not result_r2:
            return
        result_r3 = self.run_test(True,3)
        if not result_r3:
            return

        stop = Watch.stop_stopwatch()
        time_taken = round(stop - start,2)
        points = result_r1[0] + result_r2[0] + result_r3[0]
        perc = str(int(points/120)*100)+'%'
    
        final_dict = {'Round 1':result_r1[:-1],'Round 2':result_r2[:-1],'Round 3':result_r3[:-1],\
                  'Total':(points,perc,time_taken)}
        output = pd.DataFrame(data=final_dict,index=['Points','Percent','Time (seconds)'])
        print('\n')
        print(output)
        time.sleep(3)
        print('\n\nType "y" if you would you like to see a breakdown of all questions.\
          Otherwise press "enter" to exit.')
        ans = input()
        if ans == 'y':
            all_questions = pd.concat([result_r1[3],result_r2[3],result_r3[3]],ignore_index=True)
            print(all_questions)
            print('\n')
        return


    def generate_questions(self,rnd):
        operations = ['+','-','*','/']
        if rnd == 1:
            op = random.choice(operations)
            if op == '*':
                left, right = random.randint(1,99), random.randint(1,10)
                question = str(left) + op + str(right)
                answer = left*right
            elif op == '/':
                numerator = random.randint(2,99)
                denominator = random.choice([i for i in range(1,numerator) if numerator%i == 0])
                question = str(numerator) + op + str(denominator)
                answer = numerator/denominator
            else:
                left, right = random.randint(1,99), random.randint(1,99)
                question = str(left) + op + str(right)
                answer = left + right if op == '+' else left - right
    
        elif rnd == 2:
            op = random.choice(operations)
            if op == '*':
                left, right = float(random.randint(1,99)/100), float(random.randint(1,99)/100)
                question = str(left) + op + str(right)
                answer = left*right
            elif op == '/':
                numerator = random.randint(2,999)
                denominator = random.choice([i for i in range(1,numerator) if numerator%i == 0])
                question = str(numerator/100) + op + str(denominator/100)
                answer = numerator/denominator
            else:
                left, right = random.randint(1000,9999)/100, random.randint(1000,9999)/100
                question = str(left) + op + str(right)
                answer = left + right if op == '+' else left - right
            
        elif rnd == 3:
            left, right = random.randint(1,5000)/random.choice([1,100]), random.randint(1,5000)/random.choice([1,100])
            question = str(left) + '*' + str(right)
            answer = left*right

        print('\n'+question)
        return question,answer


    def answers(self):
        while True:
            ans = input()
            try:
                if str(ans) == 'q' or str(ans) == '':
                    break
                else:
                    ans = float(ans)
            except ValueError:
                print('Please enter a valid answer.')
                continue
            break
        return ans


    def performance_output(self,points,percentage,time_taken,all_questions):
        print('\nTime Taken: '+str(round(time_taken,2)) + ' seconds')
        print('Points: ' + str(points))
        print('Percentage mark: ' + percentage)
        time.sleep(3)
        print('\nIf you would like to see a breakdown of all questions and answers\
          press "y". Otherwise hit "enter" to continue.')
        ans = input()
        if ans.lower() == 'y':
            print(all_questions)
            print('\n')
        return


class Watch:
    
    def start_stopwatch():
        return time.time()

    def stop_stopwatch():
        return time.time()


class Instructions:
    
    def instructions():
        print("""
          To skip any question and move onto the next one simply hit the enter 
          key rather than submitting an answer. 
          To quit the test at any stage simply type "q".
          The maximum score possible is 120 points. The points structure
          differs in each round and negative marking is employed.
          
          Round 1 consists of 'easy' questions which could be addition, 
          subtraction, multiplication or division.
          Total questions:   30
          Correct answer:    1 point
          Incorrect answer: -3 points
          No answer:        -2 points
          
          Round 2 consists of decimal questions which could be addition, 
          subtraction, multiplication or division.
          Total questions:   30
          Correct answer:    2 points
          Incorrect answer: -1 points
          No answer:        -1 points
          
          Round 3 consists of more difficult multiplication questions.
          Total questions:   15
          Correct answer:    2 points
          Incorrect answer: -2 points
          No answer:        -1 points
          
          The full test consists of taking the above three rounds 
          consecutively. You should aim to complete this under 10 minutes and 
          be scoring at least 60%.
          
          
          Hit 'enter' to continue.
          """)
        input()
        return   

def program():
    
    while True:
        print("""What round do you want to test?:\n1. First round (Easy)\
              \n2. Second round (Decimals)\n3. Third round (Difficult Multiplication)\
              \n4. Full Test\n5. Instructions\n\nOr type "q" to quit the test
              """)
        ans = input()
        if ans == '1':
            r = RunTest(False,1)
            r.run_test(False,1)
        elif ans == '2':
            r = RunTest(False,2)
            r.run_test(False,2)
        elif ans == '3':
            r = RunTest(False,3)
            r.run_test(False,3)
        elif ans == '4':
            r = RunTest(True,'all')
            r.entire_test()
        elif ans == '5':
            Instructions.instructions()
        elif ans == 'q':
            break
        else:
            print('\nPlease enter a valid number corresponding to one of the above options\n')

if __name__ == "__main__":
    program()