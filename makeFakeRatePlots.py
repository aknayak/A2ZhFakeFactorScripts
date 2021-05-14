import sys, time, os
import ROOT, array
from ROOT import TFile, TH1F, TGraph, TCanvas, TLegend, TTree
from ROOT import TMVA, TMath

from optparse import OptionParser
parser = OptionParser()

#run: python makeFakeRatePlots.py --lepType "muon" --etabin "barrel"
parser.add_option("--lepType", type="string", dest="lepType", help="ele / muon", default='ele')
parser.add_option("--etabin", type="string", dest="etabin", help="eta bin: barrel / endcap", default='barrel')
(options, args) = parser.parse_args()

lepType = options.lepType
etabin = options.etabin

if lepType=='ele' : 
    pt = [10, 20, 40, 60]
    ptbins = ['Pt10To20', 'Pt20To40', 'Pt40To60']
elif lepType=='muon' : 
    pt = [10, 20, 30, 40, 60]
    ptbins = ['Pt10To20','Pt20To30', 'Pt30To40', 'Pt40To60']

regions = ['pass', 'fail']

if not os.path.exists('Fits'):
    os.makedirs('Fits')

nbins = len(pt)-1
hist_fr_data = TH1F("fr_data_"+lepType+"_"+etabin, "", nbins, array.array('d',pt))
hist_fr_mc = TH1F("fr_mc_"+lepType+"_"+etabin, "", nbins, array.array('d',pt))

for i, p in enumerate(ptbins):
    fakes_data = [0, 0]
    errors_data = [0, 0]
    fakes_mc = [0, 0]
    errors_mc = [0, 0]
    for j, r in enumerate(regions):
        datacardfile = 'datacards/datacard_fit_'+lepType+'_'+r+'_'+p+'_'+etabin+'.txt'
        print 'fitting ', datacardfile
        cmd = 'combine -M FitDiagnostics '+datacardfile+' --saveWithUncertainties --saveNormalizations --saveShapes'
        os.system(cmd)
        fitfile = TFile("fitDiagnosticsTest.root")
        hist_postfit_fake = fitfile.Get("shapes_fit_s/bin1/fake")
        fakes_data[j] = hist_postfit_fake.Integral()
        error = ROOT.Double()
        fakeAndError = hist_postfit_fake.IntegralAndError(1, hist_postfit_fake.GetNbinsX(), error)
        errors_data[j] = error
        print 'error on data ', error
        hist_prefit_fake = fitfile.Get("shapes_prefit/bin1/fake")
        fakes_mc[j] = hist_prefit_fake.Integral()
        error = ROOT.Double()
        fakeAndError = hist_prefit_fake.IntegralAndError(1, hist_prefit_fake.GetNbinsX(), error)
        print 'error on mc ', error
        errors_mc[j] = error
        mv_cmd = 'mv higgsCombineTest.FitDiagnostics.mH120.root '+' Fits/higgsCombineTest.FitDiagnostics.mH120.'+lepType+'.'+r+'.'+p+'.'+etabin+'.root'
        os.system(mv_cmd)
        mv_cmd = 'mv fitDiagnosticsTest.root '+' Fits/fitDiagnosticsTest.'+lepType+'.'+r+'.'+p+'.'+etabin+'.root'
        os.system(mv_cmd)
    ratio_error_data = (fakes_data[0]/fakes_data[1])*TMath.Sqrt(TMath.Power(errors_data[0]/fakes_data[0], 2) + TMath.Power(errors_data[1]/fakes_data[1], 2))
    hist_fr_data.SetBinContent(i+1, fakes_data[0]/fakes_data[1])
    hist_fr_data.SetBinError(i+1, ratio_error_data);
    ratio_error_mc = (fakes_mc[0]/fakes_mc[1])*TMath.Sqrt(TMath.Power(errors_mc[0]/fakes_mc[0], 2) + TMath.Power(errors_mc[1]/fakes_mc[1], 2))
    hist_fr_mc.SetBinContent(i+1, fakes_mc[0]/fakes_mc[1])
    hist_fr_mc.SetBinError(i+1, ratio_error_mc);
    print 'bin ', p, ' fakes data ', fakes_data[0]/fakes_data[1], ' fakes mc ', fakes_mc[0]/fakes_mc[1], '+/-',ratio_error_mc
    print 'data: pass ', fakes_data[0], ' fail ',fakes_data[1]
    print 'mc: pass ', fakes_mc[0], ' fail ',fakes_mc[1]

c1 = TCanvas()
c1.SetFillColor(10)
c1.SetBorderSize(2)
c1.SetLeftMargin(0.12)
c1.SetBottomMargin(0.12)
c1.SetRightMargin(0.05)
c1.SetLogy()

histogram_base = TH1F("histogram_base", "", 20, 0., 60.)
histogram_base.SetTitle("")
histogram_base.SetStats(False)
histogram_base.SetMinimum(0.01)
histogram_base.SetMaximum(1.0)
histogram_base.GetYaxis().SetTitle("Fake Factor")
histogram_base.GetXaxis().SetTitle("p_{T} (GeV)")
histogram_base.Draw()

hist_fr_data.SetMarkerStyle(20)
hist_fr_data.SetMarkerSize(1.0)
hist_fr_data.SetLineColor(2)
hist_fr_data.SetMarkerColor(2)
hist_fr_mc.SetMarkerStyle(24)
hist_fr_mc.SetMarkerSize(1.0)
hist_fr_mc.SetLineColor(4)

leg = TLegend(0.2, 0.65, 0.5, 0.9)
leg.SetBorderSize(0)
leg.SetFillColor(10)
leg.SetLineColor(0)
leg.SetFillStyle(0)
leg.SetTextSize(0.04)
leg.SetTextFont(42)

leg.AddEntry(hist_fr_data, "data", "lp")
leg.AddEntry(hist_fr_mc, "mc", "lp")

hist_fr_data.Draw("P E same")
hist_fr_mc.Draw("P E same")
leg.Draw()

if not os.path.exists('plots'):
    os.makedirs('plots')

c1.SaveAs("plots/fakefactor_"+lepType+"_"+etabin+".png")
outfile = TFile("plots/fakefactor_"+lepType+"_"+etabin+".root", "RECREATE")
hist_fr_data.Write()
hist_fr_mc.Write()
outfile.Close()

