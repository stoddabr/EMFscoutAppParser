import pandas as pd
import json

###################################
#       Farm class definition
###################################


class Farm:
    # class for holding, calculating, and updating field threat levels for a single farm
    # TODO:
    #   use euclidean norms and lat,long in center of fields for lat,lon->field mapping
    #       this is needed for non-square fields
    #   use time stamps
    #       this is needed to build a time map for threat values in each field using reports

    def __init__(self, field_list, disease_list, field_gps_info):
        # fields is an array with field numbers
        self.field_info = field_gps_info
        self.fields = field_list
        self.diseases = field_list
        self.df = pd.DataFrame(
            data=[[[0, 0] for _ in disease_list]],  # default empty values; [threat,num reports]
            columns=disease_list,
            index=field_list
        )

    def add_single_report(self, field, threat, disease):
        # add a report to the field, update df
        # data should be an array with same order as columns, 6 items
        prev_threat, prev_reports = self.df.loc[field, disease]
        new_threat = (prev_threat * prev_reports + threat) / (prev_reports + 1)

        # update stored field info
        self.df.loc[field, disease] = [new_threat, prev_reports+1]

    def add_report_from_df(self, report_df):
        # updates internal df with the report
        # takes data from a single-row df with the following columns, default index

        # replace 'lat' and 'lon' columns with 'field'
        report_df['field'] = pd.Series(
            [self.field_from_lat_long(report_df.loc[j, 'latitude'],
                                      report_df.loc[j, 'longitude'])

             for j in report_df.index]
        )
        report_df = report_df.drop(columns=['latitude', 'longitude'])

        print(report_df)

        # put report_df into array format to feed it into add_report_array
        for j in report_df.index:
            self.add_single_report(report_df.loc[j, 'field'],
                                   report_df.loc[j, 'severity'],
                                   report_df.loc[j, 'disease'])

    def field_from_lat_long(self, latitude, longitude):
        # MVP, create grid with corners, classify by switch statements
        for k in self.field_info['order']:
            f_lat, f_lon = self.field_info['botRight'][k]
            if latitude > f_lat and longitude < f_lon:
                return self.field_info['field'][k]

        return 404  # field not found

    def print_df(self):
        # print the dataFrame
        print(self.df)

    def remove_num(self):
        no_num_df = pd.DataFrame(
            data=[[self.df.loc[row, col][0]
                  for col in self.df.columns]
                  for row in self.df.index],
            index=self.df.index,
            columns=self.df.columns
        )
        print(no_num_df)
        return no_num_df

    def to_JSON(self):
        print([self.df.loc[row, col][0]
               for row in self.df.index
               for col in self.df.columns])
        # return df as JSON string
        return self.remove_num().to_json(orient='index')

    def to_excel(self, file_name):
        # saves as excel 2010 file using openpyxl
        self.remove_num().to_excel(file_name, sheet_name='Sheet1')

    def to_csv(self, file_name):
        self.remove_num().to_csv(file_name)


###########################################################
#        Field specific info (for Elk Mountain Farms)
###########################################################

emf_fields = [51, 41, 52, 42, 53, 43, 31,
          21, 11, 32, 22, 33, 23, 12,
          404]  # 404 is used for not valid fields

emf_diseases = ['Spider Mite', 'Downy Mildew (Primary Infection)',
            'Downy Mildew (Secondary Infection)',
            'Bertha Armyworms', 'Powdery Mildew', 'Aphid',
            ]

emf_field_gps_info = {
    # Start top left like reading a book with two pages with a crease down the center
    'field': [51, 41,
              52, 42,
              53, 43,
              31, 21, 11,
              32, 22,
              33, 23, 12],
    # bottom right corner of each field, found from google earth
    'botRight': [(48.990948, -116.522334), (48.991517, -116.515995),
                 (48.987710, -116.521631), (48.988252, -116.515086),
                 (48.985037, -116.520768), (48.985024, -116.514611),
                 (48.991111, -116.509549), (48.991681, -116.502916), (48.992418, -116.497356),
                 (48.987749, -116.508661), (48.988291, -116.501987),
                 (48.984388, -116.507812), (48.984806, -116.501284), (48.985105, -116.493662)
                 ],
    # avoid errors caused by fields not being perfectly lined up N-S/E-W
    'order': [0, 1, 2, 6, 3, 4, 5, 7, 9, 10, 11, 8, 12, 13]
}

# set object, emf = Elk Mountain Farms
emf = Farm(emf_fields, emf_diseases, emf_field_gps_info)

##################################################
#          Example using agromoai-export.json
##################################################

# JSON to DF
with open('agromoai-export.json') as f:
    data = json.load(f)

df_json = pd.DataFrame(data['mites']).transpose()
df_json.index = [i for i in range(len(df_json.index))]
print(df_json)

# print it before and after adding the report
# to show change in data structure
emf.print_df()
emf.add_report_from_df(df_json)

# print JSON
print(emf.to_JSON())
emf.to_excel('EMF pd.xlsx')
emf.to_csv('EMF pd.csv')
