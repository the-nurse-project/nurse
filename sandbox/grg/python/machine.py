import sys

def progressive_display ( text, speed = 'FAST' ) :
    speed_dict = { 'FAST': 0.015, 'NORMAL': 0.1, 'SLOW': 0.2}
    import time
    for i, char in enumerate ( text ):
        sys.stdout.write ( char )
        sys.stdout.flush()
        time.sleep ( speed_dict[speed] )

def ask_for_action ( actions ) :
    text = ''
    for each in actions.keys() :
        text = text + str(actions[each]) + ' (' + str(each) + ') '
    text = text + 'QUIT (q)'
    #text = text[0:-1]
    print text
    do_ask = True
    while ( do_ask ) :
        action = raw_input()
        if action[0] in actions.keys() or action[0] is 'q' :
            do_ask = False
    if action[0] in actions.keys() :
        print 'You chose to ' + actions[action[0]] + '.'
        return actions[action[0]]
    elif action[0] is 'q':
        return 'QUIT'

def process_rules ( machine_states, rules, action ) :
    changes = -1
    iter_nb = 0
    while changes != 0:
        iter_nb = iter_nb + 1
        changes = 0
        for rule in rules :
            conditionsAreSatisfied = True
            for each in rule[0].keys():
                if each == 'action':
                    #print rule[0][each], action
                    if rule[0][each] != action :
                        conditionsAreSatisfied = False
                else:
                    #print machine_states[each], rule[0][each]
                    if machine_states [each] != rule[0][each]:
                        conditionsAreSatisfied = False
            if conditionsAreSatisfied :
                #print 'ok'
                for each in rule[1].keys() :
                    if each == 'PRINT':
                        progressive_display ( rule[1][each] )
                    else :
                        if machine_states[each] != rule[1][each] :
                            changes = changes + 1
                            machine_states[each] = rule[1][each]
            #else :
                #print 'not ok'
        print "iteration :", iter_nb, "changes :", changes


    
intro = \
"I awake in a dark room. \n\
I don't precisely recall how I got there.\n\
My last memory was driving from work back home.\n"

#ways = { 'EXAMINE' : 'I am at present laying in a bed facing some unknown \
#ceiling.\nThe room is quite small, with a closed window on the right and a door \
#on the left.',
#'USE' : 'There is nothing to use',
#'GO' :

rules = [ ( { 'location' : 'room',
            'did_examine_room' : False,
            'action' : 'EXAMINE' },
          { 'did_examine_room' : True,
            'PRINT' : 'I am at present laying in a bed facing some unknown \
ceiling.\nThe room is quite small, with a closed window on the right and a door \
on the left.\n',
            'actions' : {'u' : 'USE',
                        'g' : 'GO'} } ) ,

          ( { 'location' : 'room',
            'did_examine_room' : False,
            'action' : 'GO' },
          { 'PRINT' : 'I don\'t know anywhere to go.\n' } ) ,

          ( { 'location' : 'room',
            'action' : 'USE' },
          { 'PRINT' : 'I have nothing to use.\n' } ) ,

          ( { 'location' : 'corridor',
            'action' : 'USE' },
          { 'PRINT' : 'I have nothing to use.\n' } ) ,

          ( { 'location' : 'room',
            'did_examine_room' : True,
            'action' : 'GO' },
          { 'PRINT' : 'I go to the door. The door is open.\n',
            'location' : 'corridor',
            'actions' : { 'e' : 'EXAMINE',
                          'u' : 'USE',
                          'g' : 'GO' } } ),

          ( { 'location' : 'corridor',
            'did_meet_nurse' : False,
            'action' : 'EXAMINE' },
          { 'PRINT' : 'There is a strange... NURSE !\n' } )

        ]

machine_states = { 'did_examine_room' : False,
            'location' : ['room', 'corridor', 'next room', 'hall', 'outside'] [0],
            'did_meet_nurse' : False,
            'actions' : { 'e' : 'EXAMINE',
                          'u' : 'USE',
                          'g' : 'GO' }
    }

disp = progressive_display
disp ( intro )
action = ''
while action != 'QUIT':
    action = ask_for_action ( machine_states['actions'] )
    process_rules ( machine_states, rules, action )





