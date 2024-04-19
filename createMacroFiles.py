#             Material Name  : (thickness in g/cm2, density in g/cm3, material exit window)

materials = {'Beryllium':(0.926, 1.85, 'Titanium'),\
             'Graphite': (0.546, 2.18, 'Titanium'),\
             'Aluminum': (0.140, 2.70, 'Titanium'),\
             'Titanium': (0.0728, 4.42, 'Air'),\
             'Copper'  : (0.0430, 8.92, 'Titanium'),\
             'Tantalum': (0.0443, 16.65, 'Titanium'),\
             'Gold'    : (0.0312, 19.30, 'Titanium')}

models = ['emstandard_opt0', 'emstandard_opt4', 'GoudsmitSaunderson', 'penelope', 'livermore']

for model in models:
	for material, value in materials.iteritems():
		name = material + '_' + model + '.mac'
		oFile = open(name, 'w')
		with open('run_option.mac') as iFile:
			for line in iFile:
				if 'theScatteringMaterial' in line:
					line = line.replace('theScatteringMaterial', material)
				if 'theExitWindowMaterial' in line:
					line = line.replace('theExitWindowMaterial', value[2])
				if 'theEmModel' in line:
					line = line.replace('theEmModel', model)
				if 'theThickness' in line:
					thick = '{:.5f}'.format(value[0]/value[1])
					line = line.replace('theThickness',thick)
				oFile.write('%s' % line)
		oFile.close()
	


