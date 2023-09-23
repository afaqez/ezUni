import re
import tabula-py as tb
import pandas as pd
import streamlit as st

st.set_page_config(page_title = 'ezUni - Timetable in seconds', page_icon='stopwatch') # setting up the basic webPage settings
st.markdown(
    """
    <div style="background-color:#808080;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">Only for CS Students</h1>
    </div>
    """,
    unsafe_allow_html=True
)

def error_handling(input_string, section_input):

    course_codes = [code.strip() for code in input_string.split(",")]  # Split the input string by commas
    
    for course_code in course_codes:
        if not re.match(r"[A-Z]{2,4}\d{4}", course_code):
            return f"The course code '{course_code}' is not in the correct form!"

    if not re.match(r"[S][1-4]", section_input):
        return f"There is no \"{section_input}\" in the CS department! Enter the correct section"
    
    
    return None  # no errors found

def register_courses(df, df_timetable, section, courses, days, time_slots):

    for course in courses:
        for day in days:
            for time in time_slots:  
                if df[df['Day'] == day][time].str.strip().eq(course + section).any():
                    if pd.isna(df_timetable.at[day, time]):
                        df_timetable.at[day, time] = course + section # register course
                    else:
                        st.error(f"Clash of {course + section} on {day} at {time}")

def get_credit_hours(courses, credit_hours):

    for course in courses:
        credit_hour = int(course[-1])  # to get the last character of the course code
        if credit_hour == 1: # to convert lab's classes to 3
            credit_hour = 3      
        credit_hours[course] = credit_hour  

def main():

    try:
        # tb.convert_into("timetable.pdf", "timetable.csv", output_format="csv", pages='all')
        df = pd.read_excel('timetable.xlsx') 
        monday_schedule = df[df['Day'] == 'Monday']
        tuesday_schedule = df[df['Day'] == 'Tuesday']
        wednesday_schedule = df[df['Day'] == 'Wednesday']
        thursday_schedule = df[df['Day'] == 'Thursday']
        friday_schedule = df[df['Day'] == 'Friday']

        column_names = df.columns[1:]
        time_slots = column_names.to_list() # getting the column names in order to iterate through them  
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        st.title("ezUni - Timetable Gen")


        input_string = st.text_input("Enter your courses(separated with comma): ").upper().strip()      
        section_input = st.text_input("Enter your section: ").upper().strip() # this will have the section in parenthesis
        error_message = error_handling(input_string, section_input)
        
        if error_message and input_string != "" and section_input != "":
            st.error(error_message)

        elif st.button("Generate Timetable"): # actual working of code will start
            section = ' ('  + section_input + ')'
            courses = [courses.strip() for courses in input_string.split(",")]      
            df_timetable = pd.DataFrame(columns=time_slots, index=days)
            register_courses(df, df_timetable, section, courses, days, time_slots)
                                
            df_timetable = df_timetable.fillna('') # this will remove the annyoing "<NA>"
            st.table(df_timetable)
        
    except Exception as e:
        print("Error: {}".format(e))


main()
