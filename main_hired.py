import streamlit as st
import pandas as pd
import numpy as np 
from collections import Counter
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go 

def wide(): 
    st.set_page_config(layout="wide")
wide()

header = st.container()
data_and_selection = st.container()
graphs = st.container()

#@st.cache
def get_data(filename):
    data = pd.read_csv(filename)

    return data 

#header in Ukr.
with header: 

    st.title('Найпопулярніші навички найнятих кандидатів')
    st.markdown('Ми проаналізували дані з профілів **12 тисяч кандидатів**, найнятих на Джині під час війни. \
        Обирайте категорію нижче, щоб побачити ключові навички, які ці кандидати вказали у своїх профілях.  \
        \n Підписуйтесь на [телеграм канал  Djinni.co](https://t.me/djinni_official)' )

with data_and_selection: 
    st.subheader('Оберіть категорію')
#loading cand data 
    cand = get_data('skills_hired_cand.csv')
    cand = cand.dropna()
    cand.rename(columns = {'skills_cache':'all_skils'}, inplace=True)

 #the dropdown. value = '' (defealt)
    options = cand['primary_keyword'].unique()
    options = np.insert(options,0,'')
    options = np.sort(options)
    keyword = st.selectbox('Порожній вибір показує всі категорії', options = options, index =0) 


# the function takes data and category and returns a list of skills in category in order of popularity 
    def one_list(data, keyword=''):
        a = data
        if keyword: 
            a = data[data['primary_keyword'] == keyword] 
        skils = a['all_skils']
        list = skils.tolist()
        all_skils = []
        for i in range(len(list)):
            a = list[i]
            a = a.split('\n')
            all_skils.append(a)
        flat_listt = [item for sublist in all_skils for item in sublist]
        flat_list =[]
        for skill in flat_listt: 
            skill = skill.strip()
            flat_list.append(skill)
        myDict = Counter(flat_list)

        skillshare = pd.DataFrame.from_dict(myDict, orient='index')
        skillshare['skill'] = skillshare.index
        skillshare.rename(columns = {0:'count'}, inplace=True)
        skillshare = skillshare[['skill', 'count']]
        skillshare = skillshare.reset_index(drop=True)
        skillshare = skillshare.sort_values(by='count', ascending=False)
        
        return skillshare
#two columns with graphs 
with graphs: 
    cand_col, jobs_col = st.columns(2)

    cand_col.subheader('Найпопулярніші навички серед кандидатів')

    if keyword == '':
        num_cand = cand.shape[0]
    else:
        num_cand = (cand[cand['primary_keyword'] == keyword]).shape[0]

    cand_col.markdown('Проаналізовано кандидатів: {}'.format(num_cand))
    
    cand_skills = one_list(cand, keyword).head(10)


    fig_cand = px.bar(cand_skills, x="count", y="skill", orientation='h')
    cand_col.write(fig_cand)

#the second column

    jobs_col.subheader('Найпопулярніші навички у вакансіях')
    if keyword == '':
        num_jobs = jobs.shape[0]
    else:
        num_jobs = jobs[jobs['primary_keyword'] == keyword].shape[0]


    jobs_col.markdown('Проаналізовано вакансій: {}'.format(num_jobs))
    
    job_skills = one_list(jobs, keyword).head(10)

    fig_jobs = px.bar(job_skills, x="count", y="skill", orientation='h')
   

    jobs_col.write(fig_jobs)
