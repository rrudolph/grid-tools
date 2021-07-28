

data = [
'Foliar Herbicide blah',
'Manual & Herbicide blah',
'Mechanical & Herbicide blah',
'Not a real thing',
'Manual - Transplant'
]

def is_non_herbicide_mode(treatment_mode):
	unacceptable_modes = [
		'Manual - Cut Stump',
		'Manual - Cut Stump & Solarize',
		'Manual - Dig & Flip',
		'Manual - Girdle',
		'Manual - Hand Halo',
		'Manual - Hoe',
		'Manual - Hula Hoe (Oscillating Hoe)',
		'Manual - Mulch',
		'Manual - Pull/Dig',
		'Manual - Pull/Dig & Bag',
		'Manual - Solarize',
		'Manual - Steam',
		'Manual - Transplant',
		'Manual - Trim',
		'Mechanical - Cut Stump',
		'Mechanical - Cut Stump & Grind',
		'Mechanical - Cut Stump & Solarize',
		'Mechanical - Dig & Flip',
		'Mechanical - Pull/Dig',
		'Mechanical - Foam',
		'Mechanical - Girdle',
		'Mechanical - Masticate',
		'Mechanical - Trim',
		'Mechanical - Grub',
		'Mechanical - Mow/Cut',
		'Mechanical - Recontour']

	found_mode = False
	for mode in unacceptable_modes:
		if treatment_mode == mode:
			found_mode = True
			break

	return found_mode


for d in data:
	print(f"Data: {d} Found Mode: {is_non_herbicide_mode(d)}")
