recipes = {'Test Recipe': {'requirements': [{'item': 'Test Item 1',
                                             'optional': False},
                                            {'item': 'Test Item 2',
                                             'optional': True}],
                           'steps': [{'name' : 'Test Step 1',
                                      'done' : False},
                                     {'name' : 'Test Step 2',
                                      'done' : False}]}}

items = {'Test Item 1': {'color': [0, 255, 255],
                         'tolerance': [16, 96, 96],
                         'minArea': 250},
         'Test Item 2': {'color': [40, 255, 255],
                         'tolerance': [16, 96, 96],
                         'minArea': 250}}
