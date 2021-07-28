import calendar as cal

# apr = cal.monthcalendar(2021, 6)
# # print(apr)

# for wk in apr:
# 	print(wk)

field = "weed_point"
spp = "Phalaris aquatica"

 # select_date = "2020-10-13"

for m in range(1, 13):
	year = 2021
	weekday, last_day = cal.monthrange(year, m)
	m = str(m).zfill(2)
	date_lower = f"{year}-{m}-01"
	date_upper = f"{year}-{m}-{last_day}"

	exp = f"{field} = '{spp}' And Action_Date >= timestamp '{date_lower} And Action_Date <= timestamp '{date_upper}'"

	

	print(f"month: {m} has last day of {last_day}")
	print(exp)