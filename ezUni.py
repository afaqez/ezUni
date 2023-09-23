import re
import tabula as tb
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
    return None  # No errors found

def find_alternating_sections(section_input, df, df_timetable, courses, days, time_slots, counters, credit_hours, anomaly, result):

    max_sections = 4  
    alternating_sections = []

    section_number = int(section_input[1:]) # number wala part in "section number"

    for i in range(1, max_sections + 1):
        if i != section_number:
            alternating_sections.append(f" (S{i})")

    for section in alternating_sections:
        alt_section = section
        for day in days:
                for time in time_slots:  
                    if df[df['Day'] == day][time].str.strip().eq(anomaly + section).any():
                        if pd.isna(df_timetable.at[day, time]):
                            counters[anomaly] += 1
        if counters[anomaly] == credit_hours[anomaly]:
            anomaly = deadlock_checker(courses, counters, credit_hours, result)
            if anomaly is None: 
                return alt_section
  
def get_credit_hours(courses, credit_hours):

    for course in courses:
        credit_hour = int(course[-1])  # to get the last character of the course code
        if credit_hour == 1: # to convert lab's classes to 3
            credit_hour = 3      
        credit_hours[course] = credit_hour  

def main_algo(df, df_timetable, section, courses, days, time_slots, counters):

    for course in courses:
        for day in days:
            for time in time_slots:  
                if df[df['Day'] == day][time].str.strip().eq(course + section).any():
                    if pd.isna(df_timetable.at[day, time]):
                        df_timetable.at[day, time] = course + section
                        counters[course] += 1

def deadlock_checker(courses, counters, credit_hours, result):
    for course in courses:
        if counters[course] == credit_hours[course]: # counter[CS1133] == credit_hours[CS1133]
            result += 1

        else:
            return course
    
def adjust_course(anomaly, df, df_timetable, alternating_section, days, time_slots, counters):
    for day in days:
            for time in time_slots:  
                if df[df['Day'] == day][time].str.strip().eq(anomaly + alternating_section).any():
                    if pd.isna(df_timetable.at[day, time]):
                        counters[anomaly] += 1

def register_clash_courses(df, df_timetable, df_final_timetable, alternating_section, section,  clash_course, days, time_slots):
       for day in days:
            for time in time_slots:  
                if df[df['Day'] == day][time].str.strip().eq(clash_course + alternating_section).any():
                    if clash_course is not None:
                        df_final_timetable.at[day, time] = clash_course + alternating_section

def register_normal_courses(df, df_timetable, df_final_timetable, section, courses, clash_course, days, time_slots, counters):
    st.write(clash_course)
    for course in courses:
        for day in days:
            for time in time_slots:  
                if course != clash_course:               
                    if df[df['Day'] == day][time].str.strip().eq(course + section).any():
                        if course != clash_course:
                            if pd.isna(df_final_timetable.at[day, time]):
                                df_final_timetable.at[day, time] = course + section
                        

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
        credit_hours = {}
        result = 0
        clash_course = None
        alternating_section = None
        st.title("ezUni - Timetable Gen")


        input_string = st.text_input("Enter your courses(separated with comma): ").upper().strip()      
        section_input = st.text_input("Enter your section: ").upper().strip() # this will have the section in parenthesis
        error_message = error_handling(input_string, section_input)
        
        if error_message and input_string != "" and section_input != "":
            st.error(error_message)
        elif st.button("Generate Timetable"): # actual working of code will start
            section = ' ('  + section_input + ')'
            courses = [courses.strip() for courses in input_string.split(",")]     
            counters = {course: 0 for course in courses} # dictionary of counters to keep count of classes in a week 
            get_credit_hours(courses, credit_hours)
            df_timetable = pd.DataFrame(columns=time_slots, index=days)
            df_final_timetable = pd.DataFrame(columns=time_slots, index=days)
            main_algo(df, df_timetable, section, courses, days, time_slots, counters)
            anomaly = deadlock_checker(courses, counters, credit_hours, result)
            while anomaly is not None:
                clash_course = anomaly
                alternating_section = find_alternating_sections(section_input, df, df_timetable, courses, days, time_slots, counters, credit_hours, anomaly, result)
                            
            if anomaly is None: 
                register_normal_courses(df, df_timetable, df_final_timetable, section, courses, clash_course, days, time_slots, counters)
                register_clash_courses(df, df_timetable, df_final_timetable, alternating_section, section,  clash_course, days, time_slots)


            df_final_timetable = df_final_timetable.fillna('') # this will remove the annyoing "<NA>"
            st.table(df_final_timetable)
            
    except Exception as e:
        print("Error: {}".format(e))


main()


# every course will have a counter 
# i will have to extract the last digit from every course to get the credit hours-> this will determine the number which the above counters must be equal to
# for example: if CS1133 has 3 credit hours then countCS1133 must have a value of 3 after the excecution of main algo or in the future (deadlock checker)
# if the number of credit hours and the counter checks out after the excution of main algo then we will move towards the "registering course function"
# so in conclusion: Get user's info, Extract Credit Hours, Make counters of each course, Run the counters through main algo (deadlock checker)
# if counters == creditHours, move towards register 
# if counters != creditHours, get the couters which are not equal and change their corresponding section (i think i will have to make another whole funciton for it)
# after changing the secitons, the whole checking process will happen again
# registration will now happen unless there is no clash 
