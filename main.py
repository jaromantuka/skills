import streamlit as st
import pandas as pd
import numpy as np 
import re
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

@st.cache_data
def get_data(filename):
    data = pd.read_csv(filename).fillna('')

    return data 

#header in Ukr.
with header: 

    st.title('Найпопулярніші навички в ІТ')
    st.markdown('Ми проаналізували дані з профілів **176 тисяч кандидатів**, які оновлювали профіль на Джині з початку 2024, та **понад 90 тисяч** опублікованих цього року вакансій.\
        Обирайте категорію нижче, щоб побачити ключові навички, які кандидати вказують у профілях, а рекрутери вимагають у вакансіях.  \
        \n Підписуйтесь на [телеграм канал  Djinni.co](https://t.me/djinni_official)' )
#candidates who activated profile this year, jobs published this year. підкатегорій немає 
with data_and_selection: 
    st.subheader('Оберіть категорію')
#loading data 
    cand = get_data('candidate_activated_skills.csv')
    jobs = get_data('jobs_with_label_published_2024.csv')
    jobs.rename(columns={'extra_keywords': 'skills_cache'}, inplace=True)
  
 #the dropdown. value = '' (defealt)
    options = cand['label'].unique()
    options = np.insert(options,0,'')
    options = np.sort(options)
    keyword = st.selectbox('Порожній вибір показує всі категорії', options = options, index =0) 


# the function takes data and category and returns a list of skills in category in order of popularity 
    exceptions = {"AI/ML", "CI/CD"}
    def one_list(data, keyword=''):
        a = data.copy()
        if keyword: 
            a = data[data['label']==keyword]
            a = a.copy()
        # Process the 'all_skills' column
        a['all_skills'] = a.apply(lambda row: 
                            [sub_skill.strip()
                                for skill in set(re.split(r'[\n,]', row['skills_cache']))
                                for sub_skill in (skill.split('/') if skill not in exceptions else [skill])],
                            axis=1)

        b = a['all_skills'].tolist()
        flat_listt = [item for sublist in b for item in sublist]
        flat_listt = [item for item in flat_listt if not (isinstance(item, float) and math.isnan(item))]
        flat_list =[]
        for skill in flat_listt: 
            skill = skill.strip()
            flat_list.append(skill)
        myDict = Counter(flat_list)

        skillshare = pd.DataFrame.from_dict(myDict, orient='index')
        skillshare['skill'] = skillshare.index
        skillshare.rename(columns = {0:'count'}, inplace=True)
        skillshare = skillshare[['skill', 'count']].sort_values(by='count', ascending=False).reset_index(drop=True)
        skillshare['share'] = skillshare['count']/len(a)
        return skillshare
#two columns with graphs 
with graphs: 
    cand_col, jobs_col = st.columns(2)

    cand_col.subheader('Найпопулярніші навички серед кандидатів')

    if keyword == '':
        num_cand = cand.shape[0]
    else:
        num_cand = (cand[cand['label'] == keyword]).shape[0]

    cand_col.markdown('Проаналізовано кандидатів: {}'.format(num_cand))
    
    cand_skills = one_list(cand, keyword).head(15)

    fig_cand = px.bar(
        cand_skills, 
        x="count", 
        y="skill", 
        orientation='h',
        height=600,
        category_orders={"skill": cand_skills["skill"].tolist()}) 
    
    fig_cand.update_yaxes(tickfont=dict(size=14, color='black'))  # Customize size and color


    cand_col.write(fig_cand)

#the second column

    jobs_col.subheader('Найпопулярніші навички у вакансіях')
    if keyword == '':
        num_jobs = jobs.shape[0]
        skil_jobs = jobs[jobs['skills_cache']!=''].shape[0]
    else:
        num_jobs = jobs[jobs['label'] == keyword].shape[0]
        skil_jobs = jobs[(jobs['label'] == keyword)&(jobs['skills_cache']!='')].shape[0]


    jobs_col.markdown('Проаналізовано вакансій: {}. Вакансій з зазначеними навичками: {}'.format(num_jobs, skil_jobs))

    
    job_skills = one_list(jobs, keyword)
    job_skills = job_skills[job_skills['skill']!=''].head(15)

    fig_jobs = px.bar(
        job_skills, 
        x="count", 
        y="skill", 
        orientation='h',
        height=600,
        category_orders={"skill": job_skills["skill"].tolist()}) 

    fig_jobs.update_yaxes(tickfont=dict(size=14, color='black'))  # Customize size and color

    jobs_col.write(fig_jobs)
