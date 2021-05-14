import sys, time, os
import ROOT, array
from ROOT import TFile, TH1F, TGraph, TCanvas, TLegend, TTree
from ROOT import TMVA, TMath
import CombineHarvester.CombineTools.plotting as plot

from optparse import OptionParser
parser = OptionParser()

#run: python makePostFitPlots.py --lepType "muon" --region "pass" --ptbin "Pt10To20" --etabin "barrel" --prefit
parser.add_option("--lepType", type="string", dest="lepType", help="ele / muon", default='ele')
parser.add_option("--region", type="string", dest="region", help="pass / fail", default='pass')
parser.add_option("--ptbin", type="string", dest="ptbin", help="pT bin", default='Pt10To20')
parser.add_option("--etabin", type="string", dest="etabin", help="eta bin: barrel / endcap", default='barrel')
parser.add_option("--prefit", action="store_true", dest="prefit", help="pre or post fit", default=False)
(options, args) = parser.parse_args()

lepType = options.lepType
region = options.region
ptbin = options.ptbin
etabin = options.etabin
prefit = options.prefit

if not os.path.exists('Fits'):
    os.makedirs('Fits')

datacardfile = 'datacards/datacard_fit_'+lepType+'_'+region+'_'+ptbin+'_'+etabin+'.txt'
#print 'fitting ', datacardfile
#Perform the fit, if not yet done
fitfile = 'Fits/fitDiagnosticsTest.'+lepType+'.'+region+'.'+ptbin+'.'+etabin+'.root'
if not os.path.exists(fitfile):
    run_cmd = 'combine -M FitDiagnostics '+datacardfile+' --saveWithUncertainties --saveNormalizations --saveShapes'
    os.system(run_cmd)
    mv_cmd = 'mv fitDiagnosticsTest.root '+' Fits/fitDiagnosticsTest.'+lepType+'.'+region+'.'+ptbin+'.'+etabin+'.root'
    os.system(mv_cmd)
    mv_cmd = 'mv higgsCombineTest.FitDiagnostics.mH120.root '+' Fits/higgsCombineTest.FitDiagnostics.mH120.'+lepType+'.'+region+'.'+ptbin+'.'+etabin+'.root'
    os.system(mv_cmd)

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

plot.ModTDRStyle()

canvas = ROOT.TCanvas()

shapefile = 'datacards/shapes_'+lepType+'_'+region+'_'+ptbin+'_'+etabin+'.root'
print shapefile
file_shapes = ROOT.TFile.Open(shapefile, "read")
h_data_prefit = file_shapes.Get("data_obs")

h_prompt = h_data_prefit.Clone("h_prompt")
h_prompt.Clear()
h_fake = h_data_prefit.Clone("h_fake")
h_fake.Clear()

first_dir = 'shapes_fit_s'
second_dir = 'bin1'
if prefit:
    first_dir = 'shapes_prefit'

fitfile = 'Fits/fitDiagnosticsTest.'+lepType+'.'+region+'.'+ptbin+'.'+etabin+'.root'
fin = ROOT.TFile(fitfile)

h_prompt_fit = fin.Get(first_dir + '/' + second_dir + '/prompt')
h_fake_fit = fin.Get(first_dir + '/' + second_dir + '/fake')
h_total_fit = fin.Get(first_dir + '/' + second_dir + '/total')
gr_data_fit = fin.Get(first_dir + '/' + second_dir + '/data') 

nbins = h_data_prefit.GetNbinsX()
x = []
y_tot = []
ex = []
ey_tot_low = []
ey_tot_up = []

for b in range(1, nbins+1):
    h_prompt.SetBinContent(b, h_prompt_fit.GetBinContent(b))
    h_fake.SetBinContent(b, h_fake_fit.GetBinContent(b))
    x_value = ROOT.Double()
    y_value = ROOT.Double()
    gr_data_fit.GetPoint(b-1, x_value, y_value) #points start from 0, not 1
    gr_data_fit.SetPoint(b-1, h_data_prefit.GetBinCenter(b), y_value) #points start from 0, not 1
    x.append(h_data_prefit.GetBinCenter(b))
    ex.append(h_data_prefit.GetBinWidth(b)/2)
    y_tot.append(h_total_fit.GetBinContent(b))
    ey_tot_low.append(h_total_fit.GetBinErrorLow(b))
    ey_tot_up.append(h_total_fit.GetBinErrorUp(b))  

h_fake.SetFillColor(ROOT.TColor.GetColor(100, 192, 232))
h_prompt.SetFillColor(ROOT.kRed)

gr_err = ROOT.TGraphAsymmErrors(nbins, array.array('d', x), array.array('d', y_tot), array.array('d', ex), array.array('d', ex), array.array('d', ey_tot_low), array.array('d', ey_tot_up))
gr_err.SetFillColorAlpha(12, 0.3)  # Set grey colour (12) and alpha (0.3)
gr_err.SetMarkerSize(0)

hs = ROOT.THStack("hs", "")
hs.Add(h_prompt)
hs.Add(h_fake)

gr_data_fit.SetMarkerStyle(20)
gr_data_fit.SetMarkerSize(1.0)

gr_data_fit.GetXaxis().SetTitle("m_{T} (GeV)")
gr_data_fit.GetYaxis().SetTitle("N_{events}/bin")
gr_data_fit.SetMaximum(1.2*h_total_fit.GetMaximum())

gr_data_fit.Draw("AP")
hs.Draw("HISTsame")
gr_err.Draw('E2SAME')
gr_data_fit.Draw("psame")
ROOT.gPad.RedrawAxis();
leg = TLegend(0.6, 0.65, 0.9, 0.9)
leg.SetBorderSize(0)
leg.SetFillColor(10)
leg.SetLineColor(0)
leg.SetFillStyle(0)
leg.SetTextSize(0.04)
leg.SetTextFont(42)

leg.AddEntry(gr_data_fit, "data", "lp")
leg.AddEntry(h_fake, "Fake", "f")
leg.AddEntry(h_prompt, "Prompt", "f")
leg.AddEntry(gr_err, 'unc', 'F')
leg.Draw()


if not os.path.exists('plots'):
    os.makedirs('plots')

if prefit:
    canvas.SaveAs("plots/mt_"+lepType+'.'+region+'.'+ptbin+'.'+etabin+"_prefit.png")
else:
    canvas.SaveAs("plots/mt_"+lepType+'.'+region+'.'+ptbin+'.'+etabin+"_postfit.png")

