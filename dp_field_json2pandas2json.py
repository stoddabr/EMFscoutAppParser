import pandas as pd
import json

'''
def field_from_lat_long(latitude, longitude):
    #MVP, create grid with corners, classify by switch statements
    fieldInfo = {
        #start top left like reading a book with two pages with a crease down the center
        'field':[51,41,
                 52,42,
                 53,43,
                 31,21,11,
                 32,22,
                 33,23,12],
        'botRight':[(48.990948,-116.522334),(48.991517,-116.515995),
                    (48.987710,-116.521631),(48.988252,-116.515086),
                    (48.985037,-116.520768),(48.985024,-116.514611),
                    (48.991111,-116.509549),(48.991681,-116.502916),(48.992418,-116.497356),
                    (48.987749,-116.508661),(48.988291,-116.501987),
                    (48.984388,-116.507812),(48.984806,-116.501284),(48.985105,-116.493662)
                    ]
    }
    #to avoid major errors caused by fields not being lined up perfectly N-S, E-W
    #compare the fields in this order
    order = [0,1,2,6,3,4,5,7,9,10,11,8,12,13]

    for i in order:
        f_lat,f_lon = fieldInfo['botRight'][i]
        if latitude > f_lat and longitude < f_lon:
            return fieldInfo['field'][i]

    return 404 #field not found
'''


class Farm:
    # class for holding, calculating, and updating field threat levels for a single farm
    # TODO:
    #   make it so lat,lon->field mapping data modifiable on init
    #   use euclidean norms and lat,long in center of fields for lat,lon->field mapping

    def __init__(self, field_list, disease_list):
        # fields is an array with field numbers
        self.fields = field_list
        self.diseases = field_list

        self.df = pd.DataFrame(
            columns=disease_list,
            index=field_list
        )
        self.df['OTHER_NAME'] = pd.Series(['default' for i in field_list],
                                          index=field_list
                                          )
        self.df = self.df.fillna(value=0)

    def add_report_array(self, field, new_data):
        # add a report to the field, update df
        # data should be an array with same order as columns, 6 items

        num_prev_reports = self.df.loc[field, 'num_reports']
        other_name = new_data[-1]

        new_data = [(self.df.loc[field, self.diseases[i]] * num_prev_reports + new_data[i])
                    / (num_prev_reports + 1)
                    for i in range(5)]  # SM through OTHER

        new_data.append(other_name)
        new_data.append(num_prev_reports + 1)  # add 1 to prev reports
        self.df.loc[field] = data  # update stored field info

    def add_report_df(self, report_df):
        # updates internal df with the report
        # takes data from a single-row df with the following columns, default index
        # 'unix_time', 'lat','lon','SM','PRED','PM','DM','OTHER','OTHER_NAME'

        # replace 'lat' and 'lon' columns with 'field'
        for j in report_df.index:
            print(self.field_from_lat_long(report_df[j, 'latitude'],
                                           report_df[j, 'longitude']))
            print(report_df[j, 'latitude'])

        report_df['field'] = pd.Series(
            [self.field_from_lat_long(report_df.loc[j, 'latitude'],
                                      report_df.loc[j, 'longitude'])

             for j in report_df.index]
        )
        report_df = report_df.drop(columns=['latitude', 'longitude'])
        print(report_df)
        # put report_df into array format to feed it into add_report_array
        for j in report_df.index:
            report_array = [report_df.loc[j, i] for i in self.diseases]
            self.add_report_array(report_df.loc[j, 'field'], report_array)

    def field_from_lat_long(self, latitude, longitude):
        # MVP, create grid with corners, classify by switch statements
        fieldInfo = {
            # Start top left like reading a book with two pages with a crease down the center
            'field': [51, 41,
                      52, 42,
                      53, 43,
                      31, 21, 11,
                      32, 22,
                      33, 23, 12],
            'botRight': [(48.990948, -116.522334), (48.991517, -116.515995),
                         (48.987710, -116.521631), (48.988252, -116.515086),
                         (48.985037, -116.520768), (48.985024, -116.514611),
                         (48.991111, -116.509549), (48.991681, -116.502916), (48.992418, -116.497356),
                         (48.987749, -116.508661), (48.988291, -116.501987),
                         (48.984388, -116.507812), (48.984806, -116.501284), (48.985105, -116.493662)
                         ]
        }
        # to avoid major errors caused by fields not being lined up perfectly N-S, E-W
        # compare the fields in this order
        order = [0, 1, 2, 6, 3, 4, 5, 7, 9, 10, 11, 8, 12, 13]
        for i in order:
            f_lat, f_lon = fieldInfo['botRight'][i]
            if latitude > f_lat and longitude < f_lon:
                return fieldInfo['field'][i]

        return 404  # field not found

    def print(self):
        # print the dataFrame
        print(self.df)

    def returnDf(self):
        # return the df
        return self.df

    def remove_num(self):
        no_num_df = pd.DataFrame(
            data=[self.df.loc[row, col][0] for row, col in self.df.iterrows],
            index=self.df.index,
            columns=self.df.columns
        )
        print(no_num_df)
        return no_num_df

    def to_JSON(self):
        print([self.df.loc[row, col][0] for row, col in self.df.itterrows])
        # return df as JSON string
        return 3
            #self.remove_num().to_json(orient='index')


fields = [51, 41, 52, 42, 53, 43, 31,
          21, 11, 32, 22, 33, 23, 12]
diseases = ['Spider Mite', 'Downy Mildew (Primary Infection)',
            'Downy Mildew (Secondary Infection)',
            'Bertha Armyworms', 'Powdery Mildew', 'Aphid',
            ]

emf = Farm(fields, diseases)

# JSON to DF
with open('agromoai-export.json') as f:
    data = json.load(f)
df_json = pd.DataFrame(data['mites']).transpose()

# print it before and after adding the report
emf.print()
for i in range(len(df_json.index)):
    emf.add_report_df(df_json)
emf.print()

# print JSON
print(emf.to_JSON())

'''example DF used for testing
df = pd.DataFrame(data=[[52241, 48.986, -116.512, 3, 1, 0, 1, 10, 'hops']],
                  columns=['unix_time', 'lat', 'lon', 'SM', 'PRED',
                           'PM', 'DM', 'OTHER', 'OTHER_NAME']
                  )
'''

'''#example
field = field_from_lat_long(48.986,-116.512)
print(field)
'''

'''
df['field'] = pd.Series(
                [ field_from_lat_long(df.loc[j,'lat']
                              ,df.loc[j,'lon'])
                for j in range(len(df.index)) ]
            )

df = df.drop(columns=['lat','lon'])
'''

'''
stuff from before started using a class
#add a report to the field, update df
df = pd.DataFrame(data=[[52241,48.986,-116.512,3,1,0,1,10,'hops'],
                  [53512,48.996,-116.532,3,1,0,1,11,'hops']],
                   columns=['unix_time','lat','lon','SM','PRED',
                            'PM','DM','OTHER','OTHER_NAME']
                  )

df['field'] = pd.Series(
        [ field_from_lat_long(df.loc[j,'lat']
                            ,df.loc[j,'lon'])
        for j in range(len(df.index)) ]
      )

df = df.drop(columns=['lat','lon'])

#print(df)

rawJSON = df.to_json(orient='index')
print( rawJSON )
'''
