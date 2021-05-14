# A2ZhFakeFactorScripts
Scripts for performing Maximum likelihood fit using Higgs Combine tool and obtain fake rate factors for leptons from data 

These are a few scripts to prepare datacards, perform maximum likelihood fit, and extract fake factor in data for leptons as function of pt/eta. The fits are performed to mT distributions in bins of pt/eta. 
The scripts/macros are self explanatory. The instructions/command to run the scripts are provided in them. 

To run the tool, we need to setup Higgs combine tool and (may be also CombineHarvester, though there is not much dependence on it except plotting tool).

Use these instructions to setup Higgs   combine tool


export SCRAM_ARCH=slc6_amd64_gcc530
scram project CMSSW CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
# IMPORTANT: Checkout the recommended tag on the link above
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scram b


#IMPORTANT: Checkout the recommended tag on http://cms-analysis.github.io/CombineHarvester/index.html and https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/

# then check out this script as
git clone 

#use makeFakeRateDataCard.C to prepare datacards
#use makeFakeRatePlots.py to perform maximum likelihood fits and make fake factor vs pt plots in bins of eta, you can save the fake factors to root file and use later in analysis. 
#use makePostFitPlots.py to make prefit and postfit plots of mt distributions in different pT and eta bins, and for pass and fail regions. Useful to check the distributions and know about the fit quality.
