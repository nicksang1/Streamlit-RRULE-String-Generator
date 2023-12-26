from itertools import product
import streamlit as st
from dateutil.rrule import rrulestr
import datetime


def build_rule(
    freq_type,
    interval,
    repeat_type,
    repeat_weeklyday,
    repeat_monthlydate,
    repeat_monthlyday,
    repeat_yearly_month,
    freq_until,
    freq_count,
):
    dow = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    interval = interval if interval else 1

    repeat_monthlydate = (
        repeat_monthlydate if repeat_monthlydate else [datetime.date.today().day]
    )
    repeat_monthlydate = ",".join(map(str, repeat_monthlydate))

    repeat_yearly_month = (
        repeat_yearly_month if repeat_yearly_month else [datetime.date.today().month]
    )
    repeat_yearly_month = ",".join(map(str, repeat_yearly_month))

    repeat_weeklyday = ",".join(repeat_weeklyday) if repeat_weeklyday else ""

    repeat_monthlyday = (
        ",".join(map(str, repeat_monthlyday)) if repeat_monthlyday else ""
    )
    if repeat_type == "w":
        repeat_monthlyday = ""  # Reset monthly day for weekly frequency
    elif not repeat_monthlyday:
        d = datetime.date.today()
        i = d.weekday()
        week = (d.day - 1) // 7 + 1
        repeat_monthlyday = f"{week}{dow[i].upper()}"

    rrule_str = ""

    if repeat_type == "d":
        rrule_str = f"FREQ=DAILY;INTERVAL={interval}"
    elif repeat_type == "w":
        rrule_str = f"FREQ=WEEKLY;INTERVAL={interval};BYDAY={repeat_weeklyday}"
    elif repeat_type == "mdate":
        rrule_str = f"FREQ=MONTHLY;INTERVAL={interval};BYMONTHDAY={repeat_monthlydate}"
    elif repeat_type == "mday":
        rrule_str = f"FREQ=MONTHLY;INTERVAL={interval};BYDAY={repeat_monthlyday}"
    elif repeat_type == "ydate":
        rrule_str = f"FREQ=YEARLY;INTERVAL={interval};BYMONTH={repeat_yearly_month};BYMONTHDAY={repeat_monthlydate}"
    elif repeat_type == "yday":
        rrule_str = f"FREQ=YEARLY;INTERVAL={interval};BYMONTH={repeat_yearly_month};BYDAY={repeat_monthlyday}"

    if freq_type == "c":
        if freq_count:
            rrule_str += f";COUNT={freq_count}"
    elif freq_type == "u":
        udate = freq_until.split("T")[0]
        rrule_str += f";UNTIL={udate}T000000Z"
        
    return rrule_str


# Streamlit app
st.title("Recurrence Rule Builder")

repeat_type_option = ["d", "w", "mday", "yday"]

# Create a dictionary for alternative text display
repeat_type_display = {"d": "Daily", "w": "Weekly", "mday": "Monthly Day", "yday": "Yearly Day"}

# Use the dictionary to display alternative text in the select box
freq = st.selectbox("Frequency", repeat_type_option, format_func=lambda x: repeat_type_display[x])

# Interval input
interval = st.number_input("Interval", min_value=1, value=1)

# Day of week selection for weekly frequency
repeat_weeklyday = []
if freq == "w":
    repeat_weeklyday = st.multiselect(
        "Select Days of Week", ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    )

# Monthly day selection for monthly frequency
repeat_monthlyday = []
if freq == "mday":
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    occurrences = ["1st", "2nd", "3rd", "4th"]
    combinations = list(product(occurrences, weekdays))
    selected_combinations = st.multiselect("Select Days", combinations, format_func=lambda x: f"{x[0]} {x[1]}")

    # The use of lambda with format func is to change the data form to Readable from refer to to it's getting
    # the index[0] of x and index[1] of x to single text form
    
    # Convert selected combinations to the format you need
    repeat_monthlyday = [f"{occurrence[0]}{day[:2].upper()}" for occurrence, day in selected_combinations]

# Yearly month selection for yearly frequency
repeat_yearly_month = []
if freq == "yday":
    repeat_yearly_month = st.multiselect("Select Months", list(range(1, 13)))

    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    occurrences = ["1st", "2nd", "3rd", "4th"]
    combinations = list(product(occurrences, weekdays))
    selected_combinations = st.multiselect("Select Days", combinations, format_func=lambda x: f"{x[0]} {x[1]}")
    repeat_monthlyday = [f"{occurrence[0]}{day[:2].upper()}" for occurrence, day in selected_combinations]

# End condition selection
freq_type = st.radio("End Condition", ["None", "Until", "Count"])

if freq_type == "Until":
    end_date = st.date_input("End Date", min_value=datetime.datetime.now())
    end_date = end_date.strftime("%Y%m%d")
    freq_type = "u"
else: end_date = None

if freq_type == "Count":
    recurrence_count = st.number_input("Repeat For", min_value=1)
    freq_type = "c"
else: recurrence_count = None

# Build and display the rule
if st.button("Generate Rule"):
    # Call the Python function to build the rule
    rrule_result = build_rule(
        freq_type,
        interval,
        freq,  # Pass freq as freq_type to build_rule
        repeat_weeklyday,
        repeat_monthlyday,
        repeat_monthlyday,  # Pass repeat_monthlyday to build_rule
        repeat_yearly_month,
        end_date,
        recurrence_count,
    )

    # Display the generated rule
    st.text_area("Generated Recurrence Rule", rrule_result)

    # Display the generated rule
    if rrule_result:
        rrule = rrulestr(rrule_result)
        datetime_instances = list(rrule)
        st.write(datetime_instances)
