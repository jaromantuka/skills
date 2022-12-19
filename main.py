import streamlit as st
import pandas as pd
import numpy as np 
from collections import Counter
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go 

header = st.container()
data_and_selection = st.container()
graphs = st.container()

#change with css i have no idea how 


#caching, not to do it many times 
@st.cache
def get_data(filename):
    data = pd.read_csv(filename)

    return data 

#header in Ukr.
with header: 
    st.title('Найпопулярніші навички в ІТ')
    st.markdown('Ми проаналізували дані з профілів **72 тисяч кандидатів** та **90 тисяч вакансій** на Джині. \
        Обирайте категорію нижче, щоб побачити ключові навички, які зназначають кандидати та про які пишуть у вакансіях.  \
         \n -  Вибірка кандидатів — були активними за останні 30 днів.  \
        \n - Вибірка вакансій: створені цього року та хоча б раз опубліковані. Поле навичок не порожнє. ' )

with data_and_selection: 
    st.subheader('Оберіть категорію')
#loading cand data 
    cand = get_data('skills_candidates.csv')
    cand = cand.dropna()
    cand.rename(columns = {'skills_cache':'all_skils'}, inplace=True)

#loading jobs data 
    jobs = get_data('skills_from_jobs.csv')
    jobs = jobs.dropna()
   # jobs['all_skils'] = jobs['primary_keyword'] + ',' + jobs['extra_keywords']
    jobs['all_skils'] = jobs['extra_keywords']
    jobs['all_skils'] = jobs['all_skils'].str.split(",").map(set).str.join("/")
    jobs['all_skils'] = jobs['all_skils'].str.split("/").map(set).str.join("\n")
    #jobs['all_skils'] = jobs['all_skils'].str.strip('\n')

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
        flat_list = [item for sublist in all_skils for item in sublist]
        myDict = Counter(flat_list)

        skillshare = pd.DataFrame.from_dict(myDict, orient='index')
        skillshare['skill'] = skillshare.index
        skillshare.rename(columns = {0:'count'}, inplace=True)
        skillshare = skillshare[['skill', 'count']]
        skillshare = skillshare.reset_index(drop=True)
        skillshare = skillshare.sort_values(by='count', ascending=False)
        
        return skillshare
#колонки з графіками 
with graphs: 
    cand_col, jobs_col = st.columns(2)

    cand_col.subheader('Найпопулярніші навички серед розробників')

    if keyword == '':
        num_cand = cand.shape[0]
    else:
        num_cand = (cand[cand['primary_keyword'] == keyword]).shape[0]

    cand_col.markdown('Проаналізовано кандидатів: {}'.format(num_cand))
    
    
    cand_skills = one_list(cand, keyword).head(10)
    
    #cand_col.write(cand_skills)
    #cand_col.bar_chart(cand_skills)

    fig_cand = px.bar(cand_skills, x="count", y="skill", orientation='h')
    cand_col.write(fig_cand)
#друга колока

    jobs_col.subheader('Найпопулярніші навички у вакансіях')
    if keyword == '':
        num_jobs = jobs.shape[0]
    else:
        num_jobs = jobs[jobs['primary_keyword'] == keyword].shape[0]


    jobs_col.markdown('Проаналізовано вакансій: {}'.format(num_jobs))
    
    job_skills = one_list(jobs, keyword).head(10)
    
    #jobs_col.write(job_skills)
   # jobs_col.bar_chart(job_skills) 

    fig_jobs = px.bar(job_skills, x="count", y="skill", orientation='h')

    jobs_col.write(fig_jobs)
