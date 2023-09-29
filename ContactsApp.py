import streamlit as st
# from streamlit_dynamic_filters import DynamicFilters
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import pandasql as psql
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

url = "https://docs.google.com/spreadsheets/d/10dpcDXGzsd8Hl_2derZ1kc6wO0tPI0N7IDs0DOGpVr8/edit?usp=sharing"
conn = st.experimental_connection('gsheets', type=GSheetsConnection, ttl=1)
# dfgoogle = conn.read(worksheet="362554757")
#Method 1:
dff = conn.read(worksheet="Master Contact List2", usecols=list(range(12)))
dff = dff.dropna(how='all').fillna("").reset_index() #resetting index so that the index stays when merging so when saving back to google I can map the filtered row to the original DF.
dff.rename(columns = {'index': 'gsIndex'}, inplace = True)



@st.cache_data
def get_data(path):
    # path = "C:\\Users\\patri\\Documents\\Contacts\\VoteRefDataWithPrecinct2.csv"
    return pd.read_csv(path).fillna("")

def clear_inputs():
    st.session_state["name_search"] = ""
    st.session_state["district_choice"] = "All"
    st.session_state["street_choice"] = "All Streets"
    st.session_state["votingCB0"] = 1
    st.session_state["votingCB1"] = 1
    st.session_state["votingCB2"] = 1
    st.session_state["votingCB3"] = 1
    st.session_state["votingCB4"] = 1
    st.session_state["votingCB5"] = 1

def merge_dataframe_for_export(dfo, dfn): #df original & df new
    dfj = dfo.merge(dfn, how='left', on='index', suffix='_y')
    print(f'dfj shae: {dfj.shape}')
    dfo['Last Name'] = dfj['Last Name_y']
    dfo['First Name'] = dfj['First Name_y']
    dfo['Phone'] = dfj['Phone_y']
    dfo['e-mail'] = dfj['e-mail_y']
    dfo['Alt e-mail'] = dfj['Alt e-mail_y']
    dfo['Address'] = dfj['Address_y']
    dfo['Comments'] = dfj['Comments_y']
    dfo['Source Comments'] = dfj['Source Comments_y']
    dfo['Full Name'] = dfj['Full Name_y']
    dfo['Signed Petition'] = dfj['Signed Petition_y']
    dfo['GACC Member'] = dfj['GACC Member_y']
    dfo['Church'] = dfj['Church_y']
    return dfo.drop(['index'],axis=1)



#Get data and clean up dataframes
df = get_data("C:\\Users\\patri\\Documents\\Contacts\\VoteRefDataWithPrecinct3.csv")
# dff = get_data("C:\\Users\\patri\\Documents\\Contacts\\ContactInformationList.csv")

df = df.drop(['ID','Index','Column2','Column1','Street','DOB','Voting History','Party Affiliation'], axis=1)
# dfj = df.join(dff.set_index('Full Name'), rsuffix='_CL', on='Full Name', validate='m:1')
# dfj = df.merge(dff, left_on=df['Full Name'].str.lower(), right_on=dff['Full Name'].str.lower(), how='left')
# print(dfj)
dfj2 = df.merge(dff.set_index(dff['Full Name'].str.lower()), left_on=df['Full Name'].str.lower(), right_index=True, how='left', suffixes=('','_CL'))

dfj = dfj2.drop('Full Name_CL', axis=1)
# df_merged = pd.merge(df_address, df_CountryMapping, left_on=df_address["Country"].str.lower(), right_on=df_CountryMapping["NAME"].str.lower(), how="left")
# new_df = Employee_Logs_df.merge(HR_Data_df.set_index('employee_id'), left_on=Employee_Logs_df.employee_id .str.extract('(.*\d+)',expand=False), right_index=True)
# dfj.to_csv("joinedContactsTest.csv")

#add column that represents a count of particular name in thomas county.
dfj['Count'] = 1
namecount = dfj.groupby('Full Name').Count.count().reset_index() #this is a new dataframe with only full name and count
dfj = dfj.drop('Count', axis=1)
dfj = dfj.join(namecount.set_index('Full Name'), on='Full Name', validate='m:1') # add the count column to the full dataset

st.sidebar.subheader('Location Filters')

# districts = df['District'].drop_duplicates()
districts = ['All', 'D1', 'D2', 'City', 'County']
district_choice = st.sidebar.selectbox('Select District:', districts, key='district_choice')

if district_choice == 'All':
    df2 = df
elif district_choice == 'City':    
    df2 = df.loc[(df['District']=="D1") | (df['District']=="D2")]
else:
    df2 = df[df['District']==district_choice]
streets = df2['StreetText'].drop_duplicates()
# dfdisplay = dfdisplay[dfdisplay["Vote History"].isin(voting_hist_choices2)]
streets.loc[-1] = 'All Streets'  # adding a row
streets.index = streets.index + 1  # shifting index
streets.sort_index(inplace=True) 
street_choice = st.sidebar.selectbox(f"Select Street ({streets.shape[0]}):", streets, key='street_choice')

st.sidebar.divider()
st.sidebar.subheader('Voting Filters')

regStatus = df['Registration Status'].drop_duplicates()
regStatus.loc[-1] = 'Everyone'  # adding a row
regStatus.index = regStatus.index + 1  # shifting index
regStatus.sort_index(inplace=True) 
reg_status_choice = st.sidebar.selectbox("Filter By Registration Status:",regStatus,0, key='reg_status_choice')

st.sidebar.write("Times Voting in past 4 years")
c1, c2, c3, c4, c5 = st.sidebar.columns(5)
votingCB0 = c1.checkbox("0", value=0, key='votingCB0')
votingCB1 = c2.checkbox("1", value=1, key='votingCB1')
votingCB2 = c3.checkbox("2", value=1, key='votingCB2')
votingCB3 = c4.checkbox("3", value=1, key='votingCB3')
votingCB4 = c5.checkbox("4", value=1, key='votingCB4')




st.sidebar.divider()
st.sidebar.subheader('Name Filter')
name_search = st.sidebar.text_input("Search Name:", key='name_search')
st.sidebar.caption('Also searches middle names.')


st.sidebar.button("Reset All", on_click=clear_inputs)

    




voting_hist_choices2 = []
if votingCB0:
    # st.sidebar.write(f'you picked 0')
    voting_hist_choices2.append("") #NEED TO FIGURE OUT NAN values or remove them from df
if votingCB1:
    voting_hist_choices2.append("+")
if votingCB2:
    voting_hist_choices2.append("++")
if votingCB3:
    voting_hist_choices2.append("+++")
if votingCB4:
    voting_hist_choices2.append("++++")



# df = pd.read_csv("C:\\Users\\patri\\Documents\\Contacts\\VoteRefDataWithPrecinct2.csv")

# dynamic_filters = DynamicFilters(df, filters=['StreetText', 'Registration Status', 'Voting History', 'District'])

# dfdisplay = df.loc[(df['District']==district_choice) & (df['StreetText']==street_choice) & (df['Registration Status']==reg_status_choice)]
# th = df[df['Region'].str.contains('th$')]

if district_choice == 'All':
    dfdisplay = dfj
elif district_choice == 'City':    
    dfdisplay = dfj.loc[(dfj['District']=="D1") | (dfj['District']=="D2")]
else:
    dfdisplay = dfj[dfj['District']==district_choice]

if street_choice == 'All Streets':
    dfdisplay = dfdisplay[dfdisplay["StreetText"].isin(streets)]
else:
    dfdisplay = dfdisplay[dfdisplay["StreetText"].isin([street_choice])]

if reg_status_choice == 'Everyone':
    dfdisplay = dfdisplay[dfdisplay["Registration Status"].isin(regStatus)]
else:
    dfdisplay = dfdisplay[dfdisplay["Registration Status"].isin([reg_status_choice])]



# dfdisplay = dfdisplay[dfdisplay["Voting History"].isin(voting_hist_choices)]
dfdisplay = dfdisplay[dfdisplay["Vote History"].isin(voting_hist_choices2)]
dfdisplay = dfdisplay[dfdisplay["Name"].str.contains(name_search.upper())]



#df1 = df[['a', 'b']]

dffriends = dfdisplay.loc[dfdisplay['InContactList']==1]
# dffriends = dffriends[['Full Name', 'Address_CL', 'Phone', 'e-mail', 'Age', 'Signed Petition', 'Comments', 'Source Comments', 'Church', 'index' ]]
dffriends.drop_duplicates(subset=['gsIndex'], keep='first', inplace=True)

st.subheader(f"Friends of the Cause ({dffriends.shape[0]})")
st.caption('Goto master spreadsheet to change with this [link](%s)' % url)

newdf = st.data_editor(
    dffriends,
    hide_index=True,
    column_order = ['Full Name', 'Address_CL', 'Phone', 'e-mail', 'Age', 'Signed Petition', 'Comments', 'Source Comments', 'Church'],
    column_config={
        "Full Name": "Name",
        "Address_CL": "Address"
    },
    use_container_width = True,
    key='dataEditor'
)
if st.button("Save to Google Sheets"):
    changes = st.session_state['dataEditor']['edited_rows']
    dffupdated = dff.copy() 
    for index, item in changes.items(): #iterates over all the rows that have changed
        gsIndex = int(newdf.iloc[index]['gsIndex'])
        for key, field in item.items(): #iterates over all the fields in a row that have changes.
            # st.write(f'for gsindex: {gsIndex} we will use{key} -> {field}')
            dffupdated.loc[gsIndex, key] = field
    # st.dataframe(dffupdated)
    dffupdated = dffupdated.drop('gsIndex', axis=1)
    # print(dffupdated.head())
    conn.update(worksheet="Master Contact List2", data=dffupdated)

st.subheader(f"All Filtered Registered Voters ({dfdisplay.shape[0]})")
st.caption("Data is from 2022 some addresses may be old.")
dfdisplay = dfdisplay[['Full Name', 'Address', 'Vote History', 'District', 'Age', 'Count']]
# st.dataframe(dfdisplay)

st.dataframe(
    dfdisplay.sort_values('Address'),
    hide_index=True,
    column_config={
        "Full Name": "Name"
    },
    use_container_width = True
)

st.caption("Voting History Represents how many times the person has voted in the past 4 years.")
st.caption("Nothing is done to correct errors for people with multiple names, so a count of the people with the same name is provided.")

if st.button("Export PDF"):
    pdf = SimpleDocTemplate("dataframe.pdf", pagesize=letter)
    table_data = []
    for i, row in dfdisplay.iterrows():
        table_data.append(list(row))
    table = Table(table_data)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    table.setStyle(table_style)
    pdf_table = []
    pdf_table.append(table)

    pdf.build(pdf_table)
    st.write('Click here to download file dataframe.pdf')

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(dfdisplay)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
)

# st.markdown(dfdisplay.style.hide(axis='index').to_html(), unsafe_allow_html=True)



# dynamic_filters = DynamicFilters(df, filters=['StreetText', 'Registration Status', 'Voting History', 'District'])
# st.write(dynamic_filters.filters)
# with st.sidebar:
#     dynamic_filters.display_filters()
# dynamic_filters.display_df()




# edited_df = st.data_editor(dff)

# st.button("Save to Google Sheet", on_click = savetogoogle)














# print(dfj.columns)

#THE BELOW DID NOT WORK BUT i WANTED TO SAVE THE WORK WHERE I WAS TRYING VERY HARD TO COMPARE TWO DATASESTS.
# def savetogoogle(): 
#     #dff is the 2099x13 original datframe from google sheet, need to update it with newdf.
#     dfupdates = newdf[['gsIndex', 'Last Name', 'First Name', 'Phone', 'e-mail', 'Alt e-mail', 'Address', 'Comments', 'Source Comments', 'Full Name', 'Signed Petition', 'GACC Member', 'Church']]
#     dfupdates.sort_values('gsIndex', inplace=True)
#     # print(dfupdates.tail())
#     dfupdates.dropna(subset=['gsIndex'],inplace=True)
#     dfupdates = dfupdates.astype({'gsIndex':'int'})
#     dfupdates.set_index('gsIndex', inplace=True)
    
#     print(f"DFUPDATES, {dfupdates.shape}-------------------")
#     print(dfupdates.head(3))

#     # #Code to check and print duplicated indexed rows
#     # duplicated_indexes = dfupdates.index.duplicated(keep=False)
#     # duplicated_rows = dfupdates[duplicated_indexes]
#     # print(duplicated_rows)

    
#     dff.set_index('gsIndex', inplace=True)
#     print(f"DFF, {dff.shape}-------------------")
#     print(dff.head(3))
    
#     dff.update(dfupdates)                #THIS UPDATES IT!
#     # dff = dff.drop('gsIndex', axis=1)
#     # print('DFF')
#     # print(dff.head(3))
#     # print(dff.shape)
#     # dfu = dff.drop('gsIndex', axis=1)
#     # print('DFU')
#     # print(dfu.shape)
#     # print(dfu.head())
#     # dfu = merge_dataframe_for_export(dff, newdf)

#     # conn.update(worksheet="Master Contact List2", data=dff)
    
    
#     # print(dfu.shape)
#     # print(dfu)

