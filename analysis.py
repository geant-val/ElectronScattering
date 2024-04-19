import numpy as np
import ROOT as root
import os

def GetCharacteristicAngle(func):
	x = np.linspace(0., 10.0, 200)
	y = np.zeros(200)
	for i in range(200):
		y[i] = func.Eval(x[i])

	y /= y.max()
	iBin = -1
	invE = 1./np.e
	for i in range(200):
		if y[i] <= invE:
			iBin = i
			break

	return x[iBin]

def GetGraph(fileNamePrefix, marker, color, isExperimental, xmax):
	f = 1e6
	graph = []
	if isExperimental:
		Angle, Fluence = GetData(fileNamePrefix, isExperimental)
		n = Angle.shape[0]
		Fluence *= f
		graph = root.TGraph(n, Angle, Fluence)
	else:	
		Angle, Fluence = GetData(fileNamePrefix + '.ascii', isExperimental)

		n = Angle.shape[0]

		Fluence *= f

		graph = root.TGraph(n, Angle, Fluence)

	graph.SetMarkerStyle(marker)
	graph.SetMarkerColor(color)
	graph.SetLineWidth(1)
	graph.SetLineColor(color)

	gauss = root.TF1('gauss','[0]*TMath::Exp( -x*x/([1]*[1]) )',0.0, xmax)
        gauss.SetParameter(0, f*10e-6) 
        gauss.SetParameter(1, 5.0)

        graph.Fit('gauss','Q','',0.0, xmax)

	charAngle = GetCharacteristicAngle(gauss)
	print '%40s %1.5f' % (fileNamePrefix, charAngle) 

	return (graph, charAngle) 

def GetData(fileName, isExperimental):
	iFile = open(fileName, 'r')
	if not isExperimental:
		for i in range(4):
			iFile.readline()
	else:
		iFile.readline()

	angle = [] 
	Fluence = [] 
	FluenceError = [] 

	for line in iFile:
		line = line.split()
		if 0 == len(line):
			break

		if not isExperimental:
			r = float(line[1])
			Fluence.append(float(line[3]))
			FluenceError.append(0.0) 
		else:
			r = float(line[0])
			Fluence.append(float(line[1]))
			FluenceError.append(0.0)
	
		angle.append(np.degrees(np.arctan(r/1182.0)))

	return (np.array(angle), np.array(Fluence))


def GetRatioAndError(expData, mcData):
	expValue = expData[0]
	expError = expData[1]
	mntValue = mcData
	ratio = 100.0 * (-expValue + mcData)/expValue
	error = 100.0 * expError/expValue
	return (ratio, error)
	

def SaveToTxt(fileName, graphs, option):
	x = root.Double(0.0)
	y = root.Double(0.0)

	oFile = open(fileName, option)
	nGraphs = len(graphs)
	oFile.write('# ')
	for j in range(nGraphs):
		oFile.write(' %s ' % graphs[j].GetName())
	oFile.write('\n') 

	nValues = graphs[0].GetN()

	for i in range(nValues):
		for j in range(nGraphs):
			graphs[j].GetPoint(i, x, y)
			oFile.write('%1.5f %1.5e  ' % (x, y))
		oFile.write('\n')
	oFile.write('\n\n')
	oFile.close() 

Exp_13MeV = {'Be': [8.182,0.01*8.182], 'C': [7.860,0.01*7.860], 'Al': [5.252,0.01*5.252], 'Ti': [4.250,0.01*4.250], 'Au': [4.855,0.01*4.855]}
materials = ['Be1', 'Ti4', 'Au1', 'C1', 'Al2']
#resultsG4103p02
xmax = 8.0

multiGraphs = []
dif_Angle = root.TMultiGraph()
dif_Angle_GS = root.TGraphErrors(len(materials))
dif_Angle_GS.SetMarkerStyle(24)
dif_Angle_GS.SetMarkerSize(2)
dif_Angle_PN = root.TGraphErrors(len(materials))
dif_Angle_PN.SetMarkerStyle(25)
dif_Angle_PN.SetMarkerSize(2)
dif_Angle_EGS = root.TGraphErrors(len(materials))
dif_Angle_EGS.SetMarkerStyle(5)
dif_Angle_EGS.SetMarkerSize(2)

i = 0
for mat in materials:
	aMG = root.TMultiGraph()
	aMG.SetTitle(mat[:-1])
	egs, aegs = GetGraph('EGS_13MeV/'+mat+'.13MeV.ascii', marker=24, color=2, isExperimental=True, xmax=xmax)
	aMG.Add(egs, 'l')

	gsn, agsn = GetGraph('results/'+mat[:-1]+'_G4GoudsmitSaunderson', marker=24, color=1, isExperimental=False, xmax=xmax)
	aMG.Add(gsn, 'l')

	pen, apen = GetGraph('results/'+mat[:-1]+'_G4Penelope', marker=24, color=4, isExperimental=False, xmax=xmax)
	aMG.Add(pen, 'l')

	multiGraphs.append(aMG)

	ratio, error = GetRatioAndError(Exp_13MeV[mat[:-1]], aegs)
	dif_Angle_EGS.SetPoint(i, i+1, ratio)
	dif_Angle_EGS.SetPointError(i, 0.0, error)

	ratio, error = GetRatioAndError(Exp_13MeV[mat[:-1]], agsn)
	dif_Angle_GS.SetPoint(i, i+1, ratio)
	dif_Angle_GS.SetPointError(i, 0.0, error)

	ratio, error = GetRatioAndError(Exp_13MeV[mat[:-1]], apen)
	dif_Angle_PN.SetPoint(i, i+1, ratio)
	dif_Angle_PN.SetPointError(i, 0.0, error)

	i += 1

dif_Angle.Add(dif_Angle_GS, 'p')
dif_Angle.Add(dif_Angle_PN, 'p')
dif_Angle.Add(dif_Angle_EGS, 'p')


c1 = root.TCanvas('c1', '', 1550, 1000)
c1.Divide(3,2)
i = 1
for graph in multiGraphs: 
	c1.cd(i)
	graph.Draw('AP')
	graph.GetXaxis().SetTitle('Angle (deg)')
	graph.GetYaxis().SetTitle('')
	i += 1

c1.cd(6)
line = root.TGraph(200)
x = np.linspace(1,5,200)
for i in range(200):
	line.SetPoint(i, x[i], 0.0)
line.SetLineStyle(2)

dif_Angle.Add(line, 'l')
dif_Angle.Draw('AP')

axis = dif_Angle.GetHistogram().GetXaxis()
x1 = axis.GetBinLowEdge(1)
x2 = axis.GetBinUpEdge(axis.GetNbins())
dif_Angle.GetHistogram().GetXaxis().Set(len(Exp_13MeV), x1, x2)
n=1
for key in materials: 
	dif_Angle.GetHistogram().GetXaxis().SetBinLabel(n, key)
	n+=1
dif_Angle.GetHistogram().GetXaxis().SetLabelSize(0.06)
dif_Angle.Draw('AP')
dif_Angle.GetYaxis().SetTitle('(MC-meas)/meas (%)')

leg = root.TLegend(0.1,0.7,0.48,0.9)
leg.SetFillColor(0)
leg.AddEntry(dif_Angle_GS, 'GoudsmitSanderson', 'p')
leg.AddEntry(dif_Angle_PN, 'Penelope', 'p')
leg.AddEntry(dif_Angle_EGS, 'EGS', 'p')
leg.Draw()

c1.Update()
c1.SaveAs(os.path.expandvars('~') + '/Dropbox/foo.eps')

raw_input()
